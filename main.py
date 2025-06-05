import time 
import numpy as np 
import pandas as pd 
import argparse
from combine import Plus_PC
import os 
from PC import PC



Algorithm = ['CPA' , 'SADA' , 'CAPA' , 'HCD']



def read_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument("--algorithm" , type=str, default="CPA" , choices=["CPA" , "CAPA" , "SADA" , "HCD"])
    parser.add_argument("--data_path", type=str, default="data.csv") # Must have headers
    parser.add_argument("--groundtruth_path", type=str, default="graph.csv") # Must have headers, same as the one above
    parser.add_argument("--output", type=str, default="res.csv")
    parser.add_argument("--datatype", type=str, default="continuous", choices=["continuous", "discrete"])
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--routine", type=str, choices=["PC", "GES", "GIES", 
                                                            "Notears", "NotearsNonlinear", "NotearsLowRank", "GOLEM",
                                                            "DAS", "SCORE",
                                                            "Varsort", "R2sort",
                                                            "ICALiNGAM", "DirectLiNGAM",
                                                            "GraNDAG"], default="PC")
    
    parser.add_argument("--groundtruth_dir" , type= str , default= './data/andes')
    parser.add_argument("--maxCset", type=int, default= 3) 
    
    options = vars(parser.parse_args())
    return options


def read_groundtruth(data_dir):

    data = pd.read_csv(f"{os.path.join(data_dir , 'graph.csv')}")
    stru_GT = pd.read_csv(f"{os.path.join(data_dir) , 'data.csv'}").to_numpy()
    return data, stru_GT


def categorize_data(data):
    ...
    return data 


if __name__ == "__main__":

    options = read_opts()
    results = {}
    results[f'{options["algorithm"]}'] = []
    for i in range(10):
        data_dir = options['groundtruth_folder']
        data_dir = os.path.join(data_dir, str(i))
        data , stru_GT = read_groundtruth(data_dir=data_dir)

        if options['datatype'] == 'discrete':
            data = categorize_data(data)


        # Run PC to get the skeleton of data, then pass the skeleton into each partition algorithm
        # pc_start = time.time()
        # pc = PC(data)
        # skeleton = pc.skeleton 
        # pc_end = time.time()
        # pc_elapsed = pc_end - pc_start 


        #Run partition and combine 
        start_time = time.time()
        result = Plus_PC(options['algorithm'], data , stru_GT, options['maxCset'])
        results[options['algorithm']].append(result)
        elapsed = time.time() - start_time
        print(f"{options['algorithm']} completed in {elapsed:.4f} seconds")



    
