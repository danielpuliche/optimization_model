from Modelos.base_model import base_model
from Modelos.serie_model import serie_model
from Modelos.parallel_model import parallel_model
from Modelos.hybrid_model import hybrid_model
from utils.utils import *
from config import *


def calcular_combinaciones_confLineal(totalNodes, seriesRequiredReliabilities, parallelRequiredReliabilities, hybridRequiredReliabilities):

    diccionarioResultados = {}

    for n in totalNodes:
        baseModel = base_model(n)

        serieMinimizedCosts = []
        parallelMinimizedCosts = []
        hybridMinimizedCosts = []

        for reqRel in seriesRequiredReliabilities:
            serieMinCost, _, _ = serie_model(baseModel, n, reqRel)
            serieMinimizedCosts.append(serieMinCost)
        print(
            f"Calculo de costos minimizados para {n} nodos en serie terminado")

        for reqRel in parallelRequiredReliabilities:
            parallelMinCost, _, _ = parallel_model(baseModel, n, reqRel)
            parallelMinimizedCosts.append(parallelMinCost)
        print(
            f"Calculo de costos minimizados para {n} nodos en paralelo terminado")

        for reqRel in hybridRequiredReliabilities:
            hybridMinCost, _, _ = hybrid_model(baseModel, n, reqRel)
            hybridMinimizedCosts.append(hybridMinCost)
        print(
            f"Calculo de costos minimizados para {n} nodos en hibrido terminado")

        diccionarioResultados[f"nodos_{n}_serie"] = serieMinimizedCosts
        diccionarioResultados[f"nodos_{n}_paralelo"] = parallelMinimizedCosts
        diccionarioResultados[f"nodos_{n}_hibrido"] = hybridMinimizedCosts

    return diccionarioResultados


def graficar_costosVsConfiabilidad(totalNodes, minimizedCosts, seriesRequiredReliabilities, parallelRequiredReliabilities, hybridRequiredReliabilities):
    try:
        for n in totalNodes:
            serieMinimizedCosts = minimizedCosts[f"nodos_{n}_serie"]
            parallelMinimizedCosts = minimizedCosts[f"nodos_{n}_paralelo"]
            hybridMinimizedCosts = minimizedCosts[f"nodos_{n}_hibrido"]

            # Plot the results
            graficar_costos_minimizados(
                seriesRequiredReliabilities, serieMinimizedCosts, "Series", n)
            graficar_costos_minimizados(
                parallelRequiredReliabilities, parallelMinimizedCosts, "Parallel", n)
            graficar_costos_minimizados(
                hybridRequiredReliabilities, hybridMinimizedCosts, "Hybrid", n)

        print("Graficado exitoso")
    except Exception as e:
        print(f"Error: {e}")


def graficar_costosVsConfiabilidad_topologiasJuntas(totalNodes, minimizedCosts, seriesRequiredReliabilities, parallelRequiredReliabilities, hybridRequiredReliabilities):

    print("Grafica de costos vs confiabilidad para topologias juntas")

    for n in totalNodes:
        serieMinimizedCosts = minimizedCosts[f"nodos_{n}_serie"]
        parallelMinimizedCosts = minimizedCosts[f"nodos_{n}_paralelo"]
        hybridMinimizedCosts = minimizedCosts[f"nodos_{n}_hibrido"]

        # Plot the results on the same graph
        plt.figure(figsize=(10, 6))
        plt.plot(seriesRequiredReliabilities, serieMinimizedCosts,
                 label='Serie', color='blue', linestyle='-', marker='.')
        plt.plot(parallelRequiredReliabilities, parallelMinimizedCosts,
                 label='Paralelo', color='red', linestyle='-', marker='.')
        plt.plot(hybridRequiredReliabilities, hybridMinimizedCosts,
                 label='Hibrido', color='green', linestyle='-', marker='.')
        plt.title(
            f'Minimized Costs vs Required Reliability - Topology Comparation - {n} Nodes')
        plt.xlabel('Required Reliability')
        plt.ylabel('Minimized Costs')
        plt.grid(True)

        # Añadir etiquetas para el último y primer valor no nulo de cada grupo
        for reliabilities, costs, color in zip(
            [seriesRequiredReliabilities, parallelRequiredReliabilities,
                hybridRequiredReliabilities],
            [serieMinimizedCosts, parallelMinimizedCosts, hybridMinimizedCosts],
            ['blue', 'orange', 'green']
        ):
            # Último valor no nulo
            for x, y in reversed(list(zip(reliabilities, costs))):
                if y is not None:
                    plt.text(x, y, f"({x:.2f}, {y:.2f})",
                             fontsize=8, color=color, ha='right')
                    break

            # Primer valor no nulo
            for x, y in zip(reliabilities, costs):
                if y is not None:
                    plt.text(x, y, f"({x:.2f}, {y:.2f})",
                             fontsize=8, color=color, ha='left')
                    break

        # Agregar leyenda para identificar cada grupo
        plt.legend(loc='upper left')

        directory = f"graficas/topologiasJuntas/"
        fileName = f"costVsReliability_Nodos{n}.png"

        if not os.path.exists(directory):
            os.makedirs(directory)

        plt.savefig(os.path.join(directory, fileName))

        print(f"Grafica para {n} nodos guardada")

# Grafica Número de nodos juntos


def graficar_costosVsConfiabilidad_porTopologia(totalNodes, minimizedCosts,
                                                seriesRequiredReliabilities,
                                                parallelRequiredReliabilities,
                                                hybridRequiredReliabilities):
    print("Graficando costos vs confiabilidad por topología...")

    topologias = [
        ("Serie", "serie", seriesRequiredReliabilities, 'blue'),
        ("Parallel", "paralelo", parallelRequiredReliabilities, 'orange'),
        ("Hybrid", "hibrido", hybridRequiredReliabilities, 'green')
    ]

    for titulo, key, reliabilities, color_base in topologias:
        plt.figure(figsize=(10, 6))
        colores = ['blue', 'red', 'green']  # Un color por cada línea/nodos

        for i, n in enumerate(totalNodes):
            costos = minimizedCosts[f"nodos_{n}_{key}"]
            plt.plot(reliabilities, costos, label=f'{n} Nodos',
                     color=colores[i], linestyle='-', marker='.')

            # Etiqueta del primer valor no nulo
            for x, y in zip(reliabilities, costos):
                if y is not None:
                    plt.text(x, y, f"({x:.2f}, {y:.2f})", fontsize=8,
                             color=colores[i], ha='left')
                    break

            # Etiqueta del último valor no nulo
            for x, y in reversed(list(zip(reliabilities, costos))):
                if y is not None:
                    plt.text(x, y, f"({x:.2f}, {y:.2f})", fontsize=8,
                             color=colores[i], ha='right')
                    break

        # Configuración visual
        plt.title(
            f'Minimized Costs vs Required Reliability - Nodes Number Comparation - {titulo} Topology')
        plt.xlabel('Required Reliability')
        plt.ylabel('Minimized Costs')
        plt.grid(True)
        plt.legend(loc='upper left')

        # Guardado de la gráfica
        directory = f"graficas/NodosJuntosPorTopologia/{key}/"
        fileName = f"costVsReliability_{key}.png"

        if not os.path.exists(directory):
            os.makedirs(directory)

        plt.savefig(os.path.join(directory, fileName))
        plt.close()

        print(f"Gráfica de topología {titulo} guardada")


# grafica de zoom
def graficar_costos_zoom_hibrido_paralelo(totalNodes, minimizedCosts,
                                          parallelRequiredReliabilities,
                                          hybridRequiredReliabilities):
    print("Graficando zoom para topologías Híbrido y Paralelo...")

    topologias = [
        ("Híbrido", "hibrido", hybridRequiredReliabilities, (0.90, 1.00)),
        ("Paralelo", "paralelo", parallelRequiredReliabilities, (0.90, 1.00))
    ]

    for titulo, key, reliabilidades, (x_min, x_max) in topologias:
        plt.figure(figsize=(10, 6))
        colores = ['blue', 'red', 'green']

        for i, n in enumerate(totalNodes):
            costos = minimizedCosts[f"nodos_{n}_{key}"]
            plt.plot(reliabilidades, costos, label=f'{n} Nodos',
                     color=colores[i], linestyle='-', marker='.')

            # Etiqueta del primer valor no nulo
            for x, y in zip(reliabilidades, costos):
                if y is not None:
                    plt.text(x, y, f"({x:.2f}, {y:.2f})", fontsize=8,
                             color=colores[i], ha='left')
                    break

            # Etiqueta del último valor no nulo
            for x, y in reversed(list(zip(reliabilidades, costos))):
                if y is not None:
                    plt.text(x, y, f"({x:.2f}, {y:.2f})", fontsize=8,
                             color=colores[i], ha='right')
                    break

        plt.title(
            f'Minimized Costs vs Required Reliability - Zoom - Topología {titulo}')
        plt.xlabel('Required Reliability')
        plt.ylabel('Minimized Costs')
        plt.grid(True)
        plt.legend(loc='upper left')
        plt.xlim(x_min, x_max)

        # Guardado
        directory = f"graficas/NodosJuntosPorTopologia/{key}/"
        fileName = f"costVsReliability_{key}_zoom.png"

        if not os.path.exists(directory):
            os.makedirs(directory)

        plt.savefig(os.path.join(directory, fileName))
        plt.close()

        print(f"Gráfica con zoom para {titulo} guardada")


# Ejecución
minReliability = 0.999
totalNodes = [5, 6, 11]

seriesRequiredReliabilities = generate_equidistant_list(
    0.5, MAX_RELIABILITY, NUM_EQUIDISTANT_VALUES)
parallelRequiredReliabilities = generate_equidistant_list(
    0.5, MAX_RELIABILITY, NUM_EQUIDISTANT_VALUES)
hybridRequiredReliabilities = generate_equidistant_list(
    0.5, MAX_RELIABILITY, NUM_EQUIDISTANT_VALUES)

minimizedCosts = calcular_combinaciones_confLineal(
    totalNodes, seriesRequiredReliabilities, parallelRequiredReliabilities, hybridRequiredReliabilities)
graficar_costosVsConfiabilidad(totalNodes, minimizedCosts, seriesRequiredReliabilities,
                               parallelRequiredReliabilities, hybridRequiredReliabilities)
graficar_costosVsConfiabilidad_topologiasJuntas(
    totalNodes, minimizedCosts, seriesRequiredReliabilities, parallelRequiredReliabilities, hybridRequiredReliabilities)
graficar_costosVsConfiabilidad_porTopologia(
    totalNodes, minimizedCosts, seriesRequiredReliabilities, parallelRequiredReliabilities, hybridRequiredReliabilities)
graficar_costos_zoom_hibrido_paralelo(
    totalNodes, minimizedCosts, parallelRequiredReliabilities, hybridRequiredReliabilities)
print("Fin del programa")
