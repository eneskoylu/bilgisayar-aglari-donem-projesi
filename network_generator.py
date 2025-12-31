import networkx as nx
import numpy as np
import random

from metrics import (
    calculate_total_delay,
    calculate_reliability_cost,
    calculate_resource_cost
)

import ga


def create_network(seed=42, N=250, p=0.4):
    random.seed(seed)
    np.random.seed(seed)

    G = nx.erdos_renyi_graph(n=N, p=p, seed=seed)

    # Eğer bağlantısızsa, bileşenleri birbirine bağlayalım
    if not nx.is_connected(G):
        components = list(nx.connected_components(G))
        for i in range(len(components) - 1):
            u = random.choice(list(components[i]))
            v = random.choice(list(components[i + 1]))
            G.add_edge(u, v)

    # Düğüm özellikleri
    for node in G.nodes():
        G.nodes[node]["processing_delay_ms"] = float(np.random.uniform(0.5, 2.0))
        G.nodes[node]["node_reliability"] = float(np.random.uniform(0.95, 0.999))

    # Kenar özellikleri
    for u, v in G.edges():
        G.edges[u, v]["bandwidth_mbps"] = float(np.random.uniform(100, 1000))
        G.edges[u, v]["link_delay_ms"] = float(np.random.uniform(3, 15))
        G.edges[u, v]["link_reliability"] = float(np.random.uniform(0.95, 0.999))

    return G


def combined_cost(u, v, data):
    """Dijkstra baseline için kenar ağırlığı."""
    return data["link_delay_ms"] + (1 / data["bandwidth_mbps"])


# ✅ Bu dosya import edilince aşağıdaki kısım çalışmaz.
# ✅ Sadece direkt çalıştırınca çalışır.
if __name__ == "__main__":
    G = create_network(seed=42, N=250, p=0.4)

    print("Ağ oluşturuldu!")
    print("Düğüm sayısı:", G.number_of_nodes())
    print("Kenar sayısı:", G.number_of_edges())

    # örnek node/edge göster
    sample_node = list(G.nodes())[0]
    sample_edge = list(G.edges())[0]

    print("\nÖrnek düğüm özellikleri:")
    print(G.nodes[sample_node])

    print("\nÖrnek kenar özellikleri:")
    print(G.edges[sample_edge])

    # TEST PATH (geçerli yol)
    source = 0
    destination = 10
    test_path = nx.shortest_path(G, source=source, target=destination)

    print("\n--- METRIC TEST ---")
    print("Path:", test_path)
    print("Total Delay:", calculate_total_delay(G, test_path))
    print("Reliability Cost:", calculate_reliability_cost(G, test_path))
    print("Resource Cost:", calculate_resource_cost(G, test_path))

    # BASELINE (Dijkstra)
    baseline_path = nx.dijkstra_path(G, source, destination, weight=combined_cost)

    print("\n--- DIJKSTRA BASELINE ---")
    print("Baseline Path:", baseline_path)
    print("Baseline Total Delay:", calculate_total_delay(G, baseline_path))
    print("Baseline Reliability Cost:", calculate_reliability_cost(G, baseline_path))
    print("Baseline Resource Cost:", calculate_resource_cost(G, baseline_path))

    # GA (eşit ağırlık)
    print("\n--- GA (GENETIC ALGORITHM) ---")
    ga_path, ga_cost = ga.run_ga(
        G,
        source=source,
        target=destination,
        generations=25,
        pop_size=30,
        elite_k=10,
        w_delay=1.0,
        w_rel=1.0,
        w_res=1.0,
        seed=42
    )

    print("GA Path:", ga_path)
    print("GA Total Delay:", calculate_total_delay(G, ga_path))
    print("GA Reliability Cost:", calculate_reliability_cost(G, ga_path))
    print("GA Resource Cost:", calculate_resource_cost(G, ga_path))
    print("GA Combined Cost:", ga_cost)

    # 3 senaryo
    print("\n--- GA SCENARIO A: DELAY-FOCUSED ---")
    ga_path, ga_cost = ga.run_ga(
        G, source=source, target=destination,
        generations=25, pop_size=30, elite_k=10,
        w_delay=1.0, w_rel=0.05, w_res=0.05,
        seed=42
    )
    print("GA Path:", ga_path)
    print("Delay:", calculate_total_delay(G, ga_path))
    print("RelCost:", calculate_reliability_cost(G, ga_path))
    print("ResCost:", calculate_resource_cost(G, ga_path))
    print("Combined:", ga_cost)

    print("\n--- GA SCENARIO B: RELIABILITY-FOCUSED ---")
    ga_path, ga_cost = ga.run_ga(
        G, source=source, target=destination,
        generations=25, pop_size=30, elite_k=10,
        w_delay=0.2, w_rel=5.0, w_res=0.2,
        seed=42
    )
    print("GA Path:", ga_path)
    print("Delay:", calculate_total_delay(G, ga_path))
    print("RelCost:", calculate_reliability_cost(G, ga_path))
    print("ResCost:", calculate_resource_cost(G, ga_path))
    print("Combined:", ga_cost)

    print("\n--- GA SCENARIO C: BANDWIDTH-FOCUSED ---")
    ga_path, ga_cost = ga.run_ga(
        G, source=source, target=destination,
        generations=25, pop_size=30, elite_k=10,
        w_delay=0.2, w_rel=0.2, w_res=20.0,
        seed=42
    )
    print("GA Path:", ga_path)
    print("Delay:", calculate_total_delay(G, ga_path))
    print("RelCost:", calculate_reliability_cost(G, ga_path))
    print("ResCost:", calculate_resource_cost(G, ga_path))
    print("Combined:", ga_cost)
