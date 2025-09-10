"""
Utilities module for network reliability optimization analysis.

This module provides functions for processing optimization results, generating plots,
and handling data visualization for network topology optimization problems.
"""

from collections import defaultdict
from itertools import product
import pandas as pd
import re
import os
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# Data Processing Functions
# ============================================================

def process_results_table(totalNodes, decisionVariables, model_type="general"):
    """
    Processes decision variables to build lists of active nodes.

    Args:
        totalNodes (int): Number of nodes in the model.
        decisionVariables (dict): Decision variables and their values.
        model_type (str): Type of model ("general", "hybrid").

    Returns:
        tuple: Lists of active nodes (x and optionally y).
            - x_active_nodes (List[List[int]]): Active nodes for x variables
            - y_active_nodes (Optional[List[List[int]]]): Active nodes for y variables (hybrid only)
    """
    x_vars = {var: val for var, val in decisionVariables.items()
              if var.startswith("x")}
    y_vars = {var: val for var, val in decisionVariables.items()
              if var.startswith("y")}

    x_active_nodes = process_active_variables(x_vars, totalNodes, "x")
    y_active_nodes = process_active_variables(
        y_vars, totalNodes, "y") if model_type == "hybrid" else None

    return x_active_nodes, y_active_nodes


def show_results_table(totalNodes, minimizedCost, decisionVariables, model_type="general"):
    """
    Displays optimization results in tabular format.

    Args:
        totalNodes (int): Number of nodes in the model.
        minimizedCost (float): Total cost of the solution.
        decisionVariables (dict): Decision variables and their values.
        model_type (str): Type of model ("general", "hybrid").
    """
    print("=" * 52)
    print(f"Number of Nodes: {totalNodes}")
    print("=" * 52)

    if minimizedCost is None:
        print("No solution found")
        return

    print("Optimization Results:")
    print("=" * 52)
    print(f"Total Cost: {minimizedCost}")
    print(f"Nodes Cost: {decisionVariables.get('nodesCost', 'N/A')}")
    print(f"Links Cost: {decisionVariables.get('linksCost', 'N/A')}")
    print("=" * 52)

    x_active_nodes, y_active_nodes = process_results_table(
        totalNodes, decisionVariables, model_type)

    # Display active nodes table (x)
    columns_titles_x = ["Low Cost", "Mid Cost", "High Cost"]
    row_index = [u + 1 for u in range(totalNodes)]
    table_x = pd.DataFrame(
        x_active_nodes, columns=columns_titles_x, index=row_index)
    print("Active nodes (x):")
    print(table_x)
    print("=" * 52)

    # Display active nodes table (y) for hybrid model
    if model_type == "hybrid" and y_active_nodes:
        columns_titles_y = [f"Subnet {i}" for i in range(len(y_active_nodes[0]))]
        table_y = pd.DataFrame(
            y_active_nodes, columns=columns_titles_y, index=row_index)
        print("Active nodes (y):")
        print(table_y)
        print("=" * 52)


def process_active_variables(variables: dict, node_count: int, prefix: str) -> list[list[int]]:
    """
    Processes active variables to build a list of values per node.

    Args:
        variables (dict): Decision variables and their values.
        node_count (int): Number of nodes in the model.
        prefix (str): Variable prefix ("x" or "y").

    Returns:
        List[List[int]]: List of lists with active variable values.
    """
    active_nodes = [[] for _ in range(node_count)]
    for var, val in variables.items():
        if var.startswith(prefix):
            u, _ = map(int, var[len(prefix) + 1:-1].split(","))
            active_nodes[u].append(int(val))
    return active_nodes


# ============================================================
# Utility Functions
# ============================================================

def generate_equidistant_list(start, end, num_elements):
    """
    Generates a list of equidistant numbers between two given floats, excluding the endpoints.

    Args:
        start (float): The starting value.
        end (float): The ending value.
        num_elements (int): The number of elements in the resulting list.

    Returns:
        list: A list of equidistant floats between start and end (excluding endpoints).

    Raises:
        ValueError: If num_elements <= 0, start == end, or end < start.

    Example:
        >>> generate_equidistant_list(0.5, 1.0, 3)
        [0.625, 0.75, 0.875]
    """
    if num_elements <= 0:
        raise ValueError("Number of elements must be greater than 0.")
    if start == end:
        raise ValueError("Start and end values must be different.")
    if end < start:
        raise ValueError("End value must be greater than start value.")

    step = (end - start) / (num_elements + 1)
    result = []
    for i in range(1, num_elements + 1):
        result.append(start + i * step)
    return result


# ============================================================
# Plotting Functions
# ============================================================

def plot_minimized_costs_single(requiredReliabilities, minimizedCosts, topology, totalNodes, analysis_type="standard"):
    """
    Generates a plot of minimized costs as a function of required reliability for a single topology.

    Args:
        requiredReliabilities (list): List of required reliability values.
        minimizedCosts (list): List of corresponding minimized costs.
        topology (str): Network topology name (e.g., 'series', 'mesh', 'hybrid').
        totalNodes (int): Total number of nodes in the network.
        analysis_type (str): Type of analysis ("standard" or "high_reliability").

    Example:
        >>> plot_minimized_costs_single([0.6, 0.7, 0.8], [100, 120, 150], 'series', 6, "standard")
    """
    plt.figure(figsize=(10, 6))
    plt.plot(requiredReliabilities, minimizedCosts, linestyle='-', color='b', marker='.')
    plt.xlabel('Required Reliability')
    plt.ylabel('Minimized Costs')
    plt.grid(True)

    # Create organized directory structure
    directory = f"Figures/{analysis_type}/individual_topologies/{topology}"
    fileName = f"costVsReliability_{topology}_{totalNodes}.png"

    if not os.path.exists(directory):
        os.makedirs(directory)

    plt.savefig(os.path.join(directory, fileName))
    plt.close()


def plot_total_costs(reliabilities, node_counts, total_costs):
    """
    Generates a line plot of total costs, using only the information returned by the model.

    Args:
        reliabilities (list[float]): List of reliability values.
        node_counts (list[int]): List of node counts.
        total_costs (list[float]): List of costs in product order (reliability, nodes).
    """
    # Build costs_by_reliability internally
    combinations = list(product(reliabilities, node_counts))
    costs_by_reliability = defaultdict(list)

    for idx, (reliability, _) in enumerate(combinations):
        costs_by_reliability[reliability].append(total_costs[idx])

    # Create plot
    plt.figure(figsize=(12, 6))

    for reliability, costs in costs_by_reliability.items():
        plt.plot(node_counts, costs, marker='o', label=f'Reliability: {reliability}')

    plt.xlabel('Nodes Count')
    plt.ylabel('Minimized Costs')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()


def plot_stacked_distribution(reliabilities, node_counts, decision_sets, topology, analysis_type="standard"):
    """
    Generates a stacked bar chart of node types (low, medium, high),
    grouped by combination of reliability and number of nodes.

    Args:
        reliabilities (list[float]): Reliability values (in execution order).
        node_counts (list[int]): Node counts (in execution order).
        decision_sets (list[dict]): List of decision variables as returned by the model.
        topology (str): Network topology name.
        analysis_type (str): Type of analysis ("standard" or "high_reliability").
    """
    combinations = list(product(reliabilities, node_counts))

    data = []
    for idx, decision in enumerate(decision_sets):
        reliability, nodes = combinations[idx]
        low = medium = high = 0

        for var, val in decision.items():
            if var.startswith("x[") and round(val) == 1:
                _, node_type = map(
                    int, var[var.find("[")+1:var.find("]")].split(","))
                if node_type == 0:
                    low += 1
                elif node_type == 1:
                    medium += 1
                elif node_type == 2:
                    high += 1

        data.append({
            "Reliability": reliability,
            "Nodes": nodes,
            "Low": low,
            "Medium": medium,
            "High": high
        })

    # Group by reliability for plotting
    grouped = defaultdict(list)
    for d in data:
        grouped[d["Reliability"]].append(d)

    fig, ax = plt.subplots(figsize=(12, 6))
    bar_width = 0.25
    group_spacing = 1.0
    positions = []

    colors = {
        "Low": "#1f77b4",
        "Medium": "#ff7f0e",
        "High": "#2ca02c"
    }

    for i, reliability in enumerate(sorted(grouped.keys())):
        group = grouped[reliability]
        for j, item in enumerate(group):
            x = i * group_spacing + j * bar_width
            positions.append(x)

            l, m, h = item["Low"], item["Medium"], item["High"]
            ax.bar(x, l, bar_width, color=colors["Low"], edgecolor='black', linewidth=0.8)
            ax.bar(x, m, bar_width, bottom=l, color=colors["Medium"], edgecolor='black', linewidth=0.8)
            ax.bar(x, h, bar_width, bottom=l + m, color=colors["High"], edgecolor='black', linewidth=0.8)

            # Add text labels for each segment
            for height, y0, text in [(l, 0, l), (m, l, m), (h, l + m, h)]:
                if height > 0:
                    ax.text(x, y0 + height / 2, str(int(text)),
                            ha='center', va='center', fontsize=12, color="white")

    # Set x-axis ticks and labels
    xtick_positions = [
        i * group_spacing + (len(grouped[reliability]) - 1) * bar_width / 2
        for i, reliability in enumerate(sorted(grouped.keys()))
    ]
    xtick_labels = [f'{round(reliability*100, 10)}%' for reliability in sorted(grouped.keys())]

    ax.set_xticks(xtick_positions)
    ax.set_xticklabels(xtick_labels)
    ax.set_ylabel('Node Count', fontsize=16)
    ax.set_xlabel('Required Reliability', fontsize=16)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    # Add legend
    ax.legend(handles=[
        plt.Rectangle((0, 0), 1, 1, color=colors["Low"], label='Low', edgecolor='black', linewidth=0.8),
        plt.Rectangle((0, 0), 1, 1, color=colors["Medium"], label='Medium', edgecolor='black', linewidth=0.8),
        plt.Rectangle((0, 0), 1, 1, color=colors["High"], label='High', edgecolor='black', linewidth=0.8),
    ], title="Node Type", fontsize=14, title_fontsize=14)

    ax.grid(True, axis='y', linestyle='--', alpha=0.6)
    ax.set_yticks(range(0, max(node_counts) + 2, 1))
    plt.ylim(0, max(node_counts) + 1)
    plt.tight_layout()

    # Save plot with organized directory structure
    directory = f"Figures/{analysis_type}/individual_topologies/{topology}"
    fileName = f"stacked_{topology}.png"

    if not os.path.exists(directory):
        os.makedirs(directory)

    plt.savefig(os.path.join(directory, fileName))
    plt.show()
    plt.close()


# ============================================================
# Advanced Plotting Functions
# ============================================================

def plot_costs_comparison_joint_topologies(totalNodes, minimizedCosts, seriesRequiredReliabilities, meshRequiredReliabilities, hybridRequiredReliabilities, analysis_type="standard"):
    """
    Plots cost vs reliability comparison for all topologies on the same graph for each node count.

    Args:
        totalNodes (list): List of node counts to analyze.
        minimizedCosts (dict): Dictionary with minimized costs for each topology and node count.
        seriesRequiredReliabilities (list): Reliability values for series topology.
        meshRequiredReliabilities (list): Reliability values for mesh topology.
        hybridRequiredReliabilities (list): Reliability values for hybrid topology.
        analysis_type (str): Type of analysis ("standard" or "high_reliability").
    """
    print("Plotting costs vs reliability for joint topologies")

    for n in totalNodes:
        serieMinimizedCosts = minimizedCosts[f"nodes_{n}_series"]
        meshMinimizedCosts = minimizedCosts[f"nodes_{n}_mesh"]
        hybridMinimizedCosts = minimizedCosts[f"nodes_{n}_hybrid"]

        # Plot the results on the same graph
        plt.figure(figsize=(10, 6))
        plt.plot(seriesRequiredReliabilities, serieMinimizedCosts, label='Series', color='blue', linestyle='-', marker='.')
        plt.plot(meshRequiredReliabilities, meshMinimizedCosts, label='Mesh', color='red', linestyle='-', marker='.')
        plt.plot(hybridRequiredReliabilities, hybridMinimizedCosts, label='Hybrid', color='green', linestyle='-', marker='.')

        plt.xlabel('Required Reliability', fontsize=16)
        plt.ylabel('Minimized Costs', fontsize=16)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.grid(True)
        plt.legend(loc='upper left', fontsize=14)

        # Save plot with organized directory structure
        directory = f"Figures/{analysis_type}/jointTopologies/"
        fileName = f"CostVsReliability_{n}nodes.png"

        if not os.path.exists(directory):
            os.makedirs(directory)

        plt.tight_layout()
        plt.savefig(os.path.join(directory, fileName), dpi=600, bbox_inches='tight')
        plt.close()

        print(f"Plot for {n} nodes saved")


def plot_costs_comparison_by_topology(totalNodes, minimizedCosts, seriesRequiredReliabilities, meshRequiredReliabilities, hybridRequiredReliabilities, analysis_type="standard"):
    """
    Plots cost vs reliability comparison by topology, showing different node counts on each graph.

    Args:
        totalNodes (list): List of node counts to analyze.
        minimizedCosts (dict): Dictionary with minimized costs for each topology and node count.
        seriesRequiredReliabilities (list): Reliability values for series topology.
        meshRequiredReliabilities (list): Reliability values for mesh topology.
        hybridRequiredReliabilities (list): Reliability values for hybrid topology.
        analysis_type (str): Type of analysis ("standard" or "high_reliability").
    """
    print("Plotting costs vs reliability by topology...")

    topologies = [
        ("Series", "series", seriesRequiredReliabilities, 'blue'),
        ("Mesh", "mesh", meshRequiredReliabilities, 'orange'),
        ("Hybrid", "hybrid", hybridRequiredReliabilities, 'green')
    ]

    for title, key, reliabilities, color_base in topologies:
        plt.figure(figsize=(10, 6))
        colors = ['blue', 'red', 'green']  # One color per line/nodes

        for i, n in enumerate(totalNodes):
            costs = minimizedCosts[f"nodes_{n}_{key}"]
            plt.plot(reliabilities, costs, label=f'{n} Nodes',
                     color=colors[i], linestyle='-', marker='.')

        # Visual configuration
        plt.xlabel('Required Reliability', fontsize=16)
        plt.ylabel('Minimized Costs (SCU)', fontsize=16)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.grid(True)
        plt.legend(loc='upper left', fontsize=14)

        # Save the plot with organized directory structure
        directory = f"Figures/{analysis_type}/NodesJointByTopology/{key}/"
        fileName = f"costVsReliability_{key}.png"

        if not os.path.exists(directory):
            os.makedirs(directory)

        plt.tight_layout()
        plt.savefig(os.path.join(directory, fileName), dpi=600, bbox_inches='tight')
        plt.close()

        print(f"Topology {title} plot saved")


def plot_costs_zoom_hybrid_mesh_comparison(totalNodes, minimizedCosts, meshRequiredReliabilities, hybridRequiredReliabilities, analysis_type="high_reliability"):
    """
    Creates zoomed plots focusing on high reliability ranges for Hybrid and Mesh topologies.

    Args:
        totalNodes (list): List of node counts to analyze.
        minimizedCosts (dict): Dictionary with minimized costs for each topology and node count.
        meshRequiredReliabilities (list): Reliability values for mesh topology.
        hybridRequiredReliabilities (list): Reliability values for hybrid topology.
        analysis_type (str): Type of analysis ("standard" or "high_reliability").
    """
    print("Plotting zoom for Hybrid and Mesh topologies...")

    topologies = [
        ("Hybrid", "hybrid", hybridRequiredReliabilities, (0.999, 1.00)),
        ("Mesh", "mesh", meshRequiredReliabilities, (0.999, 1.00))
    ]

    for title, key, reliabilities, (x_min, x_max) in topologies:
        plt.figure(figsize=(10, 6))
        colors = ['blue', 'red', 'green']

        for i, n in enumerate(totalNodes):
            costs = minimizedCosts[f"nodes_{n}_{key}"]
            plt.plot(reliabilities, costs, label=f'{n} Nodes',
                     color=colors[i], linestyle='-', marker='.')

        plt.xlabel('Required Reliability', fontsize=16)
        plt.ylabel('Minimized Costs', fontsize=16)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.grid(True)
        plt.legend(loc='upper left', fontsize=14)
        plt.xlim(x_min, x_max)

        # Save with organized directory structure
        directory = f"Figures/{analysis_type}/NodesJointByTopology/{key}/"
        fileName = f"costVsReliability_{key}_zoom.png"

        if not os.path.exists(directory):
            os.makedirs(directory)

        plt.tight_layout()
        plt.savefig(os.path.join(directory, fileName), dpi=600, bbox_inches='tight')
        plt.close()

        print(f"Zoom plot for {title} saved")
