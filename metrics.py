import math

def calculate_total_delay(G, path):
    total_delay = 0.0

    for node in path:
        total_delay += G.nodes[node]['processing_delay_ms']

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        total_delay += G.edges[u, v]['link_delay_ms']

    return total_delay


def calculate_reliability_cost(G, path):
    reliability_product = 1.0

    for node in path:
        reliability_product *= G.nodes[node]['node_reliability']

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        reliability_product *= G.edges[u, v]['link_reliability']

    return -math.log(reliability_product)


def calculate_resource_cost(G, path):
    resource_cost = 0.0

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        bandwidth = G.edges[u, v]['bandwidth_mbps']
        resource_cost += 1 / bandwidth

    return resource_cost
