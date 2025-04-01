import gurobipy as gp
from gurobipy import GRB

def hibrid_model(model_base, N, L):
    """
    Extiende el modelo base para incluir las restricciones y costos específicos del modelo híbrido.

    Parámetros:
    - model_base (gurobipy.Model): Modelo base generado por base_model.
    - N (int): Número de nodos en la red.
    - L (float): Costo de un enlace.

    Retorna:
    - costo_total (float): Costo total de la solución.
    - variables_decision (dict): Diccionario con las variables de decisión y sus valores.
    - model (gurobipy.Model): Modelo optimizado de Gurobi.
    """
    # Validación de entrada
    if N < 4:
        raise ValueError("El número de nodos debe ser al menos 4.")
    if L <= 0:
        raise ValueError("El costo de un enlace (L) debe ser mayor a 0.")

    # Conjuntos
    U = range(N)  # Nodos a desplegar
    J = range(N // 3 + 1)  # Subredes (0: serie, 1 en adelante: paralelo)

    # Copiar el modelo base
    model = model_base.copy()

    # Recuperar la variable linksCost del modelo base
    linksCost = model.getVarByName("linksCost")
    if linksCost is None:
        raise ValueError("No se encontró la variable de costo de enlaces en el modelo base.")

    # Eliminar la restricción general de linksCost (si existe)
    linksCost_Condition = model.getConstrByName("LinksCost_General")
    if linksCost_Condition is not None:
        model.remove(linksCost_Condition)

    # Variables adicionales
    y = model.addVars(U, J, vtype=GRB.BINARY, name="y")  # Nodo u pertenece a la subred j
    alpha = model.addVars(J, vtype=GRB.BINARY, name="alpha")  # Subred j activa o no
    p = model.addVars(J, vtype=GRB.INTEGER, name="p")  # Número de nodos en la subred j
    z = model.addVars(J, vtype=GRB.INTEGER, name="z")  # Número de enlaces en paralelo por subred j
    N_s = model.addVar(vtype=GRB.INTEGER, name="N_s")  # Número de nodos en la subred serie (j = 0)

    # ============================
    # Definiciones de variables auxiliares
    # ============================

    # Definición: Número de nodos en la subred serie (j = 0)
    model.addConstr(N_s == gp.quicksum(y[u, 0] for u in U), name="Ns_def")

    # Definición: Número de nodos en cada subred paralela (j >= 1)
    model.addConstrs(
        (p[j] == gp.quicksum(y[u, j] for u in U) for j in J if j > 0),
        name="p_def"
    )

    # Definición: Número de enlaces en paralelo por subred j >= 1
    model.addConstrs(
        (2 * z[j] == p[j] * (p[j] - 1) for j in J if j > 0),
        name="Enlaces_Paralelo_Subred"
    )

    # ============================
    # Restricciones del modelo
    # ============================

    # Restricción: Cada nodo debe pertenecer a una única subred
    model.addConstrs(
        (gp.quicksum(y[u, j] for j in J) == 1 for u in U),
        name="Unicidad_Subred"
    )

    # Restricción: Activar subred si tiene nodos asignados
    model.addConstrs(
        (alpha[j] >= y[u, j] for u in U for j in J if j > 0),
        name="Activar_Subred"
    )

    # Restricción: Si la subred j >= 1 existe, debe tener al menos 3 nodos
    model.addConstrs(
        (gp.quicksum(y[u, j] for u in U) >= 3 * alpha[j] for j in J if j > 0),
        name="Subredes_Min_3"
    )

    # Restricción: Al menos una subred paralela debe estar activa
    model.addConstr(
        gp.quicksum(alpha[j] for j in J if j > 0) >= 1,
        name="AlMenosUnaSubredActiva"
    )

    # ============================
    # Cálculo del costo de enlaces
    # ============================

    # H: Número de enlaces adicionales entre subredes paralelas
    H = gp.quicksum(alpha[j] for j in J if j > 0) - 1  # Enlaces adicionales por subredes paralelas

    # B: Número de enlaces internos en las subredes paralelas
    B = gp.quicksum(z[j] for j in J if j > 0)

    # Restricción: Costo total de los enlaces
    model.addConstr(
        linksCost == L * (N_s + H + B),
        name="LinksCost_Hibrido"
    )

    # Optimizar el modelo
    model.optimize()

    # Verificar si se encontró una solución óptima
    if model.status == GRB.OPTIMAL:
        # Extraer las variables de decisión y sus valores
        variables_decision = {var.varName: var.x for var in model.getVars()}
        return model.objVal, variables_decision, model
    else:
        raise Exception("No se encontró una solución óptima.")