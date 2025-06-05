import pandas as pd 
import numpy as np
from oracleCIT import CitOracle
from itertools import combinations




def merge_adj(structA , structB):
    ...

def find_min_separating_set(cond_set, x_idx, y_idx, oracleCIT):
    for k in range(len(cond_set) + 1):  # Try subsets of increasing size
        for subset in combinations(cond_set, k):
            if oracleCIT.query(x_idx, y_idx, subset):
                return list(subset)  # Found minimal separating set
    return None  # No separating set found


def find_causal_cut(V_set , struct_GT , k = 150):
    nNode = struct_GT.shape[1]
    CIT = CitOracle(struct_GT)
    best_cut = {}

    best_balance = 0 
    for run in range(k):
        u = np.random.randint(low=0 , high = nNode-1)
        v = 0
        cond_nodes = []
        flag = 0
        for tmp in range(nNode) 
            if tmp == u:
                continue
            cond_nodes = list(set(range(nNode)) - {u, tmp})
            if CIT.query(u , tmp , Z = cond_nodes):
                v = tmp
                flag = 1 #found u, v that u ind v | other nodes
                break

        if flag == 0:
            continue
        
        min_subset = find_min_separating_set(cond_set=cond_nodes,x_idx = u , y_idx= v, oracleCIT=CIT)
        V1= [u]
        V2 = [v]
        C = min_subset
        # remaining_V = list(set(V_set) - set(V1) - set(V2) - set(C))
        for node in V_set:
            if node in V1 or node in V2 or node in C:
                continue
            flag1 = 1
            flag2 = 1 
            for node1 in V1:
                if find_min_separating_set(C ,node, node1 , oracleCIT = CIT) == None:
                    flag2 = 0  #node can not be in V2 
            
            for node2 in V2:
                if find_min_separating_set(C , node , node2 ,oracleCIT= CIT ) == None:
                    flag1 = 0 #node can not be in V1 

            if flag1 == 0 and flag2 ==0:
                C.append(node)
            elif flag1 == 1 and flag2==0:
                V1.append(node)
            elif flag1 == 0 and flag2 ==1:
                V2.append(node)
            else:
                print("Error in this case. Code 1")

        for s in C[:]:
            flag1 = 1 
            flag2 = 1 
            for node1 in V1:
                if find_min_separating_set(list(set(C) - {s}), node1, s , CIT) == None:
                    flag2 = 0 
            for node2 in V2:
                if find_min_separating_set(list(set(C) - {s}) , node2 , s, CIT) == None:
                    flag1 = 0 
            if flag1 == 0 and flag2 == 1:
                C.remove(s)
                V2.append(s)
            elif flag1 ==1 and flag2 == 0:
                C.remove(s)
                V1.append(s)
            elif flag1== 1 and flag2 == 1:
                print("Error in this case. Code 2")

        if best_balance < min(len(V1) , len(V2)):
            best_balance = min(len(V1) , len(V2))
            best_cut['V1'] = V1 
            best_cut['V2'] = V2
            best_cut['C'] = C


    return best_cut  

        



        

            


def SADA(data, V_set, threshold , cau ):
    ...

        