import gurobipy as gp
from gurobipy import GRB

def base_model(totalNodes, costByNodeType):
    """
    Crea un modelo base de optimización para desplegar nodos con diferentes costos.

    Parámetros:
    - totalNodes (int): Número de nodos a desplegar (mínimo 4).
    - costByNodeType (dict): Costos asociados a cada tipo de nodo (0: Low, 1: Medium, 2: High).

    Retorna:
    - model (gurobipy.Model): Modelo base de Gurobi.

    Descripción de las variables:
    - x[u, i] (binary): Indica si el nodo `u` es del tipo `i`.
    - nodesCost (continuous): Representa el costo total de los nodos desplegados.
    - linksCost (continuous): Representa el costo total de los enlaces (inicialmente 0 en este modelo base).

    Restricciones:
    1. Definición del costo total de los nodos:
       - `nodesCost` es igual a la suma de los costos de los nodos desplegados, calculados como el costo del tipo de nodo multiplicado por la variable binaria `x[u, i]`.
    2. El costo total de los enlaces es 0:
       - `linksCost` se fija en 0, ya que este modelo base no considera enlaces.
    3. Cada nodo debe ser de un único tipo:
       - Para cada nodo `u`, la suma de las variables `x[u, i]` sobre todos los tipos `i` debe ser igual a 1.

    Función objetivo:
    - Minimizar el costo total, que es la suma de `nodesCost` y `linksCost`.

    Configuración adicional:
    - Se desactiva la salida de Gurobi (`OutputFlag = 0`) para evitar mensajes en consola durante la optimización.
    """
    # Validación de entrada
    if totalNodes < 4:
        raise ValueError("El número de nodos debe ser al menos 4.")
    if not isinstance(costByNodeType, dict) or len(costByNodeType) == 0:
        raise ValueError("costByNodeType debe ser un diccionario con los costos de los nodos.")

    # Creación del modelo
    model = gp.Model(f"General_Model_{totalNodes}_Nodes")

    # Conjuntos
    nodesSet = range(totalNodes)
    nodesTypeSet = range(len(costByNodeType))

    # Variables
    x = model.addVars(nodesSet, nodesTypeSet, vtype=GRB.BINARY, name="x")
    nodesCost = model.addVar(vtype=GRB.CONTINUOUS, name="nodesCost")
    linksCost = model.addVar(vtype=GRB.CONTINUOUS, name="linksCost")

    # Restricciones
    model.addConstr(
        nodesCost == gp.quicksum(costByNodeType[i] * x[u, i] for u in nodesSet for i in nodesTypeSet),
        name="NodesCost_def"
    )
    model.addConstr(linksCost == 0, name="LinksCost_General")
    model.addConstrs(
        (gp.quicksum(x[u, i] for i in nodesTypeSet) == 1 for u in nodesSet),
        name="Unicidad_i"
    )

    # Función objetivo: Minimizar el costo total
    model.setObjective(nodesCost + linksCost, GRB.MINIMIZE)

    # Configuración del solver
    model.setParam('OutputFlag', 0)

    # Optimización
    model.optimize()

    return model