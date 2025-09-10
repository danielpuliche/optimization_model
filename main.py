from Models.base_model import base_model
from Models.series_model import series_model
from Models.mesh_model import mesh_model
from Models.hybrid_model import hybrid_model
from utils.utils import (
    plot_minimized_costs_single,
    generate_equidistant_list,
    plot_costs_comparison_joint_topologies,
    plot_costs_comparison_by_topology,
    plot_costs_zoom_hybrid_mesh_comparison
)
from config import (
    NUM_EQUIDISTANT_VALUES,
    NUM_HIGH_RELIABILITY_VALUES,
    DEFAULT_NODE_COUNTS,
    SERIES_RELIABILITY_RANGE,
    MESH_RELIABILITY_RANGE,
    HYBRID_RELIABILITY_RANGE,
    HIGH_RELIABILITY_MESH_RANGE,
    HIGH_RELIABILITY_HYBRID_RANGE
)


def compute_minimized_costs_by_topology(totalNodes, seriesRequiredReliabilities, meshRequiredReliabilities, hybridRequiredReliabilities):
    """
    Computes minimized costs for all topologies across different node counts and reliability requirements.

    Args:
        totalNodes (list): List of node counts to analyze.
        seriesRequiredReliabilities (list): Reliability values for series topology.
        meshRequiredReliabilities (list): Reliability values for mesh topology.
        hybridRequiredReliabilities (list): Reliability values for hybrid topology.

    Returns:
        dict: Dictionary with minimized costs for each topology and node count.
    """
    resultsDictionary = {}

    for n in totalNodes:
        baseModel = base_model(n)

        # Initialize cost lists
        serieMinimizedCosts = []
        meshMinimizedCosts = []
        hybridMinimizedCosts = []

        # Compute series costs
        for reqRel in seriesRequiredReliabilities:
            serieMinCost, _, _ = series_model(baseModel, n, reqRel)
            serieMinimizedCosts.append(serieMinCost)
        print(f"Minimized cost calculation for {n} nodes in series completed")

        # Compute mesh costs
        for reqRel in meshRequiredReliabilities:
            meshMinCost, _, _ = mesh_model(baseModel, n, reqRel)
            meshMinimizedCosts.append(meshMinCost)
        print(f"Minimized cost calculation for {n} nodes in mesh completed")

        # Compute hybrid costs
        for reqRel in hybridRequiredReliabilities:
            hybridMinCost, _, _ = hybrid_model(baseModel, n, reqRel)
            hybridMinimizedCosts.append(hybridMinCost)
        print(f"Minimized cost calculation for {n} nodes in hybrid completed")

        # Store results
        resultsDictionary[f"nodes_{n}_series"] = serieMinimizedCosts
        resultsDictionary[f"nodes_{n}_mesh"] = meshMinimizedCosts
        resultsDictionary[f"nodes_{n}_hybrid"] = hybridMinimizedCosts

    return resultsDictionary


def plot_individual_topology_results(totalNodes, minimizedCosts, seriesRequiredReliabilities, meshRequiredReliabilities, hybridRequiredReliabilities, analysis_type="standard"):
    """
    Plots individual results for each topology and node count.

    Args:
        totalNodes (list): List of node counts to analyze.
        minimizedCosts (dict): Dictionary with minimized costs.
        seriesRequiredReliabilities (list): Reliability values for series topology.
        meshRequiredReliabilities (list): Reliability values for mesh topology.
        hybridRequiredReliabilities (list): Reliability values for hybrid topology.
        analysis_type (str): Type of analysis ("standard" or "high_reliability").
    """
    try:
        for n in totalNodes:
            serieMinimizedCosts = minimizedCosts[f"nodes_{n}_series"]
            meshMinimizedCosts = minimizedCosts[f"nodes_{n}_mesh"]
            hybridMinimizedCosts = minimizedCosts[f"nodes_{n}_hybrid"]

            # Plot individual results
            plot_minimized_costs_single(seriesRequiredReliabilities, serieMinimizedCosts, "Series", n, analysis_type)
            plot_minimized_costs_single(meshRequiredReliabilities, meshMinimizedCosts, "Mesh", n, analysis_type)
            plot_minimized_costs_single(hybridRequiredReliabilities, hybridMinimizedCosts, "Hybrid", n, analysis_type)

        print("Individual plotting successful")
    except Exception as e:
        print(f"Error in individual plotting: {e}")


def run_standard_analysis(totalNodes=None):
    """
    Runs the standard analysis with default reliability ranges.

    Args:
        totalNodes (list, optional): List of node counts. Defaults to DEFAULT_NODE_COUNTS.
    """
    if totalNodes is None:
        totalNodes = DEFAULT_NODE_COUNTS

    print("Starting standard analysis...")
    print(f"Using {NUM_EQUIDISTANT_VALUES} samples for standard analysis")

    # Generate reliability ranges
    seriesRequiredReliabilities = generate_equidistant_list(*SERIES_RELIABILITY_RANGE, NUM_EQUIDISTANT_VALUES)
    meshRequiredReliabilities = generate_equidistant_list(*MESH_RELIABILITY_RANGE, NUM_EQUIDISTANT_VALUES)
    hybridRequiredReliabilities = generate_equidistant_list(*HYBRID_RELIABILITY_RANGE, NUM_EQUIDISTANT_VALUES)

    # Compute costs
    minimizedCosts = compute_minimized_costs_by_topology(
        totalNodes, seriesRequiredReliabilities, meshRequiredReliabilities, hybridRequiredReliabilities
    )

    # Generate plots
    plot_individual_topology_results(
        totalNodes, minimizedCosts, seriesRequiredReliabilities, meshRequiredReliabilities, hybridRequiredReliabilities, "standard"
    )
    plot_costs_comparison_joint_topologies(
        totalNodes, minimizedCosts, seriesRequiredReliabilities, meshRequiredReliabilities, hybridRequiredReliabilities, "standard"
    )
    plot_costs_comparison_by_topology(
        totalNodes, minimizedCosts, seriesRequiredReliabilities, meshRequiredReliabilities, hybridRequiredReliabilities, "standard"
    )

    print("Standard analysis completed")


def run_high_reliability_analysis(totalNodes=None):
    """
    Runs analysis focused on high reliability ranges for mesh and hybrid topologies.

    Args:
        totalNodes (list, optional): List of node counts. Defaults to DEFAULT_NODE_COUNTS.
    """
    if totalNodes is None:
        totalNodes = DEFAULT_NODE_COUNTS

    print("Starting high reliability analysis...")
    print(f"Using {NUM_HIGH_RELIABILITY_VALUES} samples for high reliability analysis (reduced for faster execution)")

    # Generate reliability ranges (standard for series, high for mesh and hybrid with reduced samples)
    seriesRequiredReliabilities = generate_equidistant_list(*SERIES_RELIABILITY_RANGE, NUM_EQUIDISTANT_VALUES)
    meshRequiredReliabilities = generate_equidistant_list(*HIGH_RELIABILITY_MESH_RANGE, NUM_HIGH_RELIABILITY_VALUES)
    hybridRequiredReliabilities = generate_equidistant_list(*HIGH_RELIABILITY_HYBRID_RANGE, NUM_HIGH_RELIABILITY_VALUES)

    # Compute costs
    minimizedCosts = compute_minimized_costs_by_topology(
        totalNodes, seriesRequiredReliabilities, meshRequiredReliabilities, hybridRequiredReliabilities
    )

    # Generate plots
    plot_individual_topology_results(
        totalNodes, minimizedCosts, seriesRequiredReliabilities, meshRequiredReliabilities, hybridRequiredReliabilities, "high_reliability"
    )
    plot_costs_comparison_by_topology(
        totalNodes, minimizedCosts, seriesRequiredReliabilities, meshRequiredReliabilities, hybridRequiredReliabilities, "high_reliability"
    )

    print("High reliability analysis completed")


def main():
    """
    Main execution function that runs both standard and high reliability analyses.
    """
    print("=" * 60)
    print("Network Reliability Optimization Analysis")
    print("=" * 60)

    # Run standard analysis
    run_standard_analysis()

    print("\n" + "=" * 60)

    # Run high reliability analysis
    run_high_reliability_analysis()

    print("\n" + "=" * 60)
    print("Analysis completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
