import argparse
from random import randint


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("input", help="input file")
    parser.add_argument("output", help="output file")
    parser.add_argument("graph_size", help="number of vertices")
    parser.add_argument("graph_density", help="density of the graph")
    
    args = parser.parse_args()
    graph_size = int(args.graph_size)
    graph_density = int(args.graph_density)
    edge_counter = {}
    for i in range(graph_size):
        edge_counter[i] = 0
    
    with open(args.output, "w") as f:
        for i in range(graph_size):
            if i < 10:
                num_edges = graph_density*5
            elif i < 100:
                num_edges = graph_density*2
            else:
                num_edges = graph_density
            
            for j in range(num_edges):
                temp_graph_density = graph_density
                while True:
                    random_vertex = randint(0, graph_size-1)
                    if edge_counter[random_vertex] < temp_graph_density and random_vertex != i:
                        edge_counter[random_vertex] += 1
                        break
                    else:
                        temp_graph_density += 1
                        
                f.write(f"{i} {random_vertex}\n")
            
    
    
   
    print("Done!")
                