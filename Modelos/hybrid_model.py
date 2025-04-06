# ============================================================
# Importación de librerías necesarias
# ============================================================
import gurobipy as gp
from gurobipy import GRB
import math

from utils.validation import validar_entrada
from config import LINK_COST, RELIABILITY_BY_NODE_TYPE  # Importar parámetros globales

# ============================================================
# Función principal: hybrid_model
# ============================================================
def hybrid_model(baseModel, totalNodes, requiredReliability):
	"""
	Extiende el modelo base para incluir restricciones y costos del modelo híbrido.

	Parámetros:
	- baseModel (gurobipy.Model): Modelo base generado por base_model.
	- totalNodes (int): Número de nodos en la red (mínimo 4).
	- requiredReliability (float): Confiabilidad total requerida (0 < valor < 1).

	Retorna:
	- costo_total (float): Costo total de la solución.
	- variables_decision (dict): Variables de decisión y sus valores.
	- model (gurobipy.Model): Modelo optimizado.
	"""
	# Validación de entrada
	validar_entrada(totalNodes, LINK_COST, RELIABILITY_BY_NODE_TYPE)

	# Copia del modelo base
	model = baseModel.copy()

	nodeSet = range(totalNodes)
	subnetSet = range(totalNodes // 3 + 1)
	nodesTypeSet = range(len(RELIABILITY_BY_NODE_TYPE))

	# Recuperar la variable linksCost del modelo base
	linksCost = model.getVarByName("linksCost")
	if linksCost is None:
		raise ValueError("No se encontró la variable linksCost en el modelo base.")

	# Recuperar las variables de decisión x[u, i]
	x = {
		tuple(map(int, var.varName.split('[')[1].split(']')[0].split(','))): var
		for var in model.getVars() if "x" in var.varName
	}

	# Eliminar restricción general de linksCost (si existe)
	linksCost_Condition = model.getConstrByName("LinksCost_General")
	if linksCost_Condition:
		model.remove(linksCost_Condition)

	# Variables adicionales
	y = model.addVars(nodeSet, subnetSet, vtype=GRB.BINARY, name="y")
	activeSubnet = model.addVars(subnetSet, vtype=GRB.BINARY, name="activeSubnet")
	nodesBySubnet = model.addVars(subnetSet, vtype=GRB.INTEGER, name="nodesBySubnet")
	parallelSubnetLinks = model.addVars(subnetSet, vtype=GRB.INTEGER, name="parallelSubnetLinks")
	nodeReliability = model.addVars(nodeSet, vtype=GRB.CONTINUOUS, name="nodeReliability")
	nodeUnreliability = model.addVars(nodeSet, vtype=GRB.CONTINUOUS, name="nodeUnreliability")
	logNodeReliability = model.addVars(nodeSet, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="logNodeReliability")
	logNodeUnreliability = model.addVars(nodeSet, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="logNodeUnreliability")
	logSubnetTotalReliability = model.addVars(subnetSet, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="logSubnetTotalReliability")
	totalReliability = model.addVar(vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="TotalReliability")
	extraSubnetConnections = model.addVar(vtype=GRB.INTEGER, name="extraSubnetConnections")
	totalParallelSubnetLinks = model.addVar(vtype=GRB.INTEGER, name="totalParallelSubnetLinks")

	for u in nodeSet: # Definición de confiabilidad e inconfiabilidad de los nodos
		model.addConstr( # Definición de nodeReliability[u]
			nodeReliability[u] == gp.quicksum(
				RELIABILITY_BY_NODE_TYPE[i] * x[u, i] for i in nodesTypeSet
			),
			name=f"NodeReliability_{u}"
		)
		model.addConstr( # Definición de nodeUnreliability[u]
			nodeUnreliability[u] == 1 - gp.quicksum(
				RELIABILITY_BY_NODE_TYPE[i] * x[u, i] for i in nodesTypeSet
			),
			name=f"NodeUnreliability_{u}"
		)
		model.addGenConstrLog( # Definición de logNodeReliability[u]
			nodeReliability[u], logNodeReliability[u], name=f"LogNodeReliability_{u}"
		)
		model.addGenConstrLog( # Definición de logNodeUnreliability[u]
			nodeUnreliability[u], logNodeUnreliability[u], name=f"LogNodeUnreliability_{u}"
		)

	model.addConstrs( # Definición de nodos por subred
		(nodesBySubnet[j] == gp.quicksum(y[u, j] for u in nodeSet) for j in subnetSet),
		name="NodesBySubnet_def"
	)
	model.addConstrs( # Definición de enlaces paralelos por subred j > 0
		(2 * parallelSubnetLinks[j] == nodesBySubnet[j] * (nodesBySubnet[j] - 1) for j in subnetSet if j > 0),
		name="Enlaces_Paralelo_Subred"
	)

	# Constraints

	model.addConstrs( # Constraint: Cada nodo pertenece a una sola subred
		(gp.quicksum(y[u, j] for j in subnetSet) == 1 for u in nodeSet),
		name="Unicidad_Subred"
	)
	model.addConstr( # Constraint: Al menos una subred activa
		gp.quicksum(activeSubnet[j] for j in subnetSet) >= 1,
		name="AlMenosUnaSubredeActiva"
	)

	model.addConstr( # Constraint: La suma de nodos por subred activa debe ser igual al total de nodos
		gp.quicksum(nodesBySubnet[j]*activeSubnet[j] for j in subnetSet) == totalNodes,
		name="TotalNodesBySubnet"
	)

	# model.addConstr( # La subred serie activa debe tener al menos 1 nodo
	# 	(nodesBySubnet[0] >= activeSubnet[0]),
	# 	name="Subred_Serie_Activa"
	# )
	model.addConstrs( # Las subredes paralelo activas deben tener al menos 3 nodos
		(nodesBySubnet[j] >= 3 * activeSubnet[j] for j in subnetSet if j > 0),
		name="Subredes_Min_3"
	)


	for j in subnetSet: # Definición de confiabilidad por subredes
		if j == 0: # confiabilidad de la subred serie
			model.addConstr( # Definición de la confiabilidad de la subred serie
				logSubnetTotalReliability[0] == gp.quicksum(y[u, 0] * logNodeReliability[u] for u in nodeSet),
				name=f"SerieSubnetReliability_def_0"
			)
		else: # confiabilidad de las subredes paralelas
			subnetUnreliability = model.addVar(vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name=f"subnetUnreliability_{j}")
			expSubnetUnreliability = model.addVar(vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name=f"expSubnetUnreliability_{j}")
			subnetReliability = model.addVar(vtype=GRB.CONTINUOUS, name=f"subnetReliability_{j}")
			logSubnetReliability = model.addVar(vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name=f"logSubnetReliability_{j}")

			model.addConstr( # Definir subnetUnreliability
				subnetUnreliability == gp.quicksum(y[u, j] * logNodeUnreliability[u] for u in nodeSet),
			)
			model.addGenConstrExp( # Definir relación del exp^K_j
				subnetUnreliability, expSubnetUnreliability,
				name=f"expSubnetUnreliability_{j}"
			)
			model.addConstr( # Definición de subnetReliability
				subnetReliability == 1 - expSubnetUnreliability,
				name=f"SubnetReliability_{j}"
			)
			model.addGenConstrLog( # Definir relación del log(1-exp(K_j))
				subnetReliability, logSubnetReliability,
				name=f"LogSubnetReliability_{j}"
			)
			model.addConstr( # Definición de logSubnetTotalReliability[j]
				logSubnetTotalReliability[j] == logSubnetReliability,
				name=f"ParallelSubnetReliability_def_{j}"
			)

	model.addConstr( # Definición de totalReliability
		totalReliability == gp.quicksum(logSubnetTotalReliability[j] for j in subnetSet),
		name="TotalReliability_def"
	)
	model.addConstr( # Constraint de confiabilidad total
		totalReliability >= math.log(requiredReliability),
		name="TotalReliability"
	)

	# Cálculo del costo de enlaces
	model.addConstr(
		extraSubnetConnections == gp.quicksum(activeSubnet[j] for j in subnetSet if j > 0) - 1,
		name="ExtraSubnetConnections"
	)
	model.addConstr(
		totalParallelSubnetLinks == gp.quicksum(parallelSubnetLinks[j] for j in subnetSet if j > 0),
		name="TotalParallelSubnetLinks"
	)
	model.addConstr(
		linksCost == LINK_COST * (nodesBySubnet[0] + extraSubnetConnections + totalParallelSubnetLinks),
		name="LinksCost_Hibrido"
	)

	# Optimización
	model.optimize()

	# Verificar solución óptima
	if model.status == GRB.OPTIMAL:
		variables_decision = {var.varName: var.x for var in model.getVars()}
		return model.objVal, variables_decision, model
	else:
		return None, None, model