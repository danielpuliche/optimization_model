# ============================================================
# Importación de librerías necesarias
# ============================================================
import gurobipy as gp
from gurobipy import GRB

# ============================================================
# Función principal: base_model
# ============================================================
def base_model(N, c_values):
    """
    Crea un modelo base de optimización para desplegar nodos con diferentes costos.

    Parámetros:
    - N (int): Número de nodos a desplegar. Debe ser al menos 4.
    - c_values (dict): Costos asociados a cada tipo de nodo (0: Low, 1: Medium, 2: High).

    Retorna:
    - model (gurobipy.Model): Modelo base de Gurobi.
    """
    # ========================================================
    # Validación de entrada
    # ========================================================
    if N < 4:
        raise ValueError("El número de nodos debe ser al menos 4.")
    if not isinstance(c_values, dict) or len(c_values) == 0:
        raise ValueError("c_values debe ser un diccionario con los costos de los nodos.")

    # ========================================================
    # Creación del modelo
    # ========================================================
    model = gp.Model(f"General_Model_{N}_Nodes")

    # ========================================================
    # Definición de conjuntos
    # ========================================================
    U = range(N)  # Conjunto de nodos a desplegar
    I = range(len(c_values))  # Conjunto de tipos de nodos (0: Low, 1: Medium, 2: High)

    # ========================================================
    # Definición de variables
    # ========================================================
    # Variables de decisión: x[u, i] indica si el nodo u es del tipo i
    x = model.addVars(U, I, vtype=GRB.BINARY, name="x")

    # Variable para el costo total de los nodos desplegados
    nodesCost = model.addVar(vtype=GRB.CONTINUOUS, name="nodesCost")

    # Variable para el costo total de los enlaces (inicialmente 0 en este modelo base)
    linksCost = model.addVar(vtype=GRB.CONTINUOUS, name="linksCost")

    # ========================================================
    # Definición de restricciones
    # ========================================================
    # Restricción: Definición del costo total de los nodos
    model.addConstr(
        nodesCost == gp.quicksum(c_values[i] * x[u, i] for u in U for i in I),
        name="NodesCost_def"
    )

    # Restricción: El costo total de los enlaces es 0 (modelo base)
    model.addConstr(linksCost == 0, name="LinksCost_General")

    # Restricción: Cada nodo debe ser de un único tipo
    model.addConstrs(
        (gp.quicksum(x[u, i] for i in I) == 1 for u in U),
        name="Unicidad_i"
    )

    # ========================================================
    # Configuración de la función objetivo
    # ========================================================
    # Minimizar el costo total (nodos + enlaces)
    model.setObjective(nodesCost + linksCost, GRB.MINIMIZE)

    # ========================================================
    # Configuración de parámetros del solver
    # ========================================================
    model.setParam('OutputFlag', 0)  # Desactivar salida de Gurobi

    # ========================================================
    # Optimización del modelo
    # ========================================================
    model.optimize()

    # ========================================================
    # Retorno del modelo optimizado
    # ========================================================
    return model