import m5
from m5.objects import *

from caches import *

num_cores = 21 # nothing happens at 59 cores, error at 57 cores, doesnt weork at 55 cores
edge_mem_type = "DDR4_2400_16x4"
num_edge_mem_ctrls = 6

vertex_mem_type = "ddr" #"HBM_2000_4H_1x64"
num_vertex_mem_ctrls = 2

mem_size = "8GiB"

mq_range_base = 0x200000000
mq_ranges = [AddrRange(start=str(mq_range_base + (4096*i)) + "B", size="4KiB") for i in range(int(num_cores/2))]

active_list_base = 0x240000000 # 9GiB
active_list_ranges = [AddrRange(start=str(active_list_base + (65536*i)) + "B", size="64KiB") for i in range(int(num_cores/2))]

# num_DDR_chnls = 6
# num_HBM_chnls = 2

# num_mem_ctrls = num_DDR_chnls + num_HBM_chnls
num_mem_ctrls = num_edge_mem_ctrls + num_vertex_mem_ctrls
mem_range_base = 0
mem_ctrl_size = int(8589934592 / num_mem_ctrls) # 2147483648  8589934592
vertex_ctrl_size = int(8589934592 / num_mem_ctrls)

system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('8GiB')]

system.membus = SystemXBar()

# system.cpu = X86TimingSimpleCPU()
system.cpu = [X86TimingSimpleCPU() for i in range(num_cores)]


# system.icache = L1ICache()
system.graphInitializer = GraphInit(graph_file="facebook_combined.txt")
# system.graphInitializer = GraphInit(graph_file="soc-Slashdot0902.txt")


#need to edit memory ranges
system.test_xbar = [IOXBar() for i in range(num_cores)] # xbar for each core between dcache and core
system.mem_bridge = [Bridge(delay='1ns', ranges=system.mem_ranges[0]) for i in range(num_cores)] # bridge for each core between dcache and membus
system.xbar2xbar_bridge = [Bridge(delay='1ns', ranges=AddrRange(start="8GiB", size=str((2147483648) + (4096 * int(num_cores/2))) + "B")) for i in range(num_cores)] # bridge for each core between dcache and membus
system.mq_xbar = IOXBar() # xbar for all message queues

system.mq_bridge =[Bridge(delay='1ns', ranges=AddrRange(start="8GiB", size="4KiB")) for i in range(int(num_cores/2))] # needs adjustig
mq_range = 8589934592
for bridge in system.mq_bridge:
    bridge.ranges = AddrRange(start=str(mq_range), size="4KiB")
    mq_range += 4096
# system.mq_bridge[1] = Bridge(delay='1ns', ranges=AddrRange(start="8589938688B", size="4KiB"))  # needs adjustig

system.icache = [L1ICache() for i in range(num_cores)]
system.dcache = [L1DCache() for i in range(num_cores)]

for j in range(num_cores):
    system.cpu[j].icache_port = system.icache[j].cpu_side
    system.icache[j].mem_side = system.membus.cpu_side_ports
    system.cpu[j].dcache_port = system.test_xbar[j].cpu_side_ports

    system.test_xbar[j].mem_side_ports = system.mem_bridge[j].cpu_side_port
    system.test_xbar[j].mem_side_ports = system.xbar2xbar_bridge[j].cpu_side_port

    system.xbar2xbar_bridge[j].mem_side_port = system.mq_xbar.cpu_side_ports

    system.mem_bridge[j].mem_side_port = system.dcache[j].cpu_side
    system.dcache[j].mem_side = system.membus.cpu_side_ports


for j in range(int(num_cores/2)): # num_cores/2 is the number of consumers
    system.mq_bridge[j].cpu_side_port = system.mq_xbar.mem_side_ports

    # system.mq_bridge[j].cpu_side_port = system.test_xbar.mem_side_ports
    

# system.dcache.mem_side = system.membus.cpu_side_ports

for j in range(num_cores):
    system.cpu[j].createInterruptController()
    # Note: Next 3 lines are x86 specific
    system.cpu[j].interrupts[0].pio = system.membus.mem_side_ports
    system.cpu[j].interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu[j].interrupts[0].int_responder = system.membus.mem_side_ports

#str(4096 * int(num_cores/2))



system.msg_queues = [MessageQueue(myRange=AddrRange(start=str(0x200000000 + (i*4096)) + "B", size="4KiB"), queueSize=64000) for i in range(int(num_cores/2))]
# system.msg_queues[1].myRange = AddrRange(start="8589938688B", size="4KiB")

msg_queue_base = 8589934592

for j in range(int(num_cores/2)):
    system.msg_queues[j].cpu_side = system.mq_bridge[j].mem_side_port
    system.msg_queues[j].myRange = AddrRange(start=str(msg_queue_base + (4096*j)) + "B", size="4KiB")


# system.active_list_bridges= [Bridge(delay='1ns', ranges=AddrRange(start=str(active_list_base + (65536*i)) + "B", size="64KiB")) for i in range(int(num_cores/2))]
# system.active_lists = [MessageQueue(myRange=AddrRange(start=str(0x240000000 + (i*65536)) + "B", size="64KiB"), queueSize=64000) for i in range(int(num_cores/2))]


# for j in range(int(num_cores/2)):
#     system.active_list_bridges[j].cpu_side_port = system.mq_xbar.mem_side_ports
#     system.active_list_bridges[j].mem_side_port = system.active_lists[j].cpu_side



system.system_port = system.membus.cpu_side_ports

system.graphInitializer.mirrors_map_mem = system.membus.cpu_side_ports


# num_mem_ctrls = 4
# mem_range_base = 0
# mem_ctrl_size = 8589934592
system.mem_ctrls = [MemCtrl() for i in range(num_mem_ctrls)]
# for i in range(num_HBM_chnls):
#     system.mem_ctrls.append(MemCtrl())

    # system.mem_ctrls.append(HBMCtrl())
#system.mem_ctrls += [HBMCtrl() for i in range(num_HBM_chnls)]
# for mem_ctrl in system.mem_ctrls:
for i in range(num_edge_mem_ctrls):
    system.mem_ctrls[i].dram = DDR4_2400_16x4()
    system.mem_ctrls[i].dram.range = AddrRange(start=str(mem_range_base) + "B", size=str(mem_ctrl_size) + "B")
    system.mem_ctrls[i].port = system.membus.mem_side_ports
    mem_range_base += mem_ctrl_size



# Vertex Memory Controllers
for i in range(num_edge_mem_ctrls, num_mem_ctrls):
    if(vertex_mem_type == "HBM_2000_4H_1x64"):
        system.mem_ctrls[i].dram = HBM_2000_4H_1x64()
    else:
        system.mem_ctrls[i].dram = DDR4_2400_16x4()
    system.mem_ctrls[i].dram.range = AddrRange(start=str(mem_range_base) + "B", size=str(mem_ctrl_size) + "B")
    system.mem_ctrls[i].port = system.membus.mem_side_ports
    print("HBM mem start: " + str(mem_range_base) + "B")
    mem_range_base += mem_ctrl_size


binary = "configs/William/graph_src/counter"
binary2 = "configs/William/graph_src/consumer"
binary3 = "configs/William/graph_src/generator"

system.workload = SEWorkload.init_compatible(binary)
system.workload2 = SEWorkload.init_compatible(binary2)
system.workload3 = SEWorkload.init_compatible(binary3)

process = [Process() for i in range(num_cores)]
process[0].cmd = [binary, str(num_cores - 1)] # should always be true

for i in range(1, int(num_cores/2) + 1):
    process[(2*i) - 1].cmd = [binary2, str(i - 1), str(int(num_cores/2))]
    process[(2*i) - 1].pid = 101 + i
    process[2*i].cmd = [binary3, str(i - 1), str(int(num_cores/2))]
    process[2*i].pid = 301 + i


for i in range(num_cores):
    system.cpu[i].workload = process[i]
    system.cpu[i].createThreads()



root = Root(full_system=False, system=system)
m5.instantiate()

for my_process in process:
    # 1073741824 = 1GiB
    # 2147483648 = 2GiB
    # 6442450944 = 6GiB
    # 7516192768 = 7GiB
    # 8589934592 = 8GiB
    my_process.map(vaddr=0x200000000, paddr=1 << 31, size=4096 * 1024*16*2 , cacheable=True) # EL mapping  changing paddr to 1<<30 broke it
    # my_process.map(vaddr=0x300000000, paddr=(1 << 27) , size=4096 * 512 * 2, cacheable=True) # VL mapping
    # my_process.map(vaddr=0x300000000, paddr= 1 << 31 , size=4096 * 512 * 2, cacheable=True) # VL mapping
    my_process.map(vaddr=0x300000000, paddr= 6442450944 , size=4096 * 512 * 2, cacheable=True) # VL mapping
    # my_process.map(vaddr=0x400000000, paddr=(1 << 25), size=4096, cacheable=False) #  initialized variable mapping working
    my_process.map(vaddr=0x400000000, paddr=(1 << 32), size=4096, cacheable=False) #  initialized variable mapping

    my_process.map(vaddr=0x500000000, paddr=(1 << 25) + 4096, size=4096, cacheable=False) #  Mapping of finished variabel
    # my_process.map(vaddr=0x600000000, paddr=(1 << 25) + 8192, size=65536 * int(num_cores/2), cacheable=True) #  ActiveList addr mapping
    my_process.map(vaddr=0x600000000, paddr=7516192768, size=65536 * int(num_cores/2), cacheable=True) #  ActiveList addr mapping shouldn't be cacheable?
    # my_process.map(vaddr=0x600000000, paddr=active_list_base, size=65536 * int(num_cores/2), cacheable=True) #  ActiveList addr mapping shouldn't be cacheable?

    # 7516192768B
    my_process.map(vaddr=0x510000000, paddr=(1 << 25) - 4096, size=4096, cacheable=False) #  Mapping of finished flag

    my_process.map(vaddr=0x100000000, paddr=1 << 33, size=4096 * int(num_cores/2), cacheable=True) # 1<<33 is 8Gib, msg queue mapping

print("Beginning simulation!")
exit_event = m5.simulate()
print(f"Exiting @ {m5.curTick()} because {exit_event.getCause()}")