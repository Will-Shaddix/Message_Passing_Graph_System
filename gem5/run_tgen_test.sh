
for num_cores in  49 65 97 #127
do
    for freq in 8 12 
    do
        build/X86/gem5.opt --outdir=m5out/graph_system/l2cache_interleaved/${num_cores}_cores/${freq}ghz -re configs/William/graph_src/Cache_Graph_System.py ${freq} short 8 4 0 minor ${num_cores} &
    done
done


build/X86/gem5.opt --outdir=m5out/graph_system/l2cache_interleaved/127_cores/3Ghz -re configs/William/graph_src/Cache_Graph_System.py 3 long 8 4 0 minor 127

# build/X86/gem5.opt --outdir=m5out/BW_test/mem  configs/William/graph_src/tgen_AL_Hardware.py mem &
# build/X86/gem5.opt --outdir=m5out/BW_test/mq  configs/William/graph_src/tgen_AL_Hardware.py mq &
# build/X86/gem5.opt --outdir=m5out/BW_test/al  configs/William/graph_src/tgen_AL_Hardware.py al 


# nohup build/X86/gem5.opt --outdir=m5out/big_twitter configs/William/graph_src/BFS_AL_Hardware.py &