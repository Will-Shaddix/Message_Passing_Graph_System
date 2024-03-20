

for num_cores in  49 65 97 127
do
    for freq in 8 12 
    do
        build/X86/gem5.opt --outdir=m5out/graph_system/l2cache/${num_cores}_cores/${freq}ghz -re configs/William/graph_src/Cache_Graph_System.py ${freq} short 8 4 0 minor ${num_cores} &
    done
done


build/X86/gem5.opt --outdir=m5out/graph_system/long/65_cores/5Ghz -re configs/William/graph_src/Cache_Graph_System.py 5 long 8 4 0 minor 65


#     build/X86/gem5.opt --outdir=m5out/poster/with_reset_test/129_cores_long --debug-file=debug.txt --debug-flags=OneThousand  -re configs/William/graph_src/no_cache_BFS_AL_Hardware.py 3 long 32 8 0 timing 129

# build/X86/gem5.opt --outdir=m5out/poster/16_cores_fb --debug-file=debug.txt --debug-flags=OneThousand  -re configs/William/graph_src/BFS_AL_Hardware.py 3 fb 32 8 0 timing 


# build/X86/gem5.opt --outdir=m5out/compare/timing_v_o3/timing/65_cores_actual_fb --debug-file=debug.txt --debug-flags=OneThousand  -re configs/William/graph_src/no_cache_BFS_AL_Hardware.py 3 fb 32 8 0 timing 

# nohup build/X86/gem5.opt --outdir=m5out/AL_hw/long/32GB_edge_8GB_vertex -re configs/William/graph_src/BFS_AL_Hardware.py 3 long 32 8 &

