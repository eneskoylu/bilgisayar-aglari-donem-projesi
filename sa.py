import random
import math
import networkx as nx

from metrics import (
    calculate_total_delay,
    calculate_reliability_cost,
    calculate_resource_cost
)

def total_cost(G, path, w_delay=1.0, w_rel=1.0, w_res=1.0):
    d = calculate_total_delay(G, path)
    r = calculate_reliability_cost(G, path)
    c = calculate_resource_cost(G, path)
    return (w_delay * d) + (w_rel * r) + (w_res * c)

def neighbor_path(G, path):
    """
    Komşu çözüm üretimi (güvenli):
    - Yolun içinden (S ve D hariç) bir düğüm seç
    - O düğümden D'ye yeni bir shortest_path ile devam et
    """
    if len(path) <= 2:
        return path

    cut = random.randint(1, len(path) - 2)  # içten kes
    prefix = path[:cut]
    cut_node = path[cut]
    target = path[-1]

    try:
        tail = nx.shortest_path(G, source=cut_node, target=target)
        new_path = prefix + tail  # cut_node tekrar eder, prefix cut_node içermez
        # döngü olmasın
        if len(new_path) == len(set(new_path)):
            return new_path
        return path
    except nx.NetworkXNoPath:
        return path

def run_sa(G, source, target,
           w_delay=1.0, w_rel=1.0, w_res=1.0,
           max_iter=400, T0=5.0, alpha=0.995, seed=42):
    """
    Simulated Annealing:
    - Başlangıç: shortest_path
    - Komşu: neighbor_path
    - Kabul: e^(-(Δcost)/T)
    """
    random.seed(seed)

    # başlangıç çözümü
    current = nx.shortest_path(G, source=source, target=target)
    current_cost = total_cost(G, current, w_delay, w_rel, w_res)

    best = current
    best_cost = current_cost

    T = T0

    for _ in range(max_iter):
        cand = neighbor_path(G, current)
        cand_cost = total_cost(G, cand, w_delay, w_rel, w_res)

        delta = cand_cost - current_cost

        # Daha iyiyse kabul
        if delta <= 0:
            current, current_cost = cand, cand_cost
        else:
            # Daha kötüyse belirli olasılıkla kabul
            prob = math.exp(-delta / max(T, 1e-9))
            if random.random() < prob:
                current, current_cost = cand, cand_cost

        # En iyiyi güncelle
        if current_cost < best_cost:
            best, best_cost = current, current_cost

        # soğutma
        T *= alpha

    return best, best_cost
