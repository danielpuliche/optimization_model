from Modelos.base_model import base_model
from Modelos.serie_model import serie_model
from Modelos.parallel_model import parallel_model
from Modelos.hybrid_model import hybrid_model
from utils.utils import *
from config import *

# Generate the required reliabilities
minReliability = 0.999
maxReliability = MAX_RELIABILITY

seriesRequiredReliabilities = generate_equidistant_list(0, MAX_RELIABILITY, NUM_EQUIDISTANT_VALUES)
parallelRequiredReliabilities = generate_equidistant_list(minReliability, maxReliability, NUM_EQUIDISTANT_VALUES)
hybridRequiredReliabilities = generate_equidistant_list(minReliability, maxReliability, NUM_EQUIDISTANT_VALUES)

def calcular_combinaciones_confLineal(totalNodes):

    diccionarioResultados = {}

    for n in totalNodes:
        baseModel = base_model(n)

        serieMinimizedCosts = []
        parallelMinimizedCosts = []
        hybridMinimizedCosts = []

        print("Iniciando calculos")

        for reqRel in seriesRequiredReliabilities:
            serieMinCost, _, _ = serie_model(baseModel, n, reqRel)
            serieMinimizedCosts.append(serieMinCost)
        print(f"Calculo de costos minimizados para {n} nodos en serie terminado")

        for reqRel in parallelRequiredReliabilities:
            parallelMinCost, _, _ = parallel_model(baseModel, n, reqRel)
            parallelMinimizedCosts.append(parallelMinCost)
        print(f"Calculo de costos minimizados para {n} nodos en paralelo terminado")

        for reqRel in hybridRequiredReliabilities:
            hybridMinCost, _, _ = hybrid_model(baseModel, n, reqRel)
            hybridMinimizedCosts.append(hybridMinCost)
        print(f"Calculo de costos minimizados para {n} nodos en hibrido terminado")

        diccionarioResultados[f"nodos_{n}_serie"] = serieMinimizedCosts
        diccionarioResultados[f"nodos_{n}_paralelo"] = parallelMinimizedCosts
        diccionarioResultados[f"nodos_{n}_hibrido"] = hybridMinimizedCosts

    return diccionarioResultados

def graficar_costosVsConfiabilidad(totalNodes):
    try:
        # Calculate the minimized costs for each topology
        minimizedCosts = calcular_combinaciones_confLineal(totalNodes)

        for n in totalNodes:
            serieMinimizedCosts = minimizedCosts[f"nodos_{n}_serie"]
            parallelMinimizedCosts = minimizedCosts[f"nodos_{n}_paralelo"]
            hybridMinimizedCosts = minimizedCosts[f"nodos_{n}_hibrido"]

            # Plot the results
            graficar_costos_minimizados(seriesRequiredReliabilities, serieMinimizedCosts, "Series", n)
            graficar_costos_minimizados(parallelRequiredReliabilities, parallelMinimizedCosts, "Parallel", n)
            graficar_costos_minimizados(hybridRequiredReliabilities, hybridMinimizedCosts, "Hybrid", n)

        print("Graficado exitoso")
    except Exception as e:
        print(f"Error: {e}")

# def graficar_costosVsConfiabilidad_topologiasJuntas(totalNodes):
#     try

graficar_costosVsConfiabilidad(totalNodes=[5,6,11])