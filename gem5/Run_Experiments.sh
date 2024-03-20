
# build/X86_MI_example/gem5.opt --outdir=m5out/ASPLOS/v_E_partitioned/test -re  configs/William/graph_src/ASPLOS_Graph_System.py 5 fb_32 32 16 0 timing 65 

for cpu in minor #timing #timing # minor # O3
do
for graph in 165k_32 # 250k_32 #short_32 # 165k_32 # short_32 fb_32 #short_32
do
    for system in  local_vertex #disaggregated local_vertex accelerator
    do
        for front_end_latency in 150 # 50 #500 #10 
        do
            build/X86_MI_example/gem5.opt --outdir=m5out/data/${graph}/${system}/${front_end_latency}ns/${cpu}/actual_no_prints -re configs/William/graph_src/My_Graph_System.py 5 ${graph} 32 24 0 ${cpu} 65 ${system} ${front_end_latency}&

            # build/X86_MI_example/gem5.opt --outdir=m5out/ASPLOS/data/${graph}/${system}/${front_end_latency}ns/${cpu} -re configs/William/graph_src/ASPLOS_Graph_System.py 5 ${graph} 32 24 0 ${cpu} 97 ${system} ${front_end_latency}&
        done
    done
done    
done


    build/X86_MI_example/gem5.opt --outdir=m5out/data/165k_48/local_vertex/150ns/minor/ -re configs/William/graph_src/My_Graph_System.py 5 165k_48 32 24 0 minor 97 local_vertex 150 &
