# Import libraries
import gurobipy as gp
from gurobipy import GRB

# Import global parameters
# Dictionary with costs by node type
from config import COST_BY_NODE_TYPE


def base_model(totalNodes):
    """
    Creates a base optimization model to deploy nodes with different costs.

    Parameters:
    - totalNodes (int): Number of nodes to deploy (minimum 4).

    Returns:
    - model (gurobipy.Model): Gurobi base model.

    Variables:
    - x[u, i] (binary): Indicates if node `u` is of type `i`.
    - nodesCost (continuous): Represents the total cost of deployed nodes.
    - linksCost (continuous): Represents the total cost of links (initially 0 in this base model).

    Constraints:
    1. Definition of total nodes cost:
       - `nodesCost` equals the sum of deployed nodes costs, calculated as the node type cost multiplied by the binary variable `x[u, i]`.
    2. Total links cost is 0:
       - `linksCost` is set to 0, since this base model doesn't consider links.
    3. Each node must be of a unique type:
       - For each node `u`, the sum of variables `x[u, i]` over all types `i` must equal 1.

    Objective function:
    - Minimize total cost, which is the sum of `nodesCost` and `linksCost`.

    Additional configuration:
    - Gurobi output is disabled (`OutputFlag = 0`) to avoid console messages during optimization.
    """
    # Input validation
    if totalNodes < 4:
        raise ValueError("The number of nodes must be at least 4.")
    if not isinstance(COST_BY_NODE_TYPE, dict) or len(COST_BY_NODE_TYPE) == 0:
        raise ValueError(
            "COST_BY_NODE_TYPE must be a dictionary with node costs.")

    # Model creation
    model = gp.Model(f"General_Model_{totalNodes}_Nodes")

    # Set definitions
    nodes_set = range(totalNodes)  # Set of nodes
    node_types_set = range(len(COST_BY_NODE_TYPE))  # Set of node types

    # Variable definitions
    x = model.addVars(nodes_set, node_types_set, vtype=GRB.BINARY,
                      name="x")  # Binary variables
    # Total cost of nodes
    nodesCost = model.addVar(vtype=GRB.CONTINUOUS, name="nodesCost")
    # Total cost of links
    linksCost = model.addVar(vtype=GRB.CONTINUOUS, name="linksCost")

    # Constraints
    # Constraint 1: Definition of total nodes cost
    model.addConstr(
        nodesCost == gp.quicksum(
            COST_BY_NODE_TYPE[i] * x[u, i] for u in nodes_set for i in node_types_set),
        name="NodesCost_def"
    )

    # Constraint 2: Total links cost is 0
    model.addConstr(linksCost == 0, name="LinksCost_General")

    # Constraint 3: Each node must be of a unique type
    model.addConstrs(
        (gp.quicksum(x[u, i] for i in node_types_set) == 1 for u in nodes_set),
        name="Uniqueness_i"
    )

    # Objective function: Minimize total cost
    model.setObjective(nodesCost + linksCost, GRB.MINIMIZE)

    # Solver configuration
    model.setParam('OutputFlag', 0)  # Disable Gurobi console output

    model.setParam('FeasibilityTol', 1e-9)
    model.setParam('OptimalityTol', 1e-9)
    model.setParam('IntFeasTol', 1e-9)
    model.setParam('MIPGap', 1e-9)

    # Optimization
    model.optimize()

    return model
