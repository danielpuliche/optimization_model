# Configuration file for the network reliability analysis

# Select the evaluation year for the analysis
EVALUATION_YEAR = True # 2025: True, 2030: False

# Costos por tipo de nodo (Low, Medium, High)
COST_BY_NODE_TYPE = {
    0: 24.2 if EVALUATION_YEAR else 10.74,  # Low Cost
    1: 91.82 if EVALUATION_YEAR else 40.74,  # Medium Cost
    2: 227.06 if EVALUATION_YEAR else 100.75   # High Cost
}

# Confiabilidad por tipo de nodo (Low, Medium, High)
RELIABILITY_BY_NODE_TYPE = [0.9, 0.95, 0.99]

# Costo de un enlace
LINK_COST = 7.69 if EVALUATION_YEAR else 3.41

# Número de valores equidistantes para confiabilidades requeridas
NUM_EQUIDISTANT_VALUES = 200

# Confiabilidad máxima
MAX_RELIABILITY = 0.9999999999999999