def input_validation(totalNodes: int, linkCost: float, reliabilityByNodeType: list | dict) -> None:
    """
    Validates input parameters for optimization models.

    Args:
        totalNodes (int): Total number of nodes in the network. Must be >= 4.
        linkCost (float): Cost of links in the network. Must be > 0.
        reliabilityByNodeType (list | dict): Reliability by node type. Must be a non-empty list or dictionary.

    Raises:
        ValueError: If any of the parameters do not meet the requirements.

    Example:
        >>> input_validation(4, 10, [0.6, 0.7, 0.8])
        >>> input_validation(5, 15, {0: 0.6, 1: 0.7, 2: 0.8})
    """
    if totalNodes < 4:
        raise ValueError(
            f"The number of nodes must be at least 4. Received: {totalNodes}")
    if linkCost <= 0:
        raise ValueError(
            f"The cost of a link must be greater than 0. Received: {linkCost}")
    if not isinstance(reliabilityByNodeType, (list, dict)) or len(reliabilityByNodeType) == 0:
        raise ValueError(
            f"reliabilityByNodeType must be a non-empty list or dictionary. Received: {type(reliabilityByNodeType)} with length {len(reliabilityByNodeType) if isinstance(reliabilityByNodeType, (list, dict)) else 'N/A'}"
        )
    if isinstance(reliabilityByNodeType, list):
        if not all(isinstance(value, (int, float)) and 0 <= value <= 1 for value in reliabilityByNodeType):
            raise ValueError(
                "All values in reliabilityByNodeType must be numbers between 0 and 1.")
    elif isinstance(reliabilityByNodeType, dict):
        if not all(isinstance(value, (int, float)) and 0 <= value <= 1 for value in reliabilityByNodeType.values()):
            raise ValueError(
                "All values in reliabilityByNodeType must be numbers between 0 and 1.")
