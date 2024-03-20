/*
 * Copyright (c) 2021 The Regents of the University of California.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */


#include <cmath>
#include <iostream>
#include <string>
#include <stdio.h>
#include <stdlib.h>
// #include "../graph_types.h"
#include <fstream>

#include "mem/graph_init.hh"
#include "mem/packet.hh"
#include "base/cprintf.hh"
#include "base/loader/memory_image.hh"
#include "base/loader/object_file.hh"
#include "debug/GraphInit.hh"
#include "sim/sim_exit.hh"
#include "sim/clocked_object.hh"
#include "sim/system.hh"
namespace gem5
{



#include <string>

struct __attribute__ ((packed)) Edge
{
    uint16_t weight : 16;
    uint64_t neighbor : 48;

    Edge(uint64_t weight, uint64_t neighbor):
        weight(weight),
        neighbor(neighbor)
    {}

    std::string to_string() {
      std::string ret = "";
      ret += "Edge{weight: " + std::to_string(weight) + ", neighbord: " +
              std::to_string(neighbor) + "}";
      return ret;
    }
};

struct __attribute__ ((packed)) Vertex
{
    uint16_t dist : 16;
    uint64_t id : 32;
    uint64_t EL_start : 48;
    uint32_t EL_size : 31; // Degree
    bool active : 1;

    Vertex(uint64_t dist,   uint64_t id, uint64_t EL_start, uint32_t EL_size, bool active):
        dist(dist),
        id(id),
        EL_start(EL_start),
        EL_size(EL_size),
        active(active)
    {}

    std::string to_string() {
      std::string ret = "";
      ret += "Vertex{dist: " + std::to_string(dist) + ", id: " +
              std::to_string(id) + "}";
      return ret;
    }
};


struct __attribute__ ((packed)) Update
{
    uint16_t weight : 16;
    uint64_t dst_id : 48;

    Update(): weight(0), dst_id(0) {}

    Update(uint16_t weight, uint64_t dst_id):
        weight(weight),
        dst_id(dst_id)
    {}
};

// GraphInit::GraphInit(const GraphInitParams& p):
//     ClockedObject(p) // , mapPort("map_port", this, 1)//, graphFile(p.graph_file)
// {

// }

const uint64_t buffer_addr = 0x100000000; // change buffer_addr to MessageQueues[], add 4096 to each message queue

// const uint64_t EL_addr = 0x0000000080000000;//1 << 31;// 0x200000000;
// const uint64_t VL_addr = 6442450944; //0x300000000;
const uint64_t initalized_addr = 0x400000000;
const uint64_t finished_addr = 0x500000000;
const uint64_t finished_flag = 0x510000000;

GraphInit::GraphInit(const GraphInitParams& p):
    ClockedObject(p), mapPort("map_port", this, 1), graphFile(p.graph_file), EL_addr(p.EL_addr), VL_addr(p.VL_addr), size_of_partition(p.partition_size), edge_partitioned(p.edge_partitioned), vertex_partitioned(p.vertex_partitioned), num_partitions(p.num_partitions), mem_ctrl_size(p.mem_ctrl_size)
{
    //data_write_req = std::make_shared<Request>();
}

Port&
GraphInit::getPort(const std::string& if_name, PortID idx)
{
    if (if_name == "port") {
        return mapPort;
    // } else if (if_name == "mem_port") {
    //     //return BaseMemoryEngine::getPort("mem_port", idx);
    } else {
        return ClockedObject::getPort(if_name, idx);
    }
}

// void
// GraphInit::createBFSWorkload(Addr init_addr, uint32_t init_value)
// {
//     workload = new BFSWorkload(init_addr, init_value);
// }

// void
// GraphInit::createBFSVisitedWorkload(Addr init_addr, uint32_t init_value)
// {
//     workload = new BFSVisitedWorkload(init_addr, init_value);
// }

// void
// GraphInit::createSSSPWorkload(Addr init_addr, uint32_t init_value)
// {
//     workload = new SSSPWorkload(init_addr, init_value);
// }

// void
// GraphInit::createCCWorkload()
// {
//     workload = new CCWorkload();
// }

// void
// GraphInit::createAsyncPRWorkload(float alpha, float threshold)
// {
//     workload = new PRWorkload(alpha, threshold);
// }

// void
// GraphInit::createPRWorkload(int num_nodes, float alpha)
// {
//     workload = new BSPPRWorkload(num_nodes, alpha);
// }

// void
// GraphInit::createBCWorkload(Addr init_addr, uint32_t init_value)
// {
//     workload = new BSPBCWorkload(init_addr, init_value);
// }

// void
// GraphInit::createPopCountDirectory(int atoms_per_block)
// {
//     fatal_if(mode == ProcessingMode::NOT_SET, "You should set the processing "
//                         "mode by calling either setAsyncMode or setBSPMode.");
//     if (mode == ProcessingMode::ASYNCHRONOUS) {
//         for (auto mpu: mpuVector) {
//             mpu->createAsyncPopCountDirectory(atoms_per_block);
//         }
//     }
//     if (mode == ProcessingMode::BULK_SYNCHRONOUS) {
//         for (auto mpu: mpuVector) {
//             mpu->createBSPPopCountDirectory(atoms_per_block);
//         }
//     }
//     if (mode == ProcessingMode::POLY_GRAPH) {
//         for (auto mpu: mpuVector) {
//             mpu->createAsyncPopCountDirectory(atoms_per_block);
//         }
//     }
// }
PacketPtr
GraphInit::createELWritePacket(Addr addr, const uint8_t* data)
{
    // Create new request
    RequestPtr req = std::make_shared<Request>(addr, sizeof(Edge), 0,
                                               requestorID);
    req->setPC(((Addr)requestorID) << 2);
    auto cmd = MemCmd::WriteReq;
    PacketPtr pkt = new Packet(req, cmd);

    // uint8_t* pkt_data = new uint8_t[req->getSize()];
    pkt->dataDynamic(data);

    // if (cmd.isWrite()) {
    //     std::fill_n(pkt_data, req->getSize(), (uint8_t)requestorId);
    // }

    return pkt;
    // return nullptr;

    // my_req = std::make_shared<Request>(EL_addr + (index * sizeof(Edge)), sizeof(Edge), 0, requestorID); // need to check if 0 is okay for flags
    //     // replacing EL_addr with 1 << 31
    //     my_req->setPC(((Addr)requestorID) << 2);
    //     auto cmd = MemCmd::WriteReq;
    //     PacketPtr pkt = new Packet(my_req, cmd);
    //     pkt->dataDynamic((uint8_t*)curr_edge);
}

PacketPtr
GraphInit::createVLWritePacket(Addr addr, const uint8_t* data)
{
    // Create new request
    RequestPtr req = std::make_shared<Request>(addr, sizeof(Vertex), 0,
                                               requestorID);
    req->setPC(((Addr)requestorID) << 2);
    auto cmd = MemCmd::WriteReq;
    PacketPtr pkt = new Packet(req, cmd);

    pkt->dataDynamic(data);

    return pkt;

}

PacketPtr
GraphInit::create64WritePacket(Addr addr, const uint8_t* data)
{
    // Create new request
    RequestPtr req = std::make_shared<Request>(addr, sizeof(uint64_t), 0,
                                               requestorID);
    req->setPC(((Addr)requestorID) << 2);
    auto cmd = MemCmd::WriteReq;
    PacketPtr pkt = new Packet(req, cmd);

    pkt->dataDynamic(data);

    return pkt;

}

void
GraphInit::startup()
{
    /*Pseudo code for graph reader:
    Assumes graph is already sorted based on num_partitions
    need to know: num_partitions, size_of_partition, whether edge is partitioned or vertex is partitioned, mem_ctrl_size
    where size_of_partition is the number of vertices per partition
    1. Read the graph file
    2. where to write current_VL is calculated as VL_addr + (curr_partition * (vertex ID/size_of_partition)  + ((vertex ID % size_of_partition) * sizeof(Vertex))
     where the first term calculated the partition address and the second term calculates the offset within the partition
    3. Keep track of how many edges are written in the current partition and store this in local_EL_index. 
    use this local_EL_index to calculate the address of the current edge in the edge list as EL_addr + (curr_partition * (vertex ID/size_of_partition) + (local_EL_index * sizeof(Edge))    
    4. also use local EL_index in vertex information, where EL_start = local_EL_index and EL_size = number of edges in the vertex


    */

    // look at base_gen.cc and linear_gen.cc
    // RequestPtr req = std::make_shared<Request>(addr, size, flags,
    //                                            requestorId);
    // pkt: cmd: WriteReq
    // const auto& vertex_file = params().graph_file;

    // int num_partitions = 32;
    // uint32_t size_of_partition = 151487; // 151487 for liveJournal 32 partitions.
    // uint8_t edge_partitioned = 1; // 1 if edge partitioned, 0 if edge not partitioned
    // uint8_t vertex_partitioned = 1; // 1 if vertex partitioned, 0 if vertex not partitioned
    // uint64_t mem_ctrl_size = 268435456; // 256 MiB
    uint64_t local_EL_index = 0;


    if (graphFile == "")
        return;

    RequestPtr my_req;// = std::make_shared<Request>(addr, size, flags, requestorId);
    // req->setPC(((Addr)requestorId) << 2);
    // PacketPtr pkt = new Packet(req, cmd);
    // uint64_t* initalized = (uint64_t*)initalized_addr;

    bool is_Weighted = false;
    uint64_t num_nodes = 1;
    uint64_t EL_start;
    uint64_t max_node_id = 0;

    std::ifstream input_file;

    input_file.open(graphFile);

    Edge* curr_edge = new Edge(1,0);
    if(is_Weighted){

    }else{
        uint64_t src_id, dst_id, curr_src_id;
        input_file >> curr_src_id >> dst_id;

        uint64_t index = 0;
        uint32_t EL_size = 1;
        EL_start = index;
        // EL[index] = Edge(1, dst_id);

        *curr_edge = Edge(1, dst_id);

        Vertex* curr_vertex = new Vertex(65535, curr_src_id, EL_start, EL_size, false);

        // DPRINTF(GraphInit, "%s: Sending edge packet %s.  curr_src = %d, curr_dst = %d\n", __func__, pkt->print(), curr_src_id, dst_id);

        PacketPtr pkt = createELWritePacket(EL_addr + index * sizeof(Edge), (uint8_t*)curr_edge);
        local_EL_index++; // added for partitioning

        // DPRINTF(GraphInit, "%s: Sending edge packet %s.  curr_src = %d, curr_dst = %d\n", __func__, pkt->print(), curr_src_id, dst_id);

        index++;
        // working block!
        // my_req = std::make_shared<Request>(EL_addr + (index * sizeof(Edge)), sizeof(Edge), 0, requestorID); // need to check if 0 is okay for flags
        // // replacing EL_addr with 1 << 31
        // my_req->setPC(((Addr)requestorID) << 2);
        // auto cmd = MemCmd::WriteReq;
        // PacketPtr pkt = new Packet(my_req, cmd);
        // pkt->dataDynamic((uint8_t*)curr_edge);

        //pkt->setData((uint8_t*)curr_edge); // Should this stay as uin8_t or be edge?

        // uint8_t* pkt_data = new uint8_t[req->getSize()];


        // if (cmd.isWrite()) {
        //     std::fill_n(pkt_data, req->getSize(), (uint8_t)requestorId);
        // }

       // PacketPtr pkt;// = createELWritePacket(EL_addr + index * sizeof(Edge), curr_edge);
    //    DPRINTF(GraphInit, "%s: Sending packet %s.\n", __func__, pkt->print());
        DPRINTF(GraphInit, "%s: 1/8 Sending packet %s.\n", __func__, pkt->print());

        mapPort.sendPacket(pkt);

        uint32_t vid_curr_partition = 0; // use this to count the number of vertices already written in this partition

        while(input_file >> src_id >> dst_id){
            if(index < 1000){
                DPRINTF(GraphInit, "%s: Sending edge packet %s.  curr_src = %d, curr_dst = %d\n", __func__, pkt->print(), src_id, dst_id);
            }
            if(dst_id > max_node_id){
                max_node_id = dst_id;
            }
            if(curr_src_id != src_id){ // new vertex
            // check if vid_curr_partition is less than size_of_partition
            // if not then we need to start writing to second partition
            // if(vid_curr_partition < size_of_partition){
                num_nodes++;
                *curr_vertex = Vertex(65535, curr_src_id, EL_start, EL_size, false); // write old vertex into memory
                // pkt = createVLWritePacket(VL_addr + (curr_src_id * sizeof(Vertex)) + (()*mem_ctrl_size*vertex_partitioned), (uint8_t*)curr_vertex);
                
                // calculate partition number: (vid_curr_partition/size_of_partition)
                // calculate offset within partition: (vid_curr_partition%size_of_partition)
                if(vertex_partitioned == 1){
                    pkt = createVLWritePacket(VL_addr + ((curr_src_id%size_of_partition) * sizeof(Vertex) + ((curr_src_id/size_of_partition)*mem_ctrl_size*vertex_partitioned)), (uint8_t*)curr_vertex);
                }else{
                    pkt = createVLWritePacket(VL_addr + (curr_src_id * sizeof(Vertex)), (uint8_t*)curr_vertex);
                }
                // vid_curr_partition++;

            //    if(curr_src_id < 1000){
            //             DPRINTF(GraphInit, "%s: Sending Vertexpacket %s. EL_size = %d\n", __func__, pkt->print(), EL_size);
            //     }
                DPRINTF(GraphInit, "%s: 2/8 Sending packet curr_src_id: %lu, pkt->print(): %s.\n", __func__, curr_src_id, pkt->print());

                mapPort.sendPacket(pkt);

                if((src_id % size_of_partition == 0) && (edge_partitioned == 1)){
                    local_EL_index = 0; // only need to do this here and if partitioned
                    printf("resetting local el index for src_id: %lu\n", src_id);

                }

                if(curr_src_id != src_id - 1){
                    for(uint64_t i = curr_src_id + 1; i < src_id; i++){
                        *curr_vertex = Vertex(65535, i, 0, 0, false);
                    //    pkt = createVLWritePacket(VL_addr + (i * sizeof(Vertex)), (uint8_t*)curr_vertex);

                        if(vertex_partitioned == 1){
                            pkt = createVLWritePacket(VL_addr + ((i%size_of_partition) * sizeof(Vertex) + ((i/size_of_partition)*mem_ctrl_size*vertex_partitioned)), (uint8_t*)curr_vertex);
                        }else{
                        pkt = createVLWritePacket(VL_addr + (i * sizeof(Vertex)), (uint8_t*)curr_vertex);
                        }

                        if((i % size_of_partition == 0) && (edge_partitioned == 1)){
                            local_EL_index = 0;
                            printf("resetting local el index for src_id: %lu\n", i);
                        }

                        DPRINTF(GraphInit, "%s: 3/8 Sending packet %s.\n", __func__, pkt->print());

                        mapPort.sendPacket(pkt);
                        num_nodes++;
                    }
                }

                curr_src_id = src_id;
                // EL_start = index;
                EL_start = local_EL_index;
                *curr_edge = Edge(1, dst_id);
                // pkt = createELWritePacket(EL_addr + index * sizeof(Edge), (uint8_t*)curr_edge);
                if(edge_partitioned == 1){
                    pkt = createELWritePacket(EL_addr + (local_EL_index * sizeof(Edge)) + ((curr_src_id/size_of_partition)*mem_ctrl_size*edge_partitioned), (uint8_t*)curr_edge);
                }else{
                    pkt = createELWritePacket(EL_addr + index * sizeof(Edge), (uint8_t*)curr_edge);
                }
                DPRINTF(GraphInit, "%s: 4/8 Sending packet %s.\n", __func__, pkt->print());

                mapPort.sendPacket(pkt);
                local_EL_index++; // for partition 
                index++;
                EL_size = 1;
            }
            else{
                *curr_edge = Edge(1, dst_id);

                // pkt = createELWritePacket(EL_addr + index * sizeof(Edge), (uint8_t*)curr_edge);
                if(edge_partitioned == 1){
                    pkt = createELWritePacket(EL_addr + (local_EL_index * sizeof(Edge)) + ((curr_src_id/size_of_partition)*mem_ctrl_size*edge_partitioned), (uint8_t*)curr_edge);
                }else{
                    pkt = createELWritePacket(EL_addr + index * sizeof(Edge), (uint8_t*)curr_edge);
                }

                DPRINTF(GraphInit, "%s: 5/8 Sending packet %s.\n", __func__, pkt->print());
                mapPort.sendPacket(pkt);

                index++;
                local_EL_index++; // for partition
                EL_size++;
            }
            // num_nodes = max(num_nodes, max(src_id, dst_id));
        }

        DPRINTF(GraphInit, "%s: Past Loop!!!!\n", __func__);

        *curr_vertex = Vertex(65535, curr_src_id, EL_start, EL_size, false);
        // pkt = createVLWritePacket(VL_addr + curr_src_id * sizeof(Vertex), (uint8_t*)curr_vertex);
        if(vertex_partitioned == 1){
            pkt = createVLWritePacket(VL_addr + ((curr_src_id%size_of_partition) * sizeof(Vertex) + ((curr_src_id/size_of_partition)*mem_ctrl_size*vertex_partitioned)), (uint8_t*)curr_vertex);
        }else{
            pkt = createVLWritePacket(VL_addr + curr_src_id * sizeof(Vertex), (uint8_t*)curr_vertex);
        }
        // DPRINTF(GraphInit, "%s: Sending Vertexpacket %s.\n", __func__, pkt->print());

        mapPort.sendPacket(pkt);
        num_nodes++;

        if(curr_src_id < max_node_id){
                    for(uint64_t i = curr_src_id + 1; i <= max_node_id; i++){
                        *curr_vertex = Vertex(65535, i, 0, 0, false);
                    //    pkt = createVLWritePacket(VL_addr + (i * sizeof(Vertex)), (uint8_t*)curr_vertex);
                    if(vertex_partitioned == 1){
                        pkt = createVLWritePacket(VL_addr + ((i%size_of_partition) * sizeof(Vertex) + ((i/size_of_partition)*mem_ctrl_size*vertex_partitioned)), (uint8_t*)curr_vertex);
                    }else{
                        pkt = createVLWritePacket(VL_addr + (i * sizeof(Vertex)), (uint8_t*)curr_vertex);
                    }

                        // DPRINTF(GraphInit, "%s: Sending Vertexpacket %s.\n", __func__, pkt->print());
                        mapPort.sendPacket(pkt);
                        num_nodes++;
                    }
        }
    }
        // DPRINTF(GraphInit, "%s: Abount to send initialized packet.\n", __func__);
        // PacketPtr pkt2 = create64WritePacket((uint64_t)1 << 32, (uint8_t*)num_nodes); // was 25
        // DPRINTF(GraphInit, "%s: Sending initialized packet %s.\n", __func__, pkt2->print());

        // mapPort.sendPacket(pkt2);
        // DPRINTF(GraphInit, "%s: Sent initialized packet %s.\n", __func__, pkt2->print());



    input_file.close();
    printf("Startup complete!\n");
    // unsigned int vertex_atom = mpuVector.front()->vertexAtomSize();
    // for (auto mpu: mpuVector) {
    //     for (auto range: mpu->getAddrRanges()) {
    //         mpuAddrMap.insert(range, mpu);
    //     }
    //     mpu->setProcessingMode(mode);
    //     mpu->recvWorkload(workload);
    // }

    // const auto& vertex_file = params().vertex_image_file;
    // if (vertex_file == "")
    //     return;

    // auto* object = loader::createObjectFile(vertex_file, true);
    // fatal_if(!object, "%s: Could not load %s.", name(), vertex_file);

    // loader::debugSymbolTable.insert(*object->symtab().globals());
    // loader::MemoryImage vertex_image = object->buildImage();
    // maxVertexAddr = vertex_image.maxAddr();

    // int num_total_vertices = (maxVertexAddr / sizeof(WorkListItem));
    // numTotalSlices = std::ceil((double) num_total_vertices / verticesPerSlice);

    // numPendingUpdates = new int [numTotalSlices];
    // bestPendingUpdate = new uint32_t [numTotalSlices];
    // for (int i = 0; i < numTotalSlices; i++) {
    //     numPendingUpdates[i] = 0;
    //     bestPendingUpdate[i] = -1;
    // }

    // PortProxy vertex_proxy(
    // [this](PacketPtr pkt) {
    //     auto routing_entry = mpuAddrMap.contains(pkt->getAddr());
    //     routing_entry->second->recvFunctional(pkt);
    // }, vertex_atom);

    // panic_if(!vertex_image.write(vertex_proxy), "%s: Unable to write image.");

    // for (auto mpu: mpuVector) {
    //     mpu->postMemInitSetup();
    //     if (!mpu->running() && (mpu->workCount() > 0)) {
    //         mpu->start();
    //     }
    // }
    // workload->iterate();
}

void
GraphInit::ReqPort::sendPacket(PacketPtr pkt)
{
    panic_if(blockedPacket != nullptr,
            "Should never try to send if blocked!");
    // If we can't send the packet across the port, store it for later.
    // DPRINTF(GraphInit, "%s: Port %d: Packet %s "
    //             "sending.\n", __func__, _id, pkt->print());
    
    sendFunctional(pkt);
    // if (!sendTimingReq(pkt))
    // if (!sendFunctional(pkt))
    // {
    //     DPRINTF(GraphInit, "%s: Port %d: Packet %s "
    //             "is blocked.\n", __func__, _id, pkt->print());
    //     blockedPacket = pkt;
    // } else {
    //     DPRINTF(GraphInit, "%s: Port %d: Packet %s "
    //                 "sent.\n", __func__, _id, pkt->print());
    // }
}

bool
GraphInit::ReqPort::recvTimingResp(PacketPtr pkt)
{
    panic("recvTimingResp should not be called at all");
}

void
GraphInit::ReqPort::recvReqRetry()
{
    panic("recvReqRetry should not be called at all");
}

void
GraphInit::recvDoneSignal()
{
    // bool done = true;
    // for (auto mpu : mpuVector) {
    //     done &= mpu->done();
    // }

    // if (done && mode == ProcessingMode::ASYNCHRONOUS) {
    //     exitSimLoopNow("no update left to process.");
    // }

    // if (done && mode == ProcessingMode::BULK_SYNCHRONOUS) {
    //     for (auto mpu: mpuVector) {
    //         mpu->postConsumeProcess();
    //         mpu->swapDirectories();
    //         if (!mpu->running() && (mpu->workCount() > 0)) {
    //             mpu->start();
    //         }
    //     }
    //     workload->iterate();
    //     exitSimLoopNow("finished an iteration.");
    // }

    // if (done && mode == ProcessingMode::POLY_GRAPH) {
    //     DPRINTF(GraphInit, "%s: Received done signal.\n", __func__);
    //     exitSimLoopNow("Finished processing a slice.");
    //     if (!nextSliceSwitchEvent.scheduled()) {
    //         schedule(nextSliceSwitchEvent, nextCycle());
    //     }
    // }
}

bool
GraphInit::handleMemResp(PacketPtr pkt)
{
    panic("handleMemResp should not be called at all");
}

void
GraphInit::recvMemRetry()
{
    panic("recvMemRetry should not be called at all");
}

void
GraphInit::recvFunctional(PacketPtr pkt)
{
    panic("recvFunctional should not be called at all");
}


// float
// GraphInit::getPRError()
// {
//     BSPPRWorkload* pr_workload = dynamic_cast<BSPPRWorkload*>(workload);
//     return pr_workload->getError();
// }

// void
// GraphInit::printAnswerToHostSimout()
// {
//     unsigned int vertex_atom = mpuVector.front()->vertexAtomSize();
//     int num_items = vertex_atom / sizeof(WorkListItem);
//     WorkListItem items[num_items];
//     for (Addr addr = 0; addr < maxVertexAddr; addr += vertex_atom)
//     {
//         PacketPtr pkt = createReadPacket(addr, vertex_atom);
//         auto routing_entry = mpuAddrMap.contains(pkt->getAddr());
//         routing_entry->second->recvFunctional(pkt);
//         pkt->writeDataToBlock((uint8_t*) items, vertex_atom);
//         for (int i = 0; i < num_items; i++) {
//             std::string print = csprintf("WorkListItem[%lu][%d]: %s.", addr, i,
//                                         workload->printWorkListItem(items[i]));

//             std::cout << print << std::endl;
//         }
//         delete pkt;
//     }
// }

// GraphInit::ControllerStats::ControllerStats(GraphInit& _ctrl):
//     statistics::Group(&_ctrl), ctrl(_ctrl),
//     ADD_STAT(numSwitches, statistics::units::Byte::get(),
//              "Number of slices switches completed."),
//     ADD_STAT(switchedBytes, statistics::units::Byte::get(),
//              "Number of bytes accessed during slice switching."),
//     ADD_STAT(switchTicks, statistics::units::Tick::get(),
//              "Number of ticks spent switching slices."),
//     ADD_STAT(switchSeconds, statistics::units::Second::get(),
//              "Traversed Edges Per Second.")
// {
// }

// void
// GraphInit::GraphInitStats::regStats()
// {
//     using namespace statistics;

//     switchSeconds = switchTicks / simFreq;
// }

}
