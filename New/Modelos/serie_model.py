import gurobipy as gp
from gurobipy import GRB

def serie_model(model_base, N, L):
    """
    Extiende el modelo base para incluir las restricciones y costos específicos del modelo en serie.

    Parámetros:
    - model_base (gurobipy.Model): Modelo base generado por base_model.
    - N (int): Número de nodos en la red.
    - L (float): Costo de un enlace.

    Retorna:
    - costo_total (float): Costo total de la solución.
    - variables_decision (dict): Diccionario con las variables de decisión y sus valores.
    - model (gurobipy.Model): Modelo optimizado de Gurobi.
    """
    # Validación de entrada
    if N < 4:
        raise ValueError("El número de nodos debe ser al menos 4.")
    if L <= 0:
        raise ValueError("El costo de un enlace (L) debe ser mayor a 0.")

    # Copiar el modelo base
    model = model_base.copy()

    # Recuperar la variable linksCost del modelo base
    linksCost = model.getVarByName("linksCost")
    if linksCost is None:
        raise ValueError("No se encontró la variable de costo de enlaces en el modelo base.")

    # Eliminar la restricción general de linksCost (si existe)
    # Esto es necesario para evitar conflictos al agregar la nueva restricción
    linksCost_Condition = model.getConstrByName("LinksCost_General")
    if linksCost_Condition is not None:
        model.remove(linksCost_Condition)

    # Agregar la restricción específica del modelo en serie para el costo de enlaces
    # linksCost = L * (N - 1)
    # donde L es el costo de un enlace y N es el número de nodos
    model.addConstr(linksCost == L * (N - 1), name="LinksCost_Serie")

    # Optimizar el modelo
    model.optimize()

    # Verificar si se encontró una solución óptima
    if model.status == GRB.OPTIMAL:
        # Extraer las variables de decisión y sus valores
        variables_decision = {var.varName: var.x for var in model.getVars()}
        return model.objVal, variables_decision, model
    else:
        raise Exception("No se encontró una solución óptima.")