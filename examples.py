"""
Example usage script for network reliability optimization analysis.

This script demonstrates how to use the optimization models for custom analysis.
"""

from main import run_standard_analysis, run_high_reliability_analysis, compute_minimized_costs_by_topology
from utils.utils import generate_equidistant_list, plot_costs_comparison_joint_topologies
from config import MAX_RELIABILITY, NUM_EQUIDISTANT_VALUES


def custom_analysis_example():
    """
    Example of how to run a custom analysis with specific parameters.
    """
    print("Running custom analysis example...")

    # Custom node counts
    custom_nodes = [4, 6, 8]

    # Custom reliability ranges
    series_reliabilities = generate_equidistant_list(0.6, 0.95, 50)
    mesh_reliabilities = generate_equidistant_list(0.98, MAX_RELIABILITY, 50)
    hybrid_reliabilities = generate_equidistant_list(0.99, MAX_RELIABILITY, 50)

    # Compute costs
    costs = compute_minimized_costs_by_topology(
        custom_nodes, series_reliabilities, mesh_reliabilities, hybrid_reliabilities
    )

    # Generate comparison plot
    plot_costs_comparison_joint_topologies(
        custom_nodes, costs, series_reliabilities, mesh_reliabilities, hybrid_reliabilities
    )

    print("Custom analysis completed!")


def single_topology_analysis(topology="series", nodes=[5, 6], reliability_range=(0.5, 0.95)):
    """
    Example of analyzing a single topology with custom parameters.

    Args:
        topology (str): Topology to analyze ("series", "mesh", or "hybrid")
        nodes (list): List of node counts
        reliability_range (tuple): Min and max reliability values
    """
    from Models.base_model import base_model
    from Models.series_model import series_model
    from Models.mesh_model import mesh_model
    from Models.hybrid_model import hybrid_model
    from utils.utils import plot_minimized_costs_single

    print(f"Analyzing {topology} topology...")

    # Select model function
    model_functions = {
        "series": series_model,
        "mesh": mesh_model,
        "hybrid": hybrid_model
    }

    if topology not in model_functions:
        raise ValueError(f"Unknown topology: {topology}")

    model_func = model_functions[topology]

    # Generate reliability range
    reliabilities = generate_equidistant_list(*reliability_range, 100)

    # Analyze each node count
    for n in nodes:
        base = base_model(n)
        costs = []

        for rel in reliabilities:
            cost, _, _ = model_func(base, n, rel)
            costs.append(cost)

        # Plot results
        plot_minimized_costs_single(reliabilities, costs, topology.capitalize(), n)
        print(f"Analysis for {n} nodes completed")


if __name__ == "__main__":
    print("=" * 60)
    print("Custom Analysis Examples")
    print("=" * 60)

    # Example 1: Standard analysis
    print("\n1. Running standard analysis...")
    run_standard_analysis([5, 6])

    # Example 2: Custom analysis
    print("\n2. Running custom analysis...")
    custom_analysis_example()

    # Example 3: Single topology analysis
    print("\n3. Running single topology analysis...")
    single_topology_analysis("series", [4, 5, 6], (0.7, 0.9))

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
