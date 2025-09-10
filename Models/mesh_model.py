# ============================================================
# Import necessary libraries
# ============================================================
import gurobipy as gp
from gurobipy import GRB
import math

from utils.validation import input_validation
# Import global parameters
from config import LINK_COST, RELIABILITY_BY_NODE_TYPE

# ============================================================
# Main function: mesh_model
# ============================================================


def mesh_model(baseModel, totalNodes, requiredReliability):
    """
    Extends a base model to include constraints and costs specific to the mesh model.

    Parameters:
    - baseModel (gurobipy.Model): Base model.
    - totalNodes (int): Number of nodes in the network (minimum 4).
    - requiredReliability (float): Total required reliability (0 < value < 1).

    Returns:
    - total_cost (float): Total cost of the solution.
    - decision_variables (dict): Values of the decision variables.
    - model (gurobipy.Model): Optimized model.

    Raises:
    - ValueError: If input parameters are invalid.
    - Exception: If no optimal solution is found.
    """
    # Input validation
    input_validation(totalNodes, LINK_COST, RELIABILITY_BY_NODE_TYPE)

    # Copy of the base model
    model = baseModel.copy()

    # Recover the linksCost variable from the base model
    linksCost = model.getVarByName("linksCost")
    if linksCost is None:
        raise ValueError(
            "linksCost variable not found in the base model.")

    # Recover decision variables x[u, i]
    x = {
        tuple(map(int, var.varName.split('[')[1].split(']')[0].split(','))): var
        for var in model.getVars() if "x" in var.varName
    }

    # Define sets of nodes and node types
    nodeSet = range(totalNodes)
    nodesTypeSet = range(len(RELIABILITY_BY_NODE_TYPE))

    # Add variables for node unreliability
    nodeUnreliability = model.addVars(
        nodeSet, vtype=GRB.CONTINUOUS, name="nodeUnreliability"
    )
    logNodeUnreliability = model.addVars(
        nodeSet, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="logNodeUnreliability"
    )

    for u in nodeSet:
        model.addConstr(
            nodeUnreliability[u] == 1 - gp.quicksum(
                RELIABILITY_BY_NODE_TYPE[i] * x[u, i] for i in nodesTypeSet
            ),
            name=f"NodeUnreliability_{u}"
        )
        model.addGenConstrLog(
            nodeUnreliability[u], logNodeUnreliability[
                u], name=f"LogNodeUnreliability_{u}"
        )

    # Constraint for the total reliability of the network
    model.addConstr(
        gp.quicksum(logNodeUnreliability[u] for u in nodeSet) <= math.log(
            1 - requiredReliability),
        name="TotalReliability"
    )

    # Remove general linksCost constraint (if it exists)
    linksCost_Condition = model.getConstrByName("LinksCost_General")
    if linksCost_Condition:
        model.remove(linksCost_Condition)

    # Add specific constraint for the mesh model
    model.addConstr(
        linksCost == LINK_COST * (totalNodes * (totalNodes - 1)) / 2,
        name="LinksCost_Mesh"
    )

    # Optimize the model
    model.optimize()

    # Check optimal solution
    if model.status == GRB.OPTIMAL:
        decision_variables = {var.varName: var.x for var in model.getVars()}
        return model.objVal, decision_variables, model
    else:
        return None, None, model