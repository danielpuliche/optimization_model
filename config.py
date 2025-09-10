# Configuration file for the network reliability analysis

# Costs per node type (Low, Medium, High)
COST_BY_NODE_TYPE = {
    0: 24.2, # Low Cost for 2025
    1: 91.82, # Medium Cost for 2025
    2: 227.06 # High Cost for 2025
}

# Reliability per node type (Low, Medium, High)
RELIABILITY_BY_NODE_TYPE = [0.9, 0.95, 0.99]

# Cost of a link
LINK_COST = 7.69 # Link Cost for 2025

# Number of equidistant values for required reliabilities
NUM_EQUIDISTANT_VALUES = 200

# Number of samples for high reliability analysis (reduced for faster execution)
# High reliability analysis focuses on a narrow range (0.99998 to 0.9999999...)
# so fewer samples provide sufficient resolution while significantly reducing computation time
NUM_HIGH_RELIABILITY_VALUES = 50

# Maximum reliability
MAX_RELIABILITY = 0.9999999999999999

# ============================================================
# Analysis Configuration
# ============================================================

# Default node counts for analysis
DEFAULT_NODE_COUNTS = [5, 6, 11]

# Reliability ranges for different topologies
SERIES_RELIABILITY_RANGE = (0.5, MAX_RELIABILITY)
MESH_RELIABILITY_RANGE = (0.5, MAX_RELIABILITY)
HYBRID_RELIABILITY_RANGE = (0.5, MAX_RELIABILITY)

# High reliability ranges for detailed analysis
HIGH_RELIABILITY_MESH_RANGE = (0.99998, MAX_RELIABILITY)
HIGH_RELIABILITY_HYBRID_RANGE = (0.99998, MAX_RELIABILITY)