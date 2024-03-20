import m5
from m5.util import *
from m5.util.convert import *
from m5.objects import *

from caches import *

import argparse
import math


# interleaving
# intlv_channels = 8
# intlv_size = self.cache_line_size
# intlv_low_bit = int(math.log(intlv_size, 2))
# intlv_bits = intlv_bits = int(math.log(intlv_channels, 2))
# interface.range = AddrRange(addr_range.start, size = addr_range.size(),
#                         intlvHighBit = intlv_low_bit + intlv_bits - 1,
#                         xorHighBit = 0,
#                         intlvBits = intlv_bits,
#                         intlvMatch = chnl)


parser = argparse.ArgumentParser()

parser.add_argument('clock_speed', type = str,
                    help = '''clock speed''')

parser.add_argument('workload', type = str,
                    help = '''short for short twitter, long for long twitter''')

parser.add_argument('num_edge_GiB', type = int, default = 8,
                    help = 'number of GiB in the memory system, \
                    could only be a multiple of 2 must be at least 4, e.g.  4, 6, 8, ..')

parser.add_argument('num_vertex_GiB', type = int, default = 2,
                    help = 'number of GiB in the memory system, \
                    could only be a multiple of 1 must be at least 2, e.g. 2, 3, 4, 5, ..')

parser.add_argument('batch', type = int, default = 0,
                    help = '''does the consumer read from the message queue in batches? true is yes''')

parser.add_argument('cpu_type', type = str, default = "timing",
                    help = '''timing or O3''')

parser.add_argument('num_cores', type = int, default = 9,
                    help = '''must be odd''')
parser.add_argument('system', type = str, default = "disagggregated",
                    help = '''options are accelerator, local_vertex, disagggregated''')

parser.add_argument('frontend_latency', type = int, default = 10,
                    help = '''front end latency of disaggregated memory controller''')



options = parser.parse_args()

options.monitors = 0

if options.system == "accelerator":
    options.edge_partitioned = 1
    options.vertex_partitioned = 1
if options.system == "local_vertex":
    options.edge_partitioned = 0
    options.vertex_partitioned = 1
if options.system == "disaggregated":
    options.edge_partitioned = 0
    options.vertex_partitioned = 0
    
vertices_per_partition = 999999999
num_cores = options.num_cores # Needs to be odd number!!

edge_mem_type = "DDR4_2400_16x4"

vertex_mem_type = "HBM_2000_4H_1x64" # "DDR"

num_edge_gib = options.num_edge_GiB # default is 8
num_vertex_gib = options.num_vertex_GiB # default is 2

mem_size = str(num_edge_gib + num_vertex_gib) + "GiB"
# mem_size = "8GiB"

# print("total mem size: " + mem_size)
# print("num_edge_gib: " + str(num_edge_gib) + "GiB num_vertex_gib: " + str(num_vertex_gib) + "GiB")

# num_edge_mem_ctrls = 6


num_edge_mem_ctrls = int(num_edge_gib*2) # assumes 512 MiB per memory controller
num_vertex_mem_ctrls = int(num_vertex_gib*2) # assumes 512 MiB per memory controller

EL_vaddr = 0x600000000 # Make sure this is the same as in consumer.cpp, counter.cpp, and generator.cpp
EL_paddr = 2 << 31# 4GiB   # need to update in graph_init
VL_vaddr = 0x2000000000
VL_paddr = num_edge_gib * gibi # 6GiB 11 << 31 Change this to be vertex memory base

active_list_size = 65536  # 64KiB 

initialization_vaddr = 0x200000000
initialization_paddr = (1 << 25) #1 << 32 # 4GiB

finished_vaddr = 0x300000000 # 
finished_paddr = (1 << 25) + 4096 # 

# print("finished_paddr = ", finished_paddr)

finished_flag_vaddr = 0x310000000 # this is what counter.cpp polls
# finished_flag_paddr = (1 << 25) - 4096 # 1GiB - 4KiB
finished_flag_paddr = (1 << 31)
# message queues are odd numbered addresses of finished flag
msg_queue_vaddr = 0x100000000
msg_queue_paddr = (num_edge_gib + num_vertex_gib) * gibi# 1 << 33 # 8GiB
# print("msg_queue_paddr", msg_queue_paddr)
active_list_vaddr = 0x400000000
active_list_paddr = msg_queue_paddr + (4*gibi)
# print("active_list_paddr", active_list_paddr)

active_list_base = toInteger(mem_size, "bytes", "GiB") * gibi + toInteger("1GiB", "bytes", "GiB") * gibi # must always be higher than mem_size
mq_range_base = toInteger(mem_size, "bytes", "GiB") * gibi#, metric_prefixes)#, int)

# each msg_queue gets a 4KiB range so that it has its own page
mq_ranges = [AddrRange(start=str(mq_range_base + (4096*i)) + "B", size="4KiB") for i in range(int(num_cores/2))] 

# each active list gets 64 KiB range which is used as a circular buffer
active_list_ranges = [AddrRange(start=str(active_list_base + (65536*i)) + "B", size="64KiB") for i in range(int(num_cores/2))]


num_mem_ctrls = num_edge_mem_ctrls + num_vertex_mem_ctrls
mem_range_base = 0
# mem_ctrl_size = int((toInteger(mem_size, "bytes", "GiB")*gibi) / num_mem_ctrls) # 2147483648  8589934592
edge_ctrl_size = int((num_edge_gib*gibi) / num_edge_mem_ctrls) # 2147483648  8589934592
vertex_ctrl_size = int((num_vertex_gib*gibi) / num_vertex_mem_ctrls) # can use this to change sizes of edge memory vs vertex memory

# print("edge_ctrl_size: ", edge_ctrl_size)
# print("vertex_ctrl_size: ", vertex_ctrl_size) 

system = System()

system.clk_domain = SrcClockDomain()
# system.clk_domain.clock = '1GHz'
system.clk_domain.clock = options.clock_speed + 'GHz'
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = 'timing'
system.mem_ranges = [AddrRange(mem_size)]

system.membus = SystemXBar(width=64)
# system.membus = IOXBar(width=64) # EDIT made non-coherent
if options.cpu_type == "timing":
    system.cpu = [X86TimingSimpleCPU() for i in range(num_cores)]
elif options.cpu_type == "O3":
    system.cpu = [X86O3CPU() for i in range(num_cores)]
elif options.cpu_type == "minor":
    system.cpu = [X86MinorCPU() for i in range(num_cores)]
else:
    print("Invalid cpu type")
    exit()


if options.workload == "short":
    system.graphInitializer = GraphInit(graph_file="twitter_sorted_done.txt", EL_addr=EL_paddr, VL_addr=VL_paddr)

if options.workload == "long":
    system.graphInitializer = GraphInit(graph_file="/data/graph_cache/real/twitter/sorted_graph.txt", EL_addr=EL_paddr, VL_addr=VL_paddr)

if options.workload == "fb":
    system.graphInitializer = GraphInit(graph_file="facebook_combined.txt", EL_addr=EL_paddr, VL_addr=VL_paddr)

if options.workload == "balance":
    system.graphInitializer = GraphInit(graph_file="../graphs/generated_graphs/small_generated_graph.txt", EL_addr=EL_paddr, VL_addr=VL_paddr)

if options.workload == "tiny":
    system.graphInitializer = GraphInit(graph_file="../graphs/generated_graphs/tiny_graph.txt", EL_addr=EL_paddr, VL_addr=VL_paddr)
    
if options.workload == "liveJournal":
    system.graphInitializer = GraphInit(graph_file="../graphs/liveJournal_sorted_1_partition.txt", EL_addr=EL_paddr, VL_addr=VL_paddr)

if options.workload == "short_32":
    vertices_per_partition = 2541
    system.graphInitializer = GraphInit(graph_file="../graphs/twitter_test3_partition.txt", EL_addr=EL_paddr, VL_addr=VL_paddr, partition_size=2541, edge_partitioned=options.edge_partitioned, vertex_partitioned=options.vertex_partitioned, num_partitions=32, mem_ctrl_size=1024*1024*512)
if options.workload == "fb_32":
    vertices_per_partition = 127
    system.graphInitializer = GraphInit(graph_file="../graphs/fb_test_partition.txt", EL_addr=EL_paddr, VL_addr=VL_paddr, partition_size=127, edge_partitioned=options.edge_partitioned, vertex_partitioned=options.vertex_partitioned, num_partitions=32, mem_ctrl_size=1024*1024*512)
if options.workload == "short_48":
    vertices_per_partition = 1694
    system.graphInitializer = GraphInit(graph_file="../graphs/short_48.txt", EL_addr=EL_paddr, VL_addr=VL_paddr, partition_size=1694, edge_partitioned=options.edge_partitioned, vertex_partitioned=options.vertex_partitioned, num_partitions=32, mem_ctrl_size=1024*1024*512)

if options.workload == "150k_32":
    vertices_per_partition = 4688
    system.graphInitializer = GraphInit(graph_file="../graphs/150k_32.txt", EL_addr=EL_paddr, VL_addr=VL_paddr, partition_size=vertices_per_partition, edge_partitioned=options.edge_partitioned, vertex_partitioned=options.vertex_partitioned, num_partitions=32, mem_ctrl_size=1024*1024*512)
if options.workload == "300k_32":
    vertices_per_partition = 9376
    system.graphInitializer = GraphInit(graph_file="../graphs/300k_32.txt", EL_addr=EL_paddr, VL_addr=VL_paddr, partition_size=vertices_per_partition, edge_partitioned=options.edge_partitioned, vertex_partitioned=options.vertex_partitioned, num_partitions=32, mem_ctrl_size=1024*1024*512)
if options.workload == "500k_32":
    vertices_per_partition = 15626
    system.graphInitializer = GraphInit(graph_file="../graphs/500k_32.txt", EL_addr=EL_paddr, VL_addr=VL_paddr, partition_size=vertices_per_partition, edge_partitioned=options.edge_partitioned, vertex_partitioned=options.vertex_partitioned, num_partitions=32, mem_ctrl_size=1024*1024*512)
if options.workload == "1m_32":
    vertices_per_partition = 15626
    system.graphInitializer = GraphInit(graph_file="../graphs/1m_32.txt", EL_addr=EL_paddr, VL_addr=VL_paddr, partition_size=vertices_per_partition, edge_partitioned=options.edge_partitioned, vertex_partitioned=options.vertex_partitioned, num_partitions=32, mem_ctrl_size=1024*1024*512)

if options.workload == "165k_32":
    vertices_per_partition = 5157
    system.graphInitializer = GraphInit(graph_file="../graphs/165k_32.txt", EL_addr=EL_paddr, VL_addr=VL_paddr, partition_size=vertices_per_partition, edge_partitioned=options.edge_partitioned, vertex_partitioned=options.vertex_partitioned, num_partitions=32, mem_ctrl_size=1024*1024*512)
if options.workload == "165k_48":
    vertices_per_partition = 3438
    system.graphInitializer = GraphInit(graph_file="../graphs/165k_48.txt", EL_addr=EL_paddr, VL_addr=VL_paddr, partition_size=vertices_per_partition, edge_partitioned=options.edge_partitioned, vertex_partitioned=options.vertex_partitioned, num_partitions=32, mem_ctrl_size=1024*1024*512)

if options.workload == "250k_32":
    vertices_per_partition = 7813
    system.graphInitializer = GraphInit(graph_file="../graphs/250k_32.txt", EL_addr=EL_paddr, VL_addr=VL_paddr, partition_size=vertices_per_partition, edge_partitioned=options.edge_partitioned, vertex_partitioned=options.vertex_partitioned, num_partitions=32, mem_ctrl_size=1024*1024*512)

# fb_32: 127, short_32: 2541, short_48: 1694
# need to edit memory ranges


if(options.monitors == 1):
    system.cpu_monitors = [CommMonitor() for i in range(num_cores)]
    system.monitors = [CommMonitor() for i in range(num_cores - 1)]


system.test_xbar = [IOXBar(width=64) for i in range(num_cores)] # xbar for each core between dcache and core
system.mem_bridge = [Bridge(delay='1ns', ranges=system.mem_ranges[0]) for i in range(num_cores)] # bridge for each core between dcache and membus

# EDIT eliminating bottom 2 sets of bridges
# system.xbar2xbar_bridge = [Bridge(delay='.1ns', ranges=AddrRange(start=mem_size, size=str((2147483648) + (4096 * int(num_cores/2))) + "B")) for i in range(num_cores)] 
# system.xbar2al_bridge = [Bridge(delay='.1ns', ranges=AddrRange(start=active_list_paddr, size=str((2147483648) + (4096 * int(num_cores/2))) + "B"), req_size=1024, resp_size=1024) for i in range(num_cores)]
system.mq_xbar = [IOXBar(width=64) for i in range(int(num_cores/2))] # xbar for all message queues   EDIT: Make one for each msg_queue
system.al_xbar = [IOXBar(width=64) for i in range(int(num_cores/2))] # xbar for all active lists   EDIT: Make one for each active_list

# # excess bridges
# system.mq_bridge =[Bridge(delay='.1ns', ranges=AddrRange(start=mem_size, size="4KiB")) for i in range(int(num_cores/2))] # bridge between xbar and msg_queue
# system.al_bridge = [Bridge(delay='.1ns', ranges=AddrRange(start=active_list_paddr, size="64KiB"),req_size=1024, resp_size=1024) for i in range(int(num_cores/2))] # needs adjustig


# mq_range = mq_range_base
# # excess bridges
# for bridge in system.mq_bridge:
#     bridge.ranges = AddrRange(start=str(mq_range), size="4KiB")
#     mq_range += 4096

# al_range = active_list_paddr
# for bridge in system.al_bridge:
#     bridge.ranges = AddrRange(start=str(al_range), size="64KiB")
#     al_range += 65536


system.icache = [L1ICache() for i in range(num_cores)]
system.l2cache = [L2Cache() for i in range(num_cores)]
system.dcache = [L1DCache() for i in range(num_cores)]

for j in range(num_cores):
    system.cpu[j].icache_port = system.icache[j].cpu_side
    system.icache[j].mem_side = system.membus.cpu_side_ports
    if(options.monitors == 1):
        system.cpu[j].dcache_port = system.cpu_monitors[j].cpu_side_port
        system.cpu_monitors[j].mem_side_port = system.test_xbar[j].cpu_side_ports
    else:
        system.cpu[j].dcache_port = system.test_xbar[j].cpu_side_ports
    # system.cpu[j].dcache_port = system.test_xbar[j].cpu_side_ports

    system.test_xbar[j].mem_side_ports = system.mem_bridge[j].cpu_side_port
    # system.test_xbar[j].mem_side_ports = system.xbar2xbar_bridge[j].cpu_side_port # EDIT Eliminate this bridge, instead have this crossbar connect to all msg_queue XBARs
    # system.test_xbar[j].mem_side_ports = system.xbar2al_bridge[j].cpu_side_port # EDIT Eliminate this bridge, instead have this crossbar connect to all active_list XBARs

    for k in range(int(num_cores/2)):
        system.test_xbar[j].mem_side_ports = system.mq_xbar[k].cpu_side_ports
        system.test_xbar[j].mem_side_ports = system.al_xbar[k].cpu_side_ports
    # system.xbar2xbar_bridge[j].mem_side_port = system.mq_xbar.cpu_side_ports # EDIT
    # system.xbar2al_bridge[j].mem_side_port = system.al_xbar.cpu_side_ports #EDIT

    system.mem_bridge[j].mem_side_port = system.dcache[j].cpu_side #system.membus.cpu_side_ports
    
    system.dcache[j].mem_side = system.l2cache[j].cpu_side
    system.l2cache[j].mem_side = system.membus.cpu_side_ports


# these bridges might be unnecessary
# for j in range(int(num_cores/2)): # num_cores/2 is the number of consumers
    # system.mq_xbar[j].mem_side_ports = system.mq_bridge[j].cpu_side_port
    # system.mq_bridge[j].cpu_side_port = system.mq_xbar[j].mem_side_ports # EDIT connect to msg_queue specific xbar
    # system.al_bridge[j].cpu_side_port = system.al_xbar[j].mem_side_ports # EDIT connect to active_list specific xbar
    
for j in range(num_cores):
    system.cpu[j].createInterruptController()
    # Note: Next 3 lines are x86 specific
    system.cpu[j].interrupts[0].pio = system.membus.mem_side_ports
    system.cpu[j].interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu[j].interrupts[0].int_responder = system.membus.mem_side_ports


# system.msg_queues = [MessageQueue(myRange=AddrRange(start=str(0x200000000 + (i*4096)) + "B", size="4KiB"), queueSize=640000, finished_addr=(finished_paddr +(2*i) + 1)) for i in range(int(num_cores/2))]
system.msg_queues = [MessageQueue(myRange=AddrRange(start=str(mq_range_base + (i*4096)), size="4KiB"), queueSize=640000, finished_addr=(finished_paddr +(2*i) + 1)) for i in range(int(num_cores/2))]

system.active_lists = [ActiveList(myRange=AddrRange(start=str(active_list_paddr + (65536*i)), size="64KiB"), queueSize=640000, finished_addr=(finished_paddr +(2*i))) for i in range(int(num_cores/2))]


for j in range(int(num_cores/2)):
    # excess bridges
    # system.msg_queues[j].cpu_side = system.mq_bridge[j].mem_side_port
    
    if(options.monitors == 0):
        system.msg_queues[j].cpu_side = system.mq_xbar[j].mem_side_ports
        system.active_lists[j].cpu_side = system.al_xbar[j].mem_side_ports
    # system.msg_queues[j].cpu_side = system.mq_xbar[j].mem_side_ports
    system.msg_queues[j].myRange = AddrRange(start=str(mq_range_base + (4096*j)) + "B", size="4KiB")
    
    # only include below line if messageQueue is writing to finished
    # system.msg_queues[j].mem_side = system.membus.cpu_side_ports    

    # system.active_lists[j].cpu_side = system.al_xbar[j].mem_side_ports
    



system.system_port = system.membus.cpu_side_ports

# system.graphInitializer.mirrors_map_mem = system.membus.cpu_side_ports
system.graphInitializer.port = system.membus.cpu_side_ports



system.mem_ctrls = [MemCtrl() for i in range(num_mem_ctrls)]
intlv_channels = 4
intlv_size = 64
intlv_low_bit = int(math.log(intlv_size, 2))
intlv_bits  = int(math.log(intlv_channels, 2))
intlv_end = mem_range_base + 4*edge_ctrl_size

edge_intlv_channels = 32
edge_intlv_size = 64
edge_intlv_low_bit = int(math.log(edge_intlv_size, 2))
edge_intlv_bits = int(math.log(edge_intlv_channels, 2))
edge_intlv_end = (edge_intlv_channels*edge_ctrl_size)
# print("edge_intlv_end: ", edge_intlv_end)
                      
for i in range(num_edge_mem_ctrls):
    # interleave first 8? start = 0 end = mem_range_base + 8*mem_ctrl_size
    
    system.mem_ctrls[i].dram = DDR4_2400_16x4()
    # system.mem_ctrls[i].dram.range = AddrRange(start=str(mem_range_base) + "B", size=str(mem_ctrl_size) + "B")
    if( i < intlv_channels):
        system.mem_ctrls[i].dram.range = AddrRange(0, size = intlv_end,
                        intlvHighBit = intlv_low_bit + intlv_bits - 1,
                        xorHighBit = 0,
                        intlvBits = intlv_bits,
                        intlvMatch = i)
    elif((i < (intlv_channels + edge_intlv_channels)) and options.edge_partitioned == 0):
        system.mem_ctrls[i].static_frontend_latency = str(options.frontend_latency) +"ns"
        system.mem_ctrls[i].dram.range = AddrRange(intlv_end, size = edge_intlv_end,
                        intlvHighBit = edge_intlv_low_bit + edge_intlv_bits - 1,
                        xorHighBit = 0,
                        intlvBits = edge_intlv_bits,
                        intlvMatch = i - 4)
    else:
        system.mem_ctrls[i].dram.range = AddrRange(start=str(mem_range_base) + "B", size=str(edge_ctrl_size) + "B")
    system.mem_ctrls[i].port = system.membus.mem_side_ports
    
    # print("Edge " + str(i) + " mem start: " + str(mem_range_base) + "B")
    mem_range_base += edge_ctrl_size
    



# Vertex Memory Controllers
for i in range(num_edge_mem_ctrls, num_mem_ctrls):
    # if(vertex_mem_type == "HBM_2000_4H_1x64"):
    if(options.system != "disaggregated"):
        system.mem_ctrls[i].dram = HBM_2000_4H_1x64()
    else:
        system.mem_ctrls[i].dram = DDR4_2400_16x4()
    # system.mem_ctrls[i].dram.range = AddrRange(start=str(mem_range_base) + "B", size=str(mem_ctrl_size) + "B")
    system.mem_ctrls[i].dram.range = AddrRange(start=str(mem_range_base) + "B", size=str(vertex_ctrl_size) + "B")
    system.mem_ctrls[i].port = system.membus.mem_side_ports
    # print("Vertex " + str(i) +  " mem start: " + str(mem_range_base) + "B")
    mem_range_base += vertex_ctrl_size
    
if(options.monitors == 1):
    for i in range(int(num_cores/2)):
        system.monitors[2*i].cpu_side_port = system.mq_xbar[i].mem_side_ports # message queues are even
        system.monitors[2*i].mem_side_port = system.msg_queues[i].cpu_side
        
        
        system.monitors[(2*i) + 1].cpu_side_port = system.al_xbar[i].mem_side_ports
        system.monitors[(2*i) + 1].mem_side_port = system.active_lists[i].cpu_side


binary = "configs/William/graph_src/counter"
binary2 = "configs/William/graph_src/batching/consumer_al_partitioned"
binary3 = "configs/William/graph_src/batching/generator_al_partitioned"

system.workload = SEWorkload.init_compatible(binary)
system.workload2 = SEWorkload.init_compatible(binary2)
system.workload3 = SEWorkload.init_compatible(binary3)

process = [Process() for i in range(num_cores)]
process[0].cmd = [binary, str(num_cores - 1)] # should always be true

for i in range(1, int(num_cores/2) + 1):
    process[(2*i) - 1].cmd = [binary2, str(i - 1), str(int(num_cores/2)), str(options.vertex_partitioned), str(vertices_per_partition)] # consumer
    process[(2*i) - 1].pid = 101 + i
    process[2*i].cmd = [binary3, str(i - 1), str(int(num_cores/2)), str(options.edge_partitioned), str(vertices_per_partition)] # generator
    process[2*i].pid = 301 + i


for i in range(num_cores):
    system.cpu[i].workload = process[i]
    system.cpu[i].createThreads()
    


root = Root(full_system=False, system=system)
m5.instantiate()


EL_size = VL_paddr - EL_paddr
max_int = 2**30

# print(type(EL_vaddr+(5*max_int)), type(EL_paddr+(5*max_int)), type(max_int))

for my_process in process:

    # my_process.map(vaddr=EL_vaddr, paddr=EL_paddr, size=3000000*8*2, cacheable=True) # EL mapping  Twitter Graph 3,000,000 edges 3000000*8*2
    my_process.map(vaddr=EL_vaddr, paddr=EL_paddr, size=max_int, cacheable=True) # EL mapping  Twitter Graph 3,000,000 edges 3000000*8*2
    my_process.map(vaddr=EL_vaddr+max_int, paddr=EL_paddr+max_int, size=max_int, cacheable=True) # EL mapping  Twitter Graph 3,000,000 edges 3000000*8*2
    my_process.map(vaddr=EL_vaddr+(2*max_int), paddr=EL_paddr+(2*max_int), size=max_int, cacheable=True) # EL mapping  Twitter Graph 3,000,000 edges 3000000*8*2
    my_process.map(vaddr=EL_vaddr+(3*max_int), paddr=EL_paddr+(3*max_int), size=max_int, cacheable=True) # EL mapping  Twitter Graph 3,000,000 edges 3000000*8*2
    my_process.map(vaddr=EL_vaddr+(4*max_int), paddr=EL_paddr+(4*max_int), size=max_int, cacheable=True) # EL mapping  Twitter Graph 3,000,000 edges 3000000*8*2
    my_process.map(vaddr=EL_vaddr+(5*max_int), paddr=EL_paddr+(5*max_int), size=max_int, cacheable=True) # EL mapping  Twitter Graph 3,000,000 edges 3000000*8*2
    # if options.workload == "long":
    my_process.map(vaddr=EL_vaddr+(6*max_int), paddr=EL_paddr+(6*max_int), size=max_int, cacheable=True)
    my_process.map(vaddr=EL_vaddr+(7*max_int), paddr=EL_paddr+(7*max_int), size=max_int, cacheable=True)
    my_process.map(vaddr=EL_vaddr+(8*max_int), paddr=EL_paddr+(8*max_int), size=max_int, cacheable=True)
    my_process.map(vaddr=EL_vaddr+(9*max_int), paddr=EL_paddr+(9*max_int), size=max_int, cacheable=True)
    my_process.map(vaddr=EL_vaddr+(10*max_int), paddr=EL_paddr+(10*max_int), size=max_int, cacheable=True)
    my_process.map(vaddr=EL_vaddr+(11*max_int), paddr=EL_paddr+(11*max_int), size=max_int, cacheable=True)
    my_process.map(vaddr=EL_vaddr+(12*max_int), paddr=EL_paddr+(12*max_int), size=max_int, cacheable=True)
    my_process.map(vaddr=EL_vaddr+(13*max_int), paddr=EL_paddr+(13*max_int), size=max_int, cacheable=True)
    my_process.map(vaddr=EL_vaddr+(14*max_int), paddr=EL_paddr+(14*max_int), size=max_int, cacheable=True)
    my_process.map(vaddr=EL_vaddr+(15*max_int), paddr=EL_paddr+(15*max_int), size=max_int, cacheable=True)
    
    # my_process.map(vaddr=VL_vaddr, paddr=VL_paddr, size=9000000*32*8, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr, paddr=VL_paddr, size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr+max_int, paddr=VL_paddr+max_int, size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr+(2*max_int), paddr=VL_paddr+(2*max_int), size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr+(3*max_int), paddr=VL_paddr+(3*max_int), size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr+(4*max_int), paddr=VL_paddr+(4*max_int), size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr+(5*max_int), paddr=VL_paddr+(5*max_int), size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr+(6*max_int), paddr=VL_paddr+(6*max_int), size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr+(7*max_int), paddr=VL_paddr+(7*max_int), size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr+(8*max_int), paddr=VL_paddr+(8*max_int), size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr+(9*max_int), paddr=VL_paddr+(9*max_int), size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr+(10*max_int), paddr=VL_paddr+(10*max_int), size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr+(11*max_int), paddr=VL_paddr+(11*max_int), size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr+(12*max_int), paddr=VL_paddr+(12*max_int), size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr+(13*max_int), paddr=VL_paddr+(13*max_int), size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr+(14*max_int), paddr=VL_paddr+(14*max_int), size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr+(15*max_int), paddr=VL_paddr+(15*max_int), size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    my_process.map(vaddr=VL_vaddr+(16*max_int), paddr=VL_paddr+(16*max_int), size=max_int, cacheable=True) # VL mapping 90,000 Vertices
    if num_vertex_gib > 16:
        i = 17
        while i < num_vertex_gib:
            my_process.map(vaddr=VL_vaddr+(i*max_int), paddr=VL_paddr+(i*max_int), size=max_int, cacheable=True)
            i += 1



    # my_process.map(vaddr=VL_vaddr, paddr=VL_paddr, size=4096 * 512 * 2, cacheable=False) # VL mapping
    # my_process.map(vaddr=0x400000000, paddr=(1 << 25), size=4096, cacheable=False) #  initialized variable mapping working
    my_process.map(vaddr=initialization_vaddr, paddr=initialization_paddr, size=4096, cacheable=False) #  initialized variable mapping

    my_process.map(vaddr=finished_vaddr, paddr=finished_paddr, size=4096, cacheable=False) #  Mapping of finished variabel
    # my_process.map(vaddr=0x600000000, paddr=(1 << 25) + 8192, size=65536 * int(num_cores/2), cacheable=True) #  ActiveList addr mapping
    my_process.map(vaddr=active_list_vaddr, paddr=active_list_paddr, size=65536 * int(num_cores/2), cacheable=False) #  ActiveList addr mapping shouldn't be cacheable?
    # my_process.map(vaddr=0x600000000, paddr=active_list_base, size=65536 * int(num_cores/2), cacheable=True) #  ActiveList addr mapping shouldn't be cacheable?
    my_process.map(vaddr=finished_flag_vaddr, paddr=EL_paddr - 8192, size=4096, cacheable=False) #  Mapping of finished flag
    my_process.map(vaddr=msg_queue_vaddr, paddr=msg_queue_paddr, size=4096 * int(num_cores/2), cacheable=False) # 1<<33 is 8Gib, msg queue mapping

print("Beginning simulation!")
exit_event = m5.simulate()
print(f"Exiting @ {m5.curTick()} because {exit_event.getCause()}")