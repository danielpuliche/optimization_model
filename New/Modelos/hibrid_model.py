# ============================================================
# Importación de librerías necesarias
# ============================================================
import gurobipy as gp
from gurobipy import GRB

# ============================================================
# Función principal: hibrid_model
# ============================================================
def hibrid_model(baseModel, totalNodes, linkCost):
    """
    Extiende el modelo base para incluir restricciones y costos del modelo híbrido.

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

    # Variables adicionales
    nodeSet = range(totalNodes)
    subnetSet = range(totalNodes // 3 + 1)
    y = model.addVars(nodeSet, subnetSet, vtype=GRB.BINARY, name="y")
    activeSubnet = model.addVars(subnetSet, vtype=GRB.BINARY, name="activeSubnet")
    nodesBySubnet = model.addVars(subnetSet, vtype=GRB.INTEGER, name="p")
    parallelSubnetLinks = model.addVars(subnetSet, vtype=GRB.INTEGER, name="z")

    # Definiciones auxiliares
    model.addConstrs( # Definición de nodos por subred
        (nodesBySubnet[j] == gp.quicksum(y[u, j] for u in nodeSet) for j in subnetSet),
        name="parallelNodesBySubnet_def"
    )
    model.addConstrs( # Definición de enlaces paralelos por subred j > 0
        (2 * parallelSubnetLinks[j] == nodesBySubnet[j] * (nodesBySubnet[j] - 1) for j in subnetSet if j > 0),
        name="Enlaces_Paralelo_Subred"
    )
    model.addConstrs( # Definición de subred activa
        (activeSubnet[j] >= y[u, j] for u in nodeSet for j in subnetSet),
        name="Activar_Subred"
    )

    # Restricciones
    model.addConstr(activeSubnet[0] == 1, name="Subred0_Min_1") # Subred 0 activa
    model.addConstr(activeSubnet[1] == 1, name="Subred1_Min_1") # Subred 1 activa
    model.addConstrs( # Cada nodo pertenece a una sola subred
        (gp.quicksum(y[u, j] for j in subnetSet) == 1 for u in nodeSet),
        name="Unicidad_Subred"
    )
    model.addConstrs( # Las subredes paralelo activas deben tener al menos 3 nodos
        (gp.quicksum(y[u, j] for u in nodeSet) >= 3 * activeSubnet[j] for j in subnetSet if j > 0),
        name="Subredes_Min_3"
    )
    model.addConstr( # Al menos 2 subredes activas (subred serie y al menos una paralela)
        gp.quicksum(activeSubnet[j] for j in subnetSet) >= 2,
        name="AlMenosDosSubredesActivas"
    )

    # Cálculo del costo de enlaces
    extraSubnetConnections = gp.quicksum(activeSubnet[j] for j in subnetSet) - 1
    totalParallelSubnetLinks = gp.quicksum(parallelSubnetLinks[j] for j in subnetSet if j > 0)
    model.addConstr(
        linksCost == linkCost * (nodesBySubnet[0] + extraSubnetConnections + totalParallelSubnetLinks - 1),
        name="LinksCost_Hibrido"
    )

    # Optimización
    model.optimize()

    # Verificar solución óptima
    if model.status == GRB.OPTIMAL:
        variables_decision = {var.varName: var.x for var in model.getVars()}
        return model.objVal, variables_decision, model
    else:
        raise Exception("No se encontró una solución óptima.")