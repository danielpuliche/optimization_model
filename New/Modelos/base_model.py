import gurobipy as gp
from gurobipy import GRB

def base_model(N, c_values):
	"""
	Crea un modelo base de optimización para desplegar nodos con diferentes costos.

	Parámetros:
	- N (int): Número de nodos a desplegar. Debe ser al menos 4.
	- c_values (dict): Costos asociados a cada tipo de nodo (0: Low, 1: Medium, 2: High).

	Retorna:
	- model (gurobipy.Model): Modelo base de Gurobi.
	"""
	# Validación de entrada
	if N < 4:
		raise ValueError("El número de nodos debe ser al menos 4.")
	if not isinstance(c_values, dict) or len(c_values) == 0:
		raise ValueError("c_values debe ser un diccionario con los costos de los nodos.")

	# Crear el modelo
	model = gp.Model(f"General_Model_{N}_Nodes")

	# Conjunto de nodos y tipos
	U = range(N)  # Nodos a desplegar
	I = range(len(c_values))  # Tipos de nodos (0: Low, 1: Medium, 2: High)

	# Variables de decisión: x[u, i] indica si el nodo u es del tipo i
	x = model.addVars(U, I, vtype=GRB.BINARY, name="x")

	# Costo total de los nodos desplegados
	nodesCost = model.addVar(vtype=GRB.CONTINUOUS, name="nodesCost")
	model.addConstr(
		nodesCost == gp.quicksum(c_values[i] * x[u, i] for u in U for i in I),
		name="NodesCost_def"
	)

	# Costo total de los enlaces (inicialmente 0 en el modelo base)
	linksCost = model.addVar(vtype=GRB.CONTINUOUS, name="linksCost")
	model.addConstr(linksCost == 0, name="LinksCost_General")

	# Restricción: Cada nodo debe ser de un único tipo
	model.addConstrs(
		(gp.quicksum(x[u, i] for i in I) == 1 for u in U),
		name="Unicidad_i"
	)

	# Configurar el objetivo: Minimizar el costo total (nodos + enlaces)
	model.setObjective(nodesCost + linksCost, GRB.MINIMIZE)

	# Configurar parámetros de Gurobi
	model.setParam('OutputFlag', 0)  # Desactivar salida de Gurobi

	model.optimize()

	return model