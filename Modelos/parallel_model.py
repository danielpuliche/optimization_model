# ============================================================
# Importación de librerías necesarias
# ============================================================
import gurobipy as gp
from gurobipy import GRB
import math

from utils.validation import validar_entrada
from config import LINK_COST, RELIABILITY_BY_NODE_TYPE  # Importar parámetros globales

# ============================================================
# Función principal: parallel_model
# ============================================================
def parallel_model(baseModel, totalNodes, requiredReliability):
    """
    Extiende un modelo base para incluir restricciones y costos específicos del modelo paralelo.

    Parámetros:
    - baseModel (gurobipy.Model): Modelo base.
    - totalNodes (int): Número de nodos en la red (mínimo 4).
    - requiredReliability (float): Confiabilidad total requerida (0 < valor < 1).

    Retorna:
    - costo_total (float): Costo total de la solución.
    - variables_decision (dict): Valores de las variables de decisión.
    - model (gurobipy.Model): Modelo optimizado.

    Lanza:
    - ValueError: Si los parámetros de entrada son inválidos.
    - Exception: Si no se encuentra una solución óptima.
    """
    # Validación de entrada
    validar_entrada(totalNodes, LINK_COST, RELIABILITY_BY_NODE_TYPE)

    # Copia del modelo base
    model = baseModel.copy()

    # Recuperar la variable linksCost del modelo base
    linksCost = model.getVarByName("linksCost")
    if linksCost is None:
        raise ValueError("No se encontró la variable linksCost en el modelo base.")

    # Recuperar las variables de decisión x[u, i]
    x = {
        tuple(map(int, var.varName.split('[')[1].split(']')[0].split(','))): var
        for var in model.getVars() if "x" in var.varName
    }

    # Definir conjuntos de nodos y tipos de nodos
    nodeSet = range(totalNodes)
    nodesTypeSet = range(len(RELIABILITY_BY_NODE_TYPE))

    # Agregar variables para la no confiabilidad de los nodos
    nodeUnreliability = model.addVars(
        nodeSet, vtype=GRB.CONTINUOUS, name="nodeUnreliability"
    )
    logNodeUnreliability = model.addVars(
        nodeSet, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="logNodeUnreliability"
    )

    for u in nodeSet:
        model.addConstr(
            nodeUnreliability[u] == 1 - gp.quicksum(
                RELIABILITY_BY_NODE_TYPE[i] * x[u, i] for i in nodesTypeSet
            ),
            name=f"NodeUnreliability_{u}"
        )
        model.addGenConstrLog(
            nodeUnreliability[u], logNodeUnreliability[u], name=f"LogNodeUnreliability_{u}"
        )

    # Restricción para la confiabilidad total de la red
    model.addConstr(
        gp.quicksum(logNodeUnreliability[u] for u in nodeSet) <= math.log(1 - requiredReliability),
        name="TotalReliability"
    )

    # Eliminar restricción general de linksCost (si existe)
    linksCost_Condition = model.getConstrByName("LinksCost_General")
    if linksCost_Condition:
        model.remove(linksCost_Condition)

    # Agregar restricción específica del modelo paralelo
    model.addConstr(
        linksCost == LINK_COST * (totalNodes * (totalNodes - 1)) / 2,
        name="LinksCost_Paralelo"
    )

    # Optimizar el modelo
    model.optimize()

    # Verificar solución óptima
    if model.status == GRB.OPTIMAL:
        variables_decision = {var.varName: var.x for var in model.getVars()}
        return model.objVal, variables_decision, model
    else:
        print("No se encontró una solución óptima.")
        return None, None, model