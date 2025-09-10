# Import libraries
import gurobipy as gp
from gurobipy import GRB
import math

# Import utilities and global parameters
from utils.validation import input_validation
# Costs and reliabilities by node type
from config import LINK_COST, RELIABILITY_BY_NODE_TYPE


def series_model(baseModel, totalNodes, requiredReliability):
    """
    Extends the base model to include constraints and costs for the series model.

    This model calculates the total reliability of a series network, where the total reliability
    is the product of the individual node reliabilities. It also adjusts the total cost
    of links according to the series model.

    Parameters:
    ----------
    - baseModel (gurobipy.Model): Previously generated base model.
    - totalNodes (int): Number of nodes in the network (minimum 4).
    - requiredReliability (float): Total reliability required for the network (between 0 and 1).

    Returns:
    -------
    - total_cost (float): Total cost of the optimal solution.
    - decision_variables (dict): Dictionary with decision variables and their values.
    - model (gurobipy.Model): Optimized model.

    Exceptions:
    ------------
    - ValueError: If input parameters do not meet the required conditions.
    - Exception: If no optimal solution is found for the model.
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

    # Add variables for node reliability
    nodeReliability = model.addVars(
        nodeSet, vtype=GRB.CONTINUOUS, lb=0.001, name="nodeReliability"
    )
    logNodeReliability = model.addVars(
        nodeSet, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="logNodeReliability"
    )

    # Add constraints for node reliability
    for u in nodeSet:
        model.addConstr(
            nodeReliability[u] == gp.quicksum(
                RELIABILITY_BY_NODE_TYPE[i] * x[u, i] for i in nodesTypeSet
            ),
            name=f"NodeReliability_{u}"
        )
        model.addGenConstrLog(
            nodeReliability[u], logNodeReliability[
                u], name=f"LogNodeReliability_{u}"
        )

    # Constraint for the total reliability of the network
    model.addConstr(
        gp.quicksum(logNodeReliability[u] for u in nodeSet) >= math.log(
            requiredReliability),
        name="TotalReliability"
    )

    # Remove general linksCost constraint (if it exists)
    linksCost_constraint = model.getConstrByName("LinksCost_General")
    if linksCost_constraint:
        model.remove(linksCost_constraint)

    # Add specific constraint for the series model
    model.addConstr(
        linksCost == LINK_COST * (totalNodes - 1), name="LinksCost_Series"
    )

    # Optimize the model
    model.optimize()

    # Check optimal solution
    if model.status == GRB.OPTIMAL:
        decision_variables = {var.varName: var.x for var in model.getVars()}
        return model.objVal, decision_variables, model
    else:
        return None, None, model