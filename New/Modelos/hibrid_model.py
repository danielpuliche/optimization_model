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
    activeParallelSubnet = model.addVars(subnetSet, vtype=GRB.BINARY, name="alpha")
    nodesParallelSubnet = model.addVars(subnetSet, vtype=GRB.INTEGER, name="p")
    parallelSubnetLinks = model.addVars(subnetSet, vtype=GRB.INTEGER, name="z")
    totalSerieNodes = model.addVar(vtype=GRB.INTEGER, name="N_s")

    # Definiciones auxiliares
    model.addConstr(totalSerieNodes == gp.quicksum(y[u, 0] for u in nodeSet), name="Ns_def")
    model.addConstrs(
        (nodesParallelSubnet[j] == gp.quicksum(y[u, j] for u in nodeSet) for j in subnetSet if j > 0),
        name="p_def"
    )
    model.addConstrs(
        (2 * parallelSubnetLinks[j] == nodesParallelSubnet[j] * (nodesParallelSubnet[j] - 1) for j in subnetSet if j > 0),
        name="Enlaces_Paralelo_Subred"
    )

    # Restricciones
    model.addConstrs(
        (gp.quicksum(y[u, j] for j in subnetSet) == 1 for u in nodeSet),
        name="Unicidad_Subred"
    )
    model.addConstrs(
        (activeParallelSubnet[j] >= y[u, j] for u in nodeSet for j in subnetSet if j > 0),
        name="Activar_Subred"
    )
    model.addConstrs(
        (gp.quicksum(y[u, j] for u in nodeSet) >= 3 * activeParallelSubnet[j] for j in subnetSet if j > 0),
        name="Subredes_Min_3"
    )
    model.addConstr(
        gp.quicksum(activeParallelSubnet[j] for j in subnetSet if j > 0) >= 1,
        name="AlMenosUnaSubredActiva"
    )

    # Cálculo del costo de enlaces
    extraSubnetConnections = gp.quicksum(activeParallelSubnet[j] for j in subnetSet if j > 0)
    totalParallelSubnetLinks = gp.quicksum(parallelSubnetLinks[j] for j in subnetSet if j > 0)
    model.addConstr(
        linksCost == linkCost * (totalSerieNodes + extraSubnetConnections + totalParallelSubnetLinks - 1),
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