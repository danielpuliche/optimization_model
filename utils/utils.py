import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt

def procesarResultadosTabla(totalNodes, decisionVariables, tipo="general"):
    """
    Procesa las variables de decisión para construir listas de nodos activos.

    Parámetros:
    - totalNodes (int): Número de nodos en el modelo.
    - decisionVariables (dict): Variables de decisión y sus valores.
    - tipo (str): Tipo de modelo ("general", "hibrido").

    Retorna:
    - Tuple[List[List[int]], Optional[List[List[int]]]]: Listas de nodos activos (x y opcionalmente y).
    """
    xVars = {var: val for var, val in decisionVariables.items() if var.startswith("x")}
    yVars = {var: val for var, val in decisionVariables.items() if var.startswith("y")}

    xactiveNodes = procesarVariablesActivas(xVars, totalNodes, "x")
    yactiveNodes = procesarVariablesActivas(yVars, totalNodes, "y") if tipo == "hibrido" else None

    return xactiveNodes, yactiveNodes

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

    xactiveNodes, yactiveNodes = procesarResultadosTabla(totalNodes, decisionVariables, tipo)

    # Mostrar tabla de nodos activos (x)
    columns_titles_x = ["Low Cost", "Mid Cost", "High Cost"]
    row_index = [u + 1 for u in range(totalNodes)]
    tablax = pd.DataFrame(xactiveNodes, columns=columns_titles_x, index=row_index)
    print("Nodos activos (x):")
    print(tablax)
    print("=" * 52)

    # Mostrar tabla de nodos activos (y) si es modelo híbrido
    if tipo == "hibrido" and yactiveNodes:
        columns_titles_y = [f"Subred {i}" for i in range(len(yactiveNodes[0]))]
        tablay = pd.DataFrame(yactiveNodes, columns=columns_titles_y, index=row_index)
        print("Nodos activos (y):")
        print(tablay)
        print("=" * 52)

def procesarVariablesActivas(variables: dict, cantidadNodos: int, prefix: str) -> list[list[int]]:
    """
    Procesa las variables activas para construir una lista de valores por nodo.

    Parámetros:
    - variables (dict): Variables de decisión y sus valores.
    - cantidadNodos (int): Número de nodos en el modelo.
    - prefix (str): Prefijo de las variables ("x" o "y").

    Retorna:
    - List[List[int]]: Lista de listas con los valores de las variables activas.
    """
    activeNodes = [[] for _ in range(cantidadNodos)]
    for var, val in variables.items():
        if var.startswith(prefix):
            u, _ = map(int, var[len(prefix) + 1:-1].split(","))
            activeNodes[u].append(int(val))
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

    if num_elements <= 0:
        raise ValueError("El número de elementos debe ser mayor a 0.")
    if start == end:
        raise ValueError("Los valores de inicio y fin deben ser diferentes.")
    if end < start:
        raise ValueError("El valor de fin debe ser mayor que el de inicio.")

    step = (end - start) / (num_elements + 1)
    result = []
    for i in range(1, num_elements+1):
        result.append(round(start + i * step, 12))
    return result

def graficar_costos_minimizados(requiredReliabilities, serieMinimizedCosts):
    """
    Genera un gráfico de costos minimizados en función de la fiabilidad requerida.

    Parámetros:
    - requiredReliabilities (list): Lista de valores de fiabilidad requerida.
    - serieMinimizedCosts (list): Lista de costos minimizados correspondientes.

    Ejemplo:
    >>> graficar_costos_minimizados([0.6, 0.7, 0.8], [100, 120, 150])
    """
    plt.figure(figsize=(10, 6))
    plt.plot(requiredReliabilities, serieMinimizedCosts, marker='o', linestyle='-', color='b')
    plt.title('Costos Minimizados vs Fiabilidad Requerida')
    plt.xlabel('Fiabilidad Requerida')
    plt.ylabel('Costos Minimizados')
    plt.grid(True)
    for x, y in zip(requiredReliabilities, serieMinimizedCosts):
        plt.text(x, y, f'x = {x:.2f}\ny = {y:.2f}', fontsize=9, ha='right', va='bottom')
    plt.show()