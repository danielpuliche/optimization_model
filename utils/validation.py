def validar_entrada(totalNodes: int, linkCost: float, reliabilityByNodeType: list | dict) -> None:
    """
    Valida los parámetros de entrada para los modelos de optimización.

    Args:
        totalNodes (int): Número total de nodos en la red. Debe ser >= 4.
        linkCost (float): Costo de los enlaces en la red. Debe ser > 0.
        reliabilityByNodeType (list | dict): Fiabilidad por tipo de nodo. Debe ser una lista o diccionario no vacío.

    Raises:
        ValueError: Si alguno de los parámetros no cumple con los requisitos.

    Ejemplo:
        >>> validar_entrada(4, 10, [0.6, 0.7, 0.8])
        >>> validar_entrada(5, 15, {0: 0.6, 1: 0.7, 2: 0.8})
    """
    if totalNodes < 4:
        raise ValueError(
            f"El número de nodos debe ser al menos 4. Se recibió: {totalNodes}")
    if linkCost <= 0:
        raise ValueError(
            f"El costo de un enlace debe ser mayor a 0. Se recibió: {linkCost}")
    if not isinstance(reliabilityByNodeType, (list, dict)) or len(reliabilityByNodeType) == 0:
        raise ValueError(
            f"reliabilityByNodeType debe ser una lista o diccionario no vacío. Se recibió: {type(reliabilityByNodeType)} con longitud {len(reliabilityByNodeType) if isinstance(reliabilityByNodeType, (list, dict)) else 'N/A'}"
        )
    if isinstance(reliabilityByNodeType, list):
        if not all(isinstance(value, (int, float)) and 0 <= value <= 1 for value in reliabilityByNodeType):
            raise ValueError(
                "Todos los valores en reliabilityByNodeType deben ser números entre 0 y 1.")
    elif isinstance(reliabilityByNodeType, dict):
        if not all(isinstance(value, (int, float)) and 0 <= value <= 1 for value in reliabilityByNodeType.values()):
            raise ValueError(
                "Todos los valores en reliabilityByNodeType deben ser números entre 0 y 1.")
