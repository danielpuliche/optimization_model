# Importación de librerías
import gurobipy as gp
from gurobipy import GRB

# Importación de parámetros globales
# Diccionario con los costos por tipo de nodo
from config import COST_BY_NODE_TYPE


def base_model(totalNodes):
    """
    Crea un modelo base de optimización para desplegar nodos con diferentes costos.

    Parámetros:
    - totalNodes (int): Número de nodos a desplegar (mínimo 4).

    Retorna:
    - model (gurobipy.Model): Modelo base de Gurobi.

    Variables:
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
    if not isinstance(COST_BY_NODE_TYPE, dict) or len(COST_BY_NODE_TYPE) == 0:
        raise ValueError(
            "COST_BY_NODE_TYPE debe ser un diccionario con los costos de los nodos.")

    # Creación del modelo
    model = gp.Model(f"General_Model_{totalNodes}_Nodes")

    # Definición de conjuntos
    nodesSet = range(totalNodes)  # Conjunto de nodos
    nodesTypeSet = range(len(COST_BY_NODE_TYPE))  # Conjunto de tipos de nodos

    # Definición de variables
    x = model.addVars(nodesSet, nodesTypeSet, vtype=GRB.BINARY,
                      name="x")  # Variables binarias
    # Costo total de los nodos
    nodesCost = model.addVar(vtype=GRB.CONTINUOUS, name="nodesCost")
    # Costo total de los enlaces
    linksCost = model.addVar(vtype=GRB.CONTINUOUS, name="linksCost")

    # Restricciones
    # Restricción 1: Definición del costo total de los nodos
    model.addConstr(
        nodesCost == gp.quicksum(
            COST_BY_NODE_TYPE[i] * x[u, i] for u in nodesSet for i in nodesTypeSet),
        name="NodesCost_def"
    )

    # Restricción 2: El costo total de los enlaces es 0
    model.addConstr(linksCost == 0, name="LinksCost_General")

    # Restricción 3: Cada nodo debe ser de un único tipo
    model.addConstrs(
        (gp.quicksum(x[u, i] for i in nodesTypeSet) == 1 for u in nodesSet),
        name="Unicidad_i"
    )

    # Función objetivo: Minimizar el costo total
    model.setObjective(nodesCost + linksCost, GRB.MINIMIZE)

    # Configuración del solver
    model.setParam('OutputFlag', 0)  # Desactiva la salida de Gurobi en consola

    # Optimización
    model.optimize()

    return model
