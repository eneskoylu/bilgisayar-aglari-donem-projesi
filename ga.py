import random
import networkx as nx

from metrics import (
    calculate_total_delay,
    calculate_reliability_cost,
    calculate_resource_cost
)

def total_cost(G, path, w_delay=1.0, w_rel=1.0, w_res=1.0):
    """3 metriği ağırlıklı toplar (küçük daha iyi)."""
    d = calculate_total_delay(G, path)
    r = calculate_reliability_cost(G, path)
    c = calculate_resource_cost(G, path)
    return (w_delay * d) + (w_rel * r) + (w_res * c)

def generate_initial_population(G, source, target, pop_size=30, k_paths=60, seed=42):
    """
    GA için başlangıç popülasyonu: geçerli yollar.
    - shortest_simple_paths ile farklı basit yollar üretip ilk popülasyonu doldurur.
    """
    random.seed(seed)

    population = []
    seen = set()

    # Ağırlıksız kısayol jeneratörü (basit yollar)
    # Not: Yoğun graf için hız iyi olur; k_paths çok büyütmeyelim.
    paths_gen = nx.shortest_simple_paths(G, source=source, target=target)

    for _ in range(k_paths):
        try:
            p = next(paths_gen)
        except StopIteration:
            break

        t = tuple(p)
        if t not in seen:
            population.append(p)
            seen.add(t)
        if len(population) >= pop_size:
            break

    # Eğer yetmediyse: rastgele ara hedef üzerinden path bulup doldur
    while len(population) < pop_size:
        mid = random.choice(list(G.nodes()))
        try:
            p1 = nx.shortest_path(G, source=source, target=mid)
            p2 = nx.shortest_path(G, source=mid, target=target)
            p = p1[:-1] + p2  # mid tekrarlanmasın
            t = tuple(p)
            if t not in seen:
                population.append(p)
                seen.add(t)
        except nx.NetworkXNoPath:
            continue

    return population

def select_top_k(G, population, k=10, w_delay=1.0, w_rel=1.0, w_res=1.0):
    """En düşük maliyetli k path'i seçer."""
    scored = [(total_cost(G, p, w_delay, w_rel, w_res), p) for p in population]
    scored.sort(key=lambda x: x[0])
    return [p for _, p in scored[:k]], scored[:k]

def crossover_paths(p1, p2, source, target):
    """
    Güvenli crossover:
    - Ortak bir düğüm bul
    - source->common kısmını p1'den, common->target kısmını p2'den al
    """
    set1 = set(p1[1:-1])
    set2 = set(p2[1:-1])
    common = list(set1.intersection(set2))
    if not common:
        return None

    pivot = random.choice(common)

    i1 = p1.index(pivot)
    i2 = p2.index(pivot)

    child = p1[:i1] + p2[i2:]  # pivot dahil, hedef dahil

    # Basit kontrol: source ve target doğru mu?
    if child[0] != source or child[-1] != target:
        return None

    # Döngü (tekrarlı node) olmasın diye basit kontrol
    if len(child) != len(set(child)):
        return None

    return child

def mutate_path(G, path, mutation_rate=0.2):
    """
    Güvenli mutasyon:
    - Path içinden (source/target hariç) bir düğüm seç
    - O düğümden target'a yeni shortest_path ile devam et
    """
    if random.random() > mutation_rate:
        return path

    if len(path) <= 2:
        return path

    cut_idx = random.randint(1, len(path) - 2)  # içten bir nokta
    prefix = path[:cut_idx]
    cut_node = path[cut_idx]

    try:
        new_tail = nx.shortest_path(G, source=cut_node, target=path[-1])
        mutated = prefix + new_tail  # cut_node tekrar eder; prefix cut_node içermez
        # Döngü kontrol
        if len(mutated) != len(set(mutated)):
            return path
        return mutated
    except nx.NetworkXNoPath:
        return path

def run_ga(G, source, target, generations=30, pop_size=30, elite_k=10,
           w_delay=1.0, w_rel=1.0, w_res=1.0, seed=42):
    random.seed(seed)

    population = generate_initial_population(G, source, target, pop_size=pop_size, seed=seed)

    best_path = None
    best_cost = float("inf")

    for gen in range(generations):
        elites, scored_elites = select_top_k(G, population, k=elite_k, w_delay=w_delay, w_rel=w_rel, w_res=w_res)

        # En iyiyi güncelle
        if scored_elites[0][0] < best_cost:
            best_cost = scored_elites[0][0]
            best_path = scored_elites[0][1]

        # Yeni popülasyon: elitleri koru
        new_population = elites[:]

        # Kalanı üret
        while len(new_population) < pop_size:
            p1, p2 = random.sample(elites, 2)
            child = crossover_paths(p1, p2, source, target)
            if child is None:
                # crossover olmazsa ebeveynlerden birini kopyala
                child = random.choice([p1, p2])

            child = mutate_path(G, child, mutation_rate=0.25)
            new_population.append(child)

        population = new_population

    return best_path, best_cost
if __name__ == "__main__":
    print("ga.py OK - run_ga exists:", callable(run_ga))
