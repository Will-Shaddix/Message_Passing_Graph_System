unique_numbers = set()

num_cores = 48
vertex_list = []
# graph_file = 'generated_graphs/150k_vertices_3_6mil_edges.txt'
# graph_file = 'generated_graphs/300k_vertices_7_2mil_edges.txt' # 9376
# graph_file = 'generated_graphs/500k_vertices_10_2mil_edges.txt' # 15626
# graph_file = 'generated_graphs/1m_vertices_25mil_edges.txt'
graph_file = 'generated_graphs/165k.txt' # 5157 for 32, 3438 for 48
# 250k: 7813 for 32
# graph_file = 'imported_graphs/gplus_combined.txt' # 

# graph_file = '../gem5/twitter_sorted_done.txt'
# graph_file = 'imported_graphs/soc-LiveJournal1.txt'
# graph_file = 'imported_graphs/facebook_combined.txt'


with open(graph_file, 'r') as file:
    for line in file:
        if line.startswith('#'):
            continue
        splitted = line.strip().split()
        if(len(splitted) < 2):
            print(splitted)
            continue
        x, y = splitted
        unique_numbers.add(x)
        unique_numbers.add(y)

# unique_numbers = list(unique_numbers)
# unique_numbers.sort()
# unique_numbers = list(enumerate(unique_numbers))
# print(unique_numbers[0])
count = len(unique_numbers)
print(count)
num_blank_vertices = num_cores - (count % num_cores)
degree = [0 for i in range(count + num_blank_vertices)]

edges = [[] for i in range(count+ num_blank_vertices)]

vertex_alias = [0 for i in range(count+ num_blank_vertices)]

print("modulo: ", count % num_cores)

# if num_blank_vertices > 0:
#     for i in range(count, count+num_blank_vertices):
        
#         edges[i].append(count)
    # edges[count+num_blank_vertices-1] = count+1


with open(graph_file, 'r') as file:
    for line in file:
        if line.startswith('#'):
            continue
        # print(line)
        splitted = line.strip().split()
        if(len(splitted) < 2):
            print(splitted)
            continue
        x, y = splitted
        # x, y = line.strip().split()
        # degree[int(x)] += 1 # was y
        edges[int(x)].append(int(y))

for i in range(len(edges)):
    edges[i] = list(set(edges[i]))
    edges[i].sort()
    edges[i].reverse()
    degree[i] = len(edges[i])

degree = list(enumerate(degree))
degree.sort(key = lambda x: x[1], reverse = True)

if num_blank_vertices > 0:
    for i in range(count, count+num_blank_vertices):
        
        edges[i].append(count)
        print(edges[i])
# print(degree[1][0])
# print(edges[0])




index = 0
for i in range(num_cores):
    j = i
    temp_index = 0
    while j < (count + num_blank_vertices):
        vertex_list.append(degree[j][0])
        vertex_alias[degree[j][0]] = index
        j += num_cores
        index += 1
        temp_index += 1
    print("partition size:", i, temp_index)
print("vertex_list[count+num_blank_vertices-1]: ", vertex_list[count+num_blank_vertices-1])
print("vertex_alias[count+num_blank_vertices-1]", vertex_alias[count+num_blank_vertices-1])

# print(vertex_list[0:10])
# print(degree[0:32])
# liveJournal_sorted_64_cores partion sizes: 75744 for partitions 0-18, 75743 for rest
# liveJournal_sorted_96_cores partion sizes: 50496 for partitions 0-50, 50495 for rest
# liveJournal_sorted_32_cores partion sizes: 151487 for partitions 0-18, 151486 for rest


with open('165k_48_2.txt', 'w') as file:
    for i in range(count + num_blank_vertices):
        for j in edges[vertex_list[i]]:
            file.write(str(vertex_alias[vertex_list[i]]) + ' ' + str(vertex_alias[j]) + '\n')





# print(edges[0])
