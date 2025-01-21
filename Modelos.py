# Importar librerías
from gurobipy import *
import math
import os
import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np


# Mostrar modelo
def mostrarModelo(filename,model):
    print(filename)
    if os.path.exists(filename):
        os.remove(filename)
    model.write(filename)
    model.display()

# Mostrar resultados
def mostrarResultados(costo, variablesDecision):
    print('===================================')
    print('Función objetivo: ',str(round(costo,4)))
    for v in variablesDecision.keys():
        print(v, variablesDecision[v])

tipoNodos = [1,2,3] # L:1, M:2, H:3
costos = {1:1,2:3,3:7}
confiabilidad = {1:0.5,2:0.6,3:0.7}

# Modelo Base
def base_model(cantidadNodos):
    # Variables
    nodos = list(range(cantidadNodos))
    arcos = [(i,j) for i in nodos for j in tipoNodos]

    # Crear modelo
    model = Model(f"Modelo_Base_{cantidadNodos}_Nodos")
    model.setParam('OutputFlag', 0)

    # Variables de decisión
    x = model.addVars(arcos,vtype= GRB.BINARY, name='x') # Variable booleana para determinar si un nodo está activo

    # Variable objetivo
    model.setObjective(quicksum(costos[j]*x[i,j] for j in tipoNodos for i in nodos),GRB.MINIMIZE) # Costo de los nodos desplegados

    # Restricciones generales
    # 1. Cada nodo solo puede ser de un tipo
    model.addConstrs((quicksum(x[i,j] for j in tipoNodos)==1 for i in nodos), name='unicidad')

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
    z = model.addVars(nodos, vtype= GRB.CONTINUOUS, lb=0.1, name='z') # Sumatoria interna de la confiabilidad en serie
    log_z = model.addVars(nodos, vtype = GRB.CONTINUOUS, name='log_z') # Logaritmo natural de z

    # Restricciones
    # 2.1. Relación entre z y x
    for u in nodos:
        model.addConstr(z[u] == sum((1/confiabilidad[i]) * x[u,i] for i in tipoNodos), name=f"z_u_{u}")

    # 2.2. Logaritmo de z_u
    for u in nodos:
        model.addGenConstrLog(z[u], log_z[u], name=f"log_z_{u}")

    # 2.3. Restricción de la productoria
    model.addConstr(-quicksum(log_z[u] for u in nodos) >= math.log(confiabilidadObjetivo), name="log_prod")

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

# Mostrar resultados
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

        tabla = pd.DataFrame(activeNodes, columns=columns_titles, index=row_index)
        print(tabla)
        print("====================================================")



def grafico_costo_vs_confiabilidad_general(costos):
    """
    Genera un gráfico de Costo vs Confiabilidad Objetivo para cada cantidad de nodos fija.
    
    :param costos: Lista de tuplas (nodos, confiabilidad, costo) con los resultados.
    """
    data = pd.DataFrame(costos, columns=['Nodos', 'Confiabilidad', 'Costo'])
    nodos_unicos = data['Nodos'].unique()

    plt.figure(figsize=(10, 6))
    for nodos in nodos_unicos:
        subset = data[data['Nodos'] == nodos]
        plt.plot(subset['Confiabilidad'], subset['Costo'], marker='o', label=f'Nodos: {nodos}')

    plt.title("Costo vs Confiabilidad Objetivo")
    plt.xlabel("Confiabilidad Objetivo")
    plt.ylabel("Costo Total")
    plt.grid(True)
    plt.legend()
    plt.show()

def grafico_costo_vs_cantidad_nodos_general(costos, confiabilidad_fija):
    """
    Genera un gráfico de Costo vs Cantidad de Nodos para una confiabilidad fija.
    
    :param costos: Lista de tuplas (nodos, confiabilidad, costo) con los resultados.
    :param confiabilidad_fija: Valor de confiabilidad fijo para filtrar los datos.
    """
    data = pd.DataFrame(costos, columns=['Nodos', 'Confiabilidad', 'Costo'])
    subset = data[data['Confiabilidad'] == confiabilidad_fija]

    plt.figure(figsize=(10, 6))
    plt.plot(subset['Nodos'], subset['Costo'], marker='o', linestyle='-', label=f'Confiabilidad: {confiabilidad_fija}')

    plt.title(f"Costo vs Cantidad de Nodos (Confiabilidad: {confiabilidad_fija})")
    plt.xlabel("Cantidad de Nodos")
    plt.ylabel("Costo Total")
    plt.grid(True)
    plt.legend()
    plt.show()


def grafico_barras_confiabilidad(costos, tipoNodos):
    """
    Genera un gráfico de barras donde cada barra representa un rango de confiabilidad subdividido
    en segmentos que indican el número de nodos de cada tipo (Low, Medium, High).

    :param costos: Lista de tuplas (nodos, confiabilidad, costo) con los resultados.
    :param tipoNodos: Lista de diccionarios con los conteos de nodos por tipo para cada confiabilidad.
    """
    data = pd.DataFrame(costos, columns=['Nodos', 'Confiabilidad', 'Costo'])

    # Definir rangos de confiabilidad (porcentajes)
    rangos = ["Baja (0-1%)", "Media (1-3%)", "Alta (>3%)"]
    data['Rango'] = pd.cut(data['Confiabilidad'] * 100, bins=[0, 1, 3, np.inf], labels=rangos)

    # Agrupar tipoNodos por rangos dinámicamente
    rango_map = {rango: {'Low': 0, 'Medium': 0, 'High': 0} for rango in rangos}
    for idx, row in data.iterrows():
        rango = row['Rango']
        nodo_tipo = tipoNodos[idx]
        rango_map[rango]['Low'] += nodo_tipo['Low']
        rango_map[rango]['Medium'] += nodo_tipo['Medium']
        rango_map[rango]['High'] += nodo_tipo['High']

    # Preparar datos finales para las barras
    low_counts = [rango_map[r]['Low'] for r in rangos]
    medium_counts = [rango_map[r]['Medium'] for r in rangos]
    high_counts = [rango_map[r]['High'] for r in rangos]

    x = np.arange(len(rangos))  # Posiciones en el eje X

    plt.figure(figsize=(12, 7))

    # Crear las barras apiladas
    bars1 = plt.bar(x, low_counts, label='Low Cost Nodes', color='blue')
    bars2 = plt.bar(x, medium_counts, bottom=low_counts, label='Medium Cost Nodes', color='orange')
    bars3 = plt.bar(x, high_counts, bottom=np.add(low_counts, medium_counts), label='High Cost Nodes', color='green')

    # Añadir etiquetas de valores en las barras
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + height / 2,
                         f'{int(height)}', ha='center', va='center', fontsize=10, color='white')

    plt.xticks(x, rangos)
    plt.title("Distribución de Nodos por Rango de Confiabilidad")
    plt.xlabel("Rango de Confiabilidad")
    plt.ylabel("Número de Nodos")
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()