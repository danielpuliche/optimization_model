def validar_entrada(totalNodes, linkCost, reliabilityByNodeType):
    """
    Valida los parámetros de entrada para los modelos de optimización.

    Args:
        totalNodes (int): Número total de nodos en la red.
        linkCost (float): Costo de los enlaces en la red.
        reliabilityByNodeType (list | dict): Fiabilidad por tipo de nodo.

    Raises:
        ValueError: Si alguno de los parámetros no cumple con los requisitos.
    """
    if totalNodes < 4:
        raise ValueError("El número de nodos debe ser al menos 4.")
    if linkCost <= 0:
        raise ValueError("El costo de un enlace debe ser mayor a 0.")
    if not isinstance(reliabilityByNodeType, (list, dict)) or len(reliabilityByNodeType) == 0:
        raise ValueError("reliabilityByNodeType debe ser una lista o diccionario no vacío.")