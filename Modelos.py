# Importar librerías
from gurobipy import *
import math
import os
import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np

tipoNodos = [1, 2, 3]  # L:1, M:2, H:3
costos = {1: 1, 2: 3, 3: 7}
confiabilidad = {1: 0.5, 2: 0.6, 3: 0.7}

######### Funciones #########

# Mostrar modelo


def mostrarModelo(filename, model):
    print(filename)
    if os.path.exists(filename):
        os.remove(filename)
    model.write(filename)
    model.display()

# Mostrar resultados


def mostrarResultados(costo, variablesDecision):
    print('===================================')
    print('Función objetivo: ', str(round(costo, 4)))
    for v in variablesDecision.keys():
        print(v, variablesDecision[v])

# Mostrar resultados en tabla


def mostrarResultadosTabla(cantidadNodos, confiabilidadObjetivo, caso, costo, variablesDecision):
    # Cantidad de nodos: Integer, cantidad de nodos del sistema
    # Confiabilidad Objetivo: Float, confiabilidad objetivo del sistema
    # Caso: Integer, caso de estudio, 0 es serie, 1 es paralelo
    # Costo: Float, Costo Total del sistema
    # Variables de decisión: List, Lista con las variables de decisión obtenidas de optimizar el modelo

    if costo is None:
        print("====================================================")
        print("Cantidad de Nodos: ", cantidadNodos)
        print("Confiabilidad Objetivo: ", confiabilidadObjetivo)
        print("Caso: ", "Serie" if caso == 0 else "Paralelo")
        print("====================================================")
        print("No se encontró solución")
    else:
        print("====================================================")
        print("Cantidad de Nodos: ", cantidadNodos)
        print("Confiabilidad Objetivo: ", confiabilidadObjetivo)
        print("Caso: ", "Serie" if caso == 0 else "Paralelo")
        print("====================================================")
        print("Resultado de la Optimización:")
        print("====================================================")
        print("Costo Total: ", costo)
        print("Nodos activos: \n")

        xVars = dict()
        for var in variablesDecision.keys():
            if var.startswith("x"):
                xVars[var] = variablesDecision[var]

        activeNodes = []
        for i in range(cantidadNodos):
            valores = []
            pattern = re.compile(r'^x\[' + str(i) + r',')
            for var in xVars.keys():
                if pattern.match(var):
                    valores.append(int(xVars[var]))
            activeNodes.append(valores)

        columns_titles = ["Low Cost", "Mid Cost", "High Cost"]
        row_index = [i+1 for i in range(cantidadNodos)]

        tabla = pd.DataFrame(
            activeNodes, columns=columns_titles, index=row_index)
        print(tabla)
        print("====================================================")

######## Modelos ########

# Modelo Base


def base_model(cantidadNodos):
    # Variables
    nodos = list(range(cantidadNodos))
    arcos = [(i, j) for i in nodos for j in tipoNodos]

    # Crear modelo
    model = Model(f"Modelo_Base_{cantidadNodos}_Nodos")
    model.setParam('OutputFlag', 0)  # No mostrar salida por defecto de Gurobi

    # Variables de decisión
    # Variable booleana para determinar si un nodo está activo
    x = model.addVars(arcos, vtype=GRB.BINARY, name='x')

    # Variable objetivo
    # Costo de los nodos desplegados
    model.setObjective(quicksum(costos[j]*x[i, j]
                       for j in tipoNodos for i in nodos), GRB.MINIMIZE)

    # Restricciones generales
    # 1. Cada nodo solo puede ser de un tipo
    model.addConstrs(
        (quicksum(x[i, j] for j in tipoNodos) == 1 for i in nodos), name='unicidad')

    return model

# Modelo para nodos en serie


def serie_model(model_base, cantidadNodos, confiabilidadObjetivo):
    model_base.update()
    model = model_base.copy()

    nodos = list(range(cantidadNodos))
    x = model.getVars()
    x = {tuple(map(int, var.varName.split('[')[1].split(']')[0].split(','))): var
         for var in model.getVars() if "x" in var.varName}

    # Variables nuevas
    # Sumatoria interna de la confiabilidad en serie
    z = model.addVars(nodos, vtype=GRB.CONTINUOUS, lb=0.1, name='z')
    log_z = model.addVars(nodos, vtype=GRB.CONTINUOUS,
                          name='log_z')  # Logaritmo natural de z

    # Restricciones
    # 2.1. Relación entre z y x
    for u in nodos:
        model.addConstr(z[u] == sum((1/confiabilidad[i]) * x[u, i]
                        for i in tipoNodos), name=f"z_u_{u}")

    # 2.2. Logaritmo de z_u
    for u in nodos:
        model.addGenConstrLog(z[u], log_z[u], name=f"log_z_{u}")

    # 2.3. Restricción de la productoria
    model.addConstr(-quicksum(log_z[u] for u in nodos) >=
                    math.log(confiabilidadObjetivo), name="log_prod")

    # Optimizar
    model.optimize()

    if model.status == GRB.OPTIMAL:
        costo = model.objVal

        variablesDecision = dict()
        for var in model.getVars():
            variablesDecision[var.varName] = var.x

        return costo, variablesDecision
    else:
        return None, None

# Modelo para nodos en paralelo


def paralelo_model(model_base, cantidadNodos, confiabilidadObjetivo):
    model_base.update()
    model = model_base.copy()

    nodos = list(range(cantidadNodos))
    x = model.getVars()
    x = {tuple(map(int, var.varName.split('[')[1].split(']')[0].split(','))): var
         for var in model.getVars() if "x" in var.varName}

    # Variables nuevas
    # Sumatoria interna de la confiabilidad en paralelo
    z = model.addVars(nodos, vtype=GRB.CONTINUOUS, lb=0.1, name='z')
    log_z = model.addVars(nodos, vtype=GRB.CONTINUOUS,
                          name='log_z')  # Logaritmo natural de z

    # Restricciones
    # 2.1. Relación entre z y x
    for u in nodos:
        model.addConstr(z[u] == sum((1/(1-confiabilidad[i])) * x[u, i]
                        for i in tipoNodos), name=f"z_u_{u}")

    # 2.2. Logaritmo de z_u
    for u in nodos:
        model.addGenConstrLog(z[u], log_z[u], name=f"log_z_{u}")

    # 2.3. Restricción de la productoria
    model.addConstr(-quicksum(log_z[u] for u in nodos) <=
                    math.log(1-confiabilidadObjetivo), name="log_prod")

    # Optimizar
    model.optimize()

    if model.status == GRB.OPTIMAL:
        costo = model.objVal

        variablesDecision = dict()
        for var in model.getVars():
            variablesDecision[var.varName] = var.x

        return costo, variablesDecision
    else:
        return None, None

###### Funciones para gráficos ######

# Mostrar resultados


def mostrarResultadosTabla2(costos, tipoNodos):
    """
    Muestra los resultados en una tabla basada de costo y dde nodos,
    """
    data = pd.DataFrame(costos, columns=['Nodos', 'Confiabilidad', 'Costo'])
    tipo_nodos_df = pd.DataFrame(tipoNodos)
    resultado_df = pd.concat([data, tipo_nodos_df], axis=1)

    print("\nResultados en formato tabular:\n")
    print(resultado_df.to_markdown(tablefmt="double_grid", index=False))


def grafico_costo_vs_cantidad_nodos_general(costos):
    """
    Genera un gráfico de Costo vs Cantidad de Nodos para una confiabilidad.

    :param costos: Lista de tuplas (nodos, confiabilidad, costo) con los resultados.
    """
    data = pd.DataFrame(costos, columns=['Nodos', 'Confiabilidad', 'Costo'])
    confiabilidades_unicas = sorted(data['Confiabilidad'].unique())
    colores = plt.cm.viridis(np.linspace(0, 1, len(confiabilidades_unicas)))

    plt.figure(figsize=(10, 6))
    for conf, color in zip(confiabilidades_unicas, colores):
        subset = data[data['Confiabilidad'] == conf]
        plt.plot(subset['Nodos'], subset['Costo'], marker='o',
                 linestyle='-', color=color, label=f'Confiabilidad: {conf}')

    plt.title(f"Costo vs Cantidad de Nodos para Diferentes Confiabilidades")
    plt.xlabel("Cantidad de Nodos")
    plt.ylabel("Costo Total")
    plt.grid(True)
    plt.legend()
    plt.show()


def grafico_barras_confiabilidad(costos, tipoNodos):
    """

    """
    data = pd.DataFrame(costos, columns=['Nodos', 'Confiabilidad', 'Costo'])
    tipo_nodos_df = pd.DataFrame(tipoNodos)
    data = pd.concat([data, tipo_nodos_df], axis=1)

    # Obtener valores únicos de cantidad de nodos y confiabilidad
    nodos_unicos = sorted(data['Nodos'].unique())

    confiabilidades_unicas = sorted(data['Confiabilidad'].unique())

    x = np.arange(len(nodos_unicos))  # Posiciones en el eje X
    width = 0.25  # Ancho de cada grupo de barras

    plt.figure(figsize=(12, 7))

    colors = {'Low': 'royalblue',
              'Medium': 'darkorange', 'High': 'forestgreen'}
    bottom_values = {conf: np.zeros(len(nodos_unicos))
                     for conf in confiabilidades_unicas}

    for conf in confiabilidades_unicas:
        for tipo in ['Low', 'Medium', 'High']:
            tipo_counts = [data[(data['Nodos'] == n) & (data['Confiabilidad'] == conf)][tipo].sum()
                           for n in nodos_unicos
                           ]

            bars = plt.bar(
                x + confiabilidades_unicas.index(conf) * width - width,
                tipo_counts,
                width=width,
                label=f"{tipo}" if conf == confiabilidades_unicas[0] else "",
                color=colors[tipo],
                edgecolor='black',
                bottom=bottom_values[conf],
            )

            # Añadir etiquetas dentro de las barras
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + height / 2,
                             f'{int(height)}', ha='center', va='center', fontsize=10, color='white', fontweight='bold')

            # Acumular alturas para el apilamiento correcto
            bottom_values[conf] += tipo_counts

        # Agregar etiqueta de confiabilidad en la parte superior de cada grupo de barras
        for i, n in enumerate(nodos_unicos):
            total_height = bottom_values[conf][i]
            if total_height > 0:
                plt.text(x[i] + confiabilidades_unicas.index(conf) * width - width, total_height + 0.5,
                         f"{conf*100:.0f}%", ha='center', fontsize=12, fontweight='bold', color='black')

    plt.xticks(x, [f"{n}" for n in nodos_unicos])
    plt.title("Distribución de Nodos por Cantidad de Nodos y Confiabilidad")
    plt.xlabel("Number of Nodes")
    plt.ylabel("Total Nodes per Configuration")

    plt.legend(title="Node Type", loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.ylim(0, max(bottom_values[conf]) * 1.2)
    plt.show()
