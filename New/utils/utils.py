import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt

def mostrarResultadosTabla(totalNodes, minimizedCost, decisionVariables, tipo="general"):
    """
    Muestra los resultados de optimización en formato tabular.

    Parámetros:
    - totalNodes (int): Número de nodos en el modelo.
    - minimizedCost (float): Costo total de la solución.
    - decisionVariables (dict): Variables de decisión y sus valores.
    - tipo (str): Tipo de modelo ("general", "hibrido").
    """
    print("=" * 52)
    print(f"Cantidad de Nodos: {totalNodes}")
    print("=" * 52)

    if minimizedCost is None:
        print("No se encontró solución")
        return

    print("Resultado de la Optimización:")
    print("=" * 52)
    print(f"Costo Total: {minimizedCost}")
    print(f"Costo nodos: {decisionVariables.get('nodesCost', 'N/A')}")
    print(f"Costo enlaces: {decisionVariables.get('linksCost', 'N/A')}")
    print("=" * 52)

    # Filtrar variables de decisión por prefijo
    xVars = {var: val for var, val in decisionVariables.items() if var.startswith("x")}
    yVars = {var: val for var, val in decisionVariables.items() if var.startswith("y")}

    # Procesar nodos activos
    xactiveNodes = procesarVariablesActivas(xVars, totalNodes, "x")
    if tipo == "hibrido":
        yactiveNodes = procesarVariablesActivas(yVars, totalNodes, "y")

    # Mostrar tabla de nodos activos (x)
    columns_titles_x = ["Low Cost", "Mid Cost", "High Cost"]
    row_index = [u + 1 for u in range(totalNodes)]
    tablax = pd.DataFrame(xactiveNodes, columns=columns_titles_x, index=row_index)
    print("Nodos activos (x):")
    print(tablax)
    print("=" * 52)

    # Mostrar tabla de nodos activos (y) si es modelo híbrido
    if tipo == "hibrido":
        columns_titles_y = [f"Subred {i}" for i in range(len(yactiveNodes[0]))]
        tablay = pd.DataFrame(yactiveNodes, columns=columns_titles_y, index=row_index)
        print("Nodos activos (y):")
        print(tablay)
        print("=" * 52)

def procesarVariablesActivas(variables, cantidadNodos, prefix):
    """
    Procesa las variables activas para construir una lista de valores por nodo.

    Parámetros:
    - variables (dict): Variables de decisión y sus valores.
    - cantidadNodos (int): Número de nodos en el modelo.
    - prefix (str): Prefijo de las variables ("x" o "y").

    Retorna:
    - List[List[int]]: Lista de listas con los valores de las variables activas.
    """
    activeNodes = []
    for u in range(cantidadNodos):
        valores = []
        pattern = re.compile(rf'^{prefix}\[{u},')
        for var, val in variables.items():
            if pattern.match(var):
                valores.append(int(val))
        activeNodes.append(valores)
    return activeNodes

def generate_equidistant_list(start, end, num_elements):
    """
    Generates a list of equidistant numbers between two given floats, excluding the endpoints.

    Args:
        start: The starting float.
        end: The ending float.
        num_elements: The number of elements in the resulting list.

    Returns:
        A list of equidistant floats between start and end (excluding start and end).
        Returns an empty list if num_elements is zero or less.
        Returns an empty list if start and end are the same
    """

    if num_elements <=0:
        raise ValueError("num_elements must be greater than 0")
    if start == end:
        raise ValueError("start and end must be different")
    if end < start:
        raise ValueError("end must be greater than start")

    step = (end - start) / (num_elements + 1)
    result = []
    for i in range(1, num_elements+1):
        result.append(round(start + i * step, 12))
    return result

def graficar_costos_minimizados(requiredReliabilities, serieMinimizedCosts):
    plt.figure(figsize=(10, 6))
    plt.plot(requiredReliabilities, serieMinimizedCosts, marker='o', linestyle='-', color='b')
    plt.title('Costos Minimizados vs Fiabilidad Requerida')
    plt.xlabel('Fiabilidad Requerida')
    plt.ylabel('Costos Minimizados')
    plt.grid(True)
    for x, y in zip(requiredReliabilities, serieMinimizedCosts):
        plt.text(x, y, f'x = {x:.2f}\ny = {y:.2f}', fontsize=9, ha='right', va='bottom')
    plt.show()