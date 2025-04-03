# Importación de librerías
import gurobipy as gp
from gurobipy import GRB
import math

# Importación de utilidades y parámetros globales
from utils.validation import validar_entrada
from config import LINK_COST, RELIABILITY_BY_NODE_TYPE  # Costos y confiabilidades por tipo de nodo

def serie_model(baseModel, totalNodes, requiredReliability):
    """
    Extiende el modelo base para incluir restricciones y costos del modelo en serie.

    Este modelo calcula la confiabilidad total de una red en serie, donde la confiabilidad total
    es el producto de las confiabilidades individuales de los nodos. También ajusta el costo
    total de los enlaces según el modelo en serie.

    Parámetros:
    ----------
    - baseModel (gurobipy.Model): Modelo base generado previamente.
    - totalNodes (int): Número de nodos en la red (mínimo 4).
    - requiredReliability (float): Confiabilidad total requerida para la red (entre 0 y 1).

    Retorna:
    -------
    - costo_total (float): Costo total de la solución óptima.
    - variables_decision (dict): Diccionario con las variables de decisión y sus valores.
    - model (gurobipy.Model): Modelo optimizado.

    Excepciones:
    ------------
    - ValueError: Si los parámetros de entrada no cumplen con las condiciones requeridas.
    - Exception: Si no se encuentra una solución óptima al modelo.
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

    # Agregar variables para la confiabilidad de los nodos
    nodeReliability = model.addVars(
        nodeSet, vtype=GRB.CONTINUOUS, lb=0.001, name="nodeReliability"
    )
    logNodeReliability = model.addVars(
        nodeSet, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="logNodeReliability"
    )

    # Agregar restricciones para la confiabilidad de los nodos
    for u in nodeSet:
        model.addConstr(
            nodeReliability[u] == gp.quicksum(
                RELIABILITY_BY_NODE_TYPE[i] * x[u, i] for i in nodesTypeSet
            ),
            name=f"NodeReliability_{u}"
        )
        model.addGenConstrLog(
            nodeReliability[u], logNodeReliability[u], name=f"LogNodeReliability_{u}"
        )

    # Restricción para la confiabilidad total de la red
    model.addConstr(
        gp.quicksum(logNodeReliability[u] for u in nodeSet) >= math.log(requiredReliability),
        name="TotalReliability"
    )

    # Eliminar restricción general de linksCost (si existe)
    linksCost_Condition = model.getConstrByName("LinksCost_General")
    if linksCost_Condition:
        model.remove(linksCost_Condition)

    # Agregar restricción específica del modelo en serie
    model.addConstr(
        linksCost == LINK_COST * (totalNodes - 1), name="LinksCost_Serie"
    )

    # Optimizar el modelo
    model.optimize()

    # Verificar solución óptima
    if model.status == GRB.OPTIMAL:
        variables_decision = {var.varName: var.x for var in model.getVars()}
        return model.objVal, variables_decision, model
    else:
        raise Exception("No se encontró una solución óptima.")