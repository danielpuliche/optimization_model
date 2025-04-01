import pandas as pd
import re

def mostrarResultadosTabla(cantidadNodos, costo, variablesDecision, tipo="general"):
    """
    Función genérica para mostrar resultados de optimización en tablas.

    Parámetros:
    - cantidadNodos (int): Número de nodos en el modelo.
    - costo (float): Costo total de la solución.
    - variablesDecision (dict): Diccionario con las variables de decisión y sus valores.
    - tipo (str): Tipo de modelo ("general", "hibrido").
    """
    print("=" * 52)
    print(f"Cantidad de Nodos: {cantidadNodos}")
    print("=" * 52)

    if costo is None:
        print("No se encontró solución")
        return

    print("Resultado de la Optimización:")
    print("=" * 52)
    print(f"Costo Total: {costo}")
    print(f"Costo nodos: {variablesDecision.get('nodesCost', 'N/A')}")
    print(f"Costo enlaces: {variablesDecision.get('linksCost', 'N/A')}")
    print("=" * 52)

    # Filtrar variables de decisión según prefijo
    xVars = {var: val for var, val in variablesDecision.items() if var.startswith("x")}
    yVars = {var: val for var, val in variablesDecision.items() if var.startswith("y")}

    # Procesar nodos activos
    xactiveNodes = procesarVariablesActivas(xVars, cantidadNodos, "x")
    if tipo == "hibrido":
        yactiveNodes = procesarVariablesActivas(yVars, cantidadNodos, "y")

    # Crear tablas
    columns_titles_x = ["Low Cost", "Mid Cost", "High Cost"]
    row_index = [u + 1 for u in range(cantidadNodos)]
    tablax = pd.DataFrame(xactiveNodes, columns=columns_titles_x, index=row_index)
    print("Nodos activos (x):")
    print(tablax)
    print("=" * 52)

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
    - variables (dict): Diccionario con las variables de decisión y sus valores.
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