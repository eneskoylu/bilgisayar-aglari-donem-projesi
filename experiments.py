import random
import csv
import os
import time
import statistics as stats
import networkx as nx

import ga
import sa
from network_generator import create_network

from metrics import (
    calculate_total_delay,
    calculate_reliability_cost,
    calculate_resource_cost
)

def combined_cost(u, v, data):
    return data["link_delay_ms"] + (1 / data["bandwidth_mbps"])

def eval_path(G, path):
    return (
        calculate_total_delay(G, path),
        calculate_reliability_cost(G, path),
        calculate_resource_cost(G, path),
        len(path)
    )

def total_cost_from_metrics(delay, rel_cost, res_cost, w_delay, w_rel, w_res):
    return (w_delay * delay) + (w_rel * rel_cost) + (w_res * res_cost)

def run_experiments(
    seed=42,
    n_pairs=20,
    n_repeats=5,
    # ağırlıklar (şimdilik eşit; istersen sonra normalize ederiz)
    w_delay=1.0, w_rel=1.0, w_res=1.0,
    # B: talep edilen bant genişliği (Mbps) -> örnek olarak 100-1000 arası seçiyoruz
    b_min=100, b_max=1000,
    out_csv="results/results_summary.csv"
):
    random.seed(seed)

    G = create_network(seed=seed, N=250, p=0.4)
    nodes = list(G.nodes())

    # 20 farklı (S,D,B) üret
    samples = []
    seen = set()
    while len(samples) < n_pairs:
        s, d = random.sample(nodes, 2)
        B = random.randint(b_min, b_max)  # Mbps
        key = (s, d, B)
        if key in seen:
            continue
        try:
            nx.shortest_path(G, s, d)
            samples.append((s, d, B))
            seen.add(key)
        except nx.NetworkXNoPath:
            continue

    os.makedirs(os.path.dirname(out_csv), exist_ok=True)

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "sample_id", "source", "dest", "B_mbps",
                "algo",
                "mean_total_cost", "std_total_cost", "best_total_cost", "worst_total_cost",
                "mean_delay", "std_delay",
                "mean_rel_cost", "std_rel_cost",
                "mean_res_cost", "std_res_cost",
                "mean_path_len", "std_path_len",
                "mean_runtime_ms", "std_runtime_ms"
            ]
        )
        writer.writeheader()

        for idx, (s, d, B) in enumerate(samples, start=1):
            # Not: B'yi şu an “raporluyoruz”. İstersen bir sonraki adımda
            # B'yi constraint olarak ekleyip (bandwidth >= B) filtreleyeceğiz.

            algos = ["baseline", "ga", "sa"]
            for algo in algos:
                costs = []
                delays = []
                rels = []
                ress = []
                lens = []
                runtimes = []

                for rep in range(n_repeats):
                    rep_seed = seed + rep + 1000*idx

                    t0 = time.perf_counter()

                    if algo == "baseline":
                        path = nx.dijkstra_path(G, s, d, weight=combined_cost)
                        ga_cost = None

                    elif algo == "ga":
                        path, ga_cost = ga.run_ga(
                            G, source=s, target=d,
                            generations=25, pop_size=30, elite_k=10,
                            w_delay=w_delay, w_rel=w_rel, w_res=w_res,
                            seed=rep_seed
                        )

                    elif algo == "sa":
                        path, sa_cost = sa.run_sa(
                            G, source=s, target=d,
                            w_delay=w_delay, w_rel=w_rel, w_res=w_res,
                            max_iter=400, T0=5.0, alpha=0.995,
                            seed=rep_seed
                        )

                    t1 = time.perf_counter()

                    delay, rel_cost, res_cost, plen = eval_path(G, path)
                    total_c = total_cost_from_metrics(delay, rel_cost, res_cost, w_delay, w_rel, w_res)

                    costs.append(total_c)
                    delays.append(delay)
                    rels.append(rel_cost)
                    ress.append(res_cost)
                    lens.append(plen)
                    runtimes.append((t1 - t0) * 1000.0)  # ms

                def mean_std(arr):
                    return (stats.mean(arr), stats.pstdev(arr) if len(arr) > 1 else 0.0)

                m_cost, s_cost = mean_std(costs)
                m_d, s_d = mean_std(delays)
                m_r, s_r = mean_std(rels)
                m_res, s_res = mean_std(ress)
                m_len, s_len = mean_std(lens)
                m_rt, s_rt = mean_std(runtimes)

                writer.writerow({
                    "sample_id": idx,
                    "source": s,
                    "dest": d,
                    "B_mbps": B,
                    "algo": algo,
                    "mean_total_cost": m_cost,
                    "std_total_cost": s_cost,
                    "best_total_cost": min(costs),
                    "worst_total_cost": max(costs),
                    "mean_delay": m_d,
                    "std_delay": s_d,
                    "mean_rel_cost": m_r,
                    "std_rel_cost": s_r,
                    "mean_res_cost": m_res,
                    "std_res_cost": s_res,
                    "mean_path_len": m_len,
                    "std_path_len": s_len,
                    "mean_runtime_ms": m_rt,
                    "std_runtime_ms": s_rt
                })

    print(f"✅ Summary CSV yazıldı: {out_csv}")

if __name__ == "__main__":
    run_experiments(
        seed=42,
        n_pairs=20,
        n_repeats=5,
        w_delay=1.0, w_rel=1.0, w_res=1.0,
        out_csv="results/results_summary.csv"
    )
