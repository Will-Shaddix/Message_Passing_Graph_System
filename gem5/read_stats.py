import os

directory = 'm5out/ASPLOS/data/165k_32/accelerator/150ns/'  # Replace with the actual directory path
search_strings = ['busUtil ']  # Replace with the specific string you want to search for
edge_bw = []
vertex_bw = []
for filename in os.listdir(directory):
    if filename.endswith('.txt'):
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r') as file:
            for line in file:
                for search_string in search_strings:
                    if search_string in line:
                        line = line.strip()
                        line = line.split(' ')
                        line = list(filter(lambda a: a != '', line))
                        print(type(line))
                        for i in range(8, 40):
                            # if (line.contains("mem_ctrls" + str(i))):
                            if (("mem_ctrls" + str(i)) in line[0]):
                                edge_bw.append(float(line[1]))
                        for i in range(48, 80):
                            if (("mem_ctrls" + str(i)) in line[0]):
                                vertex_bw.append(float(line[1]))
                        
                        print(line)



print(edge_bw)
print(vertex_bw)
print("average edge bw = " + str(sum(edge_bw)/len(edge_bw)))
print("average vertex bw = " + str(sum(vertex_bw)/len(vertex_bw)))


                   
