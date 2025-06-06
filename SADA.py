import pandas as pd 
import numpy as np
from oracleCIT import CitOracle
from itertools import combinations
from castle.algorithms import PC
from combine import vertical_data_seperation , count_accuracy, reformat_causal_graph
from causallearn.utils.cit import CIT
import random 
import networkx as nx
from causallearn.search.ConstraintBased.PC import pc
import os
# os.environ['CASTLE_BACKEND'] = backend


def find_all_paths_exclude_direct(v1, v2, edge_list):
    from collections import defaultdict

    # Build adjacency list
    graph = defaultdict(list)
    for u, v in edge_list:
        if not (u == v1 and v == v2):  # Exclude direct edge
            graph[u].append(v)

    all_paths = []

    def dfs(current, path, visited):
        if current == v2:
            all_paths.append(path[:])
            return
        visited.add(current)
        for neighbor in graph[current]:
            if neighbor not in visited:
                path.append(neighbor)
                dfs(neighbor, path, visited)
                path.pop()
        visited.remove(current)

    dfs(v1, [v1], set())
    return all_paths


# def merge_adj(structA , structB , struct_GT , CIT):
#     # nNode = struct_GT.shape[0]
#     edge_list = {}
#     oracle = CitOracle(struct_GT)
    
    
#     for edge in structA:
#         edge_list[(edge[0] , edge[1])] = CIT(X = edge[0] , Y = edge[1] , condition_set = [])
#     for edge in structB:
#         edge_list[(edge[0] , edge[1])] = CIT(X = edge[0] , Y = edge[1] , condition_set = [])
    
#     sorted_edges = sorted(edge_list.items(), key=lambda item: item[1], reverse=True)
#     reachable = {}
#     for egde in sorted_edges:
#         reachable[egde] = False 
#     for edge in sorted_edges:
#         if reachable[edge]:
#             sorted_edges.remove(edge)
#         else:
#             reachable[edge] = True 
#     for edge in sorted_edges:
#         all_path = find_all_paths_exclude_direct(edge[0] , edge[1] , sorted_edges)
#         if len(all_path)!= 0 :
#             for path in all_path:
#                 cond_set = path.remove(edge[0], edge[1])
#                 if find_min_separating_set(cond_set= cond_set , x_idx= edge[0] , y_idx= edge[1] , oracleCIT= oracle)!= None:
#                     sorted_edges.remove(edge)  
#     return sorted_edges

# def merge_adj(structA, structB, struct_GT, CIT):
#     oracle = CitOracle(struct_GT)
#     edge_list = {}

#     # Combine edges and assign CIT score
#     for edge in structA + structB:
#         edge_list[(edge[0], edge[1])] = CIT(X=edge[0], Y=edge[1], condition_set=[])

#     # Sort edges by CIT score descending
#     sorted_edges = sorted(edge_list.items(), key=lambda item: item[1], reverse=True)
#     edge_keys = [edge[0] for edge in sorted_edges]  # list of (u,v)

#     # Filter redundant edges
#     final_edges = []
#     for u, v in edge_keys:
#         all_paths = find_all_paths_exclude_direct(u, v, edge_keys)
#         is_redundant = False
#         for path in all_paths:
#             cond_set = [node for node in path if node != u and node != v]
#             if find_min_separating_set(cond_set, x_idx=u, y_idx=v, oracleCIT=oracle) is not None:
#                 is_redundant = True
#                 break
#         if not is_redundant:
#             final_edges.append((u, v))

#     return final_edges
        

def merge_adj(structA, structB, struct_GT, CIT):
    oracle = CitOracle(struct_GT)

    # Step 1: Combine and score edges
    edge_scores = {}
    for edge in structA + structB:
        score = CIT(X=edge[0], Y=edge[1], condition_set=[])
        edge_scores[(edge[0], edge[1])] = score

    sorted_edges = sorted(edge_scores.items(), key=lambda x: x[1], reverse=True)
    candidate_edges = [e[0] for e in sorted_edges]

    # Step 2: Build DAG incrementally, avoiding cycles
    G = nx.DiGraph()
    for (u, v) in candidate_edges:
        G.add_edge(u, v)
        if not nx.is_directed_acyclic_graph(G):  # Cycle introduced
            G.remove_edge(u, v)  # Revert
            continue

    final_edges = list(G.edges)

    # Step 3: Remove conditionally independent redundant edges
    result_edges = final_edges[:]
    for (u, v) in final_edges:
        alt_paths = find_all_paths_exclude_direct(u, v, final_edges)
        for path in alt_paths:
            cond_set = [n for n in path if n != u and n != v]
            if find_min_separating_set(cond_set, x_idx=u, y_idx=v, oracleCIT=oracle) is not None:
                result_edges.remove((u, v))
                break

    return result_edges
       
        
        
        
    
def find_min_separating_set(cond_set, x_idx, y_idx, oracleCIT):
    cond_set = sorted(cond_set)
    for k in range(4):  # Try subsets of increasing size
        for subset in combinations(cond_set, k):
            if oracleCIT.query(x_idx, y_idx, subset):
                return list(subset)  # Found minimal separating set
    return None  # No separating set found


def find_causal_cut(V_set , struct_GT , k = 50):
    CIT = CitOracle(struct_GT)
    V_set = sorted(V_set)
    best_balance = 0 
    best_V1 = []
    best_V2 = []
    best_C = []
    for _ in range(k):
        
        flag = 0
        all_pairs = list(combinations(V_set , 2))
        random.shuffle(all_pairs)
        for u, v in all_pairs:
            if CIT.query(u , v , Z = list(set(V_set) - {u,v})):
                cond_nodes = list(set(V_set) - {u,v})
                flag =1 
                break

        if flag == 0:
            continue
        
        min_subset = find_min_separating_set(cond_set=cond_nodes,x_idx = u , y_idx= v, oracleCIT=CIT)
        
        if min_subset is None:
            print("None in min subset")
            continue
        
        V1 = [u]
        V2 = [v]
        C = min_subset
        
        print(V1 , V2 , C, CIT.query(u , v , Z = C))
        remaining_V = list(set(V_set) - set(V1) - set(V2) - set(C))
        for node in remaining_V:
            flag1 = 1
            flag2 = 1 
            for node1 in V1:
                if find_min_separating_set(C ,node, node1 , oracleCIT = CIT) is None:
                    flag2 = 0  #node can not be in V2 
            
            for node2 in V2:
                if find_min_separating_set(C , node , node2 ,oracleCIT= CIT ) is None:
                    flag1 = 0 #node can not be in V1 

            
            if flag1 == 1 and flag2 == 0:
                V1.append(node)
            elif flag1 == 0 and flag2 == 1:
                V2.append(node)
            else:
                C.append(node)

        for s in C[:]:
            flag1 = 1 
            flag2 = 1 
            for node1 in V1:
                if find_min_separating_set(list(set(C) - {s}), node1, s , CIT) is None:
                    flag2 = 0 
            for node2 in V2:
                if find_min_separating_set(list(set(C) - {s}) , node2 , s, CIT) is None:
                    flag1 = 0 
            if flag1 == 0 and flag2 == 1:
                C.remove(s)
                V2.append(s)
            elif flag1 == 1 and flag2 == 0:
                C.remove(s)
                V1.append(s)

        if best_balance < min(len(V1) , len(V2)):
            best_balance = min(len(V1) , len(V2))
            best_V1 = V1 
            best_V2 = V2 
            best_C = C
            print(f"best cut {V1} , {V2} , {C}")


    return best_V1 , best_V2 , best_C

        



        

def extract_edge(cg_graph, V_set):
    edge_list = []
    adj_mtx = cg_graph.G.graph
    for i in range(adj_mtx.shape[0]):
        for j in range(adj_mtx.shape[1]):
            if adj_mtx[i, j] == 1 and adj_mtx[j, i] == 0:
                edge_list.append((V_set[i], V_set[j]))
            elif adj_mtx[i,j] == -1:
                edge_list.append((V_set[i],V_set[j]))
                edge_list.append((V_set[j],V_set[i]))
                
    return edge_list


def SADA(dataset, V_set, stru_GT, options):
    
    if options['datatype'] == 'continuous':
        ci_test = 'fisherz'
        CoInT = CIT(data = dataset.to_numpy() , method = 'fisherz')
    elif options['datatype'] == 'discrete':
        ci_test = 'chi2'
        CoInT = CIT(data = dataset.to_numpy() , method = 'chi2')
    if len(V_set) == 0:
        return []
    if len(V_set) < options['threshold']:
        data = vertical_data_seperation(data_df = dataset , node_idx= V_set)
        print(V_set)
        print(dataset.columns)
        cg = pc(data=data.to_numpy(), alpha=0.3, indep_test= ci_test)
        # adj_mtx, _ = reformat_causal_graph(cg)
        # print(count_accuracy(B_true= stru_GT , B_est = adj_mtx))
        edge_list = extract_edge(cg , V_set=V_set)
        return edge_list
                
    
    
    V1, V2, C = find_causal_cut(V_set = V_set , struct_GT=stru_GT) 
    
    edge_list_1 = SADA(dataset=dataset, V_set= V1 + C, stru_GT=stru_GT, options = options)
    edge_list_2 = SADA(dataset= dataset , V_set = V2 + C , stru_GT= stru_GT , options = options) 
    
    return merge_adj(structA=edge_list_1, structB=edge_list_2, struct_GT=stru_GT , CIT = CoInT)

        
        
