import gurobipy as gp
from gurobipy import GRB

def serie_model(baseModel, totalNodes, linkCost):
    """
    Extiende el modelo base para incluir restricciones y costos del modelo en serie.

    Parámetros:
    - baseModel (gurobipy.Model): Modelo base generado por base_model.
    - totalNodes (int): Número de nodos en la red (mínimo 4).
    - linkCost (float): Costo de un enlace (debe ser mayor a 0).

    Retorna:
    - costo_total (float): Costo total de la solución.
    - variables_decision (dict): Variables de decisión y sus valores.
    - model (gurobipy.Model): Modelo optimizado.
    """
    # Validación de entrada
    if totalNodes < 4:
        raise ValueError("El número de nodos debe ser al menos 4.")
    if linkCost <= 0:
        raise ValueError("El costo de un enlace debe ser mayor a 0.")

    # Copia del modelo base
    model = baseModel.copy()

    # Recuperar la variable linksCost del modelo base
    linksCost = model.getVarByName("linksCost")
    if linksCost is None:
        raise ValueError("No se encontró la variable linksCost en el modelo base.")

    # Eliminar restricción general de linksCost (si existe)
    linksCost_Condition = model.getConstrByName("LinksCost_General")
    if linksCost_Condition:
        model.remove(linksCost_Condition)

    # Agregar restricción específica del modelo en serie
    model.addConstr(linksCost == linkCost * (totalNodes - 1), name="LinksCost_Serie")

    # Optimizar el modelo
    model.optimize()

    # Verificar solución óptima
    if model.status == GRB.OPTIMAL:
        variables_decision = {var.varName: var.x for var in model.getVars()}
        return model.objVal, variables_decision, model
    else:
        raise Exception("No se encontró una solución óptima.")