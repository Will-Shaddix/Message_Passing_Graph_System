#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include "../../graph_types.h"
#include <fstream>
#include <deque>
#include <string>
#include <iostream>
#include <cstring>
#include <cstdint>

#ifdef GEM5
#include "gem5/m5ops.h"
#endif

using namespace std;

// Static VA for EL, VL, MessageQueues, and initilization

const uint64_t buffer_addr = 0x100000000; // change buffer_addr to MessageQueues[], add 4096 to each message queue
const uint64_t EL_addr = 0x600000000;
const uint64_t VL_addr = 0x2000000000;
const uint64_t initalized_addr = 0x200000000;
const uint64_t finished_addr = 0x300000000;
const uint64_t finished_flag = 0x310000000;
const uint64_t activeList_addr = 0x400000000;

const uint64_t buffer_size = 4096;
const uint64_t activeList_size = 65536;
// 
// Steps for generator:
/*
    Spin on initilized addr until an update is seen
    read the num_vertices from initialized_addr
    based on generator_id figure out which active list belongs to you
    Loop:
        Monitor active list for an update
        Upon seeing an update read in the src_id and find the appropriate place on the EL
        Begin writing messages
    If idle for too long, update finished_Addr based on gen id

*/

int main(int argc, char* argv[]){

    uint64_t generator_id = 0;
    uint32_t active_list_len = uint32_t(activeList_size/sizeof(Vertex));
    uint16_t num_msgQueues = 2;

    uint32_t num_msgs_sent = 0;
    uint32_t num_activeList_updates = 0; // number of times active list was updated
    // uint32_t num_full_activeList = 0;

    uint64_t size_of_partion = 127; // 127 for fb with 32 partions, 2541 for short_32

    uint8_t edge_partitioned = 0;
    // uint32_t vertices_per_partition;

    if(argc > 1){
        generator_id = atoi(argv[1]);
        printf("generator_id: %ld\n", generator_id);
    }
    else{
        printf("Please enter a generator id\n");
        return 0;
    }

    if(argc > 2){
        num_msgQueues = atoi(argv[2]);
    }
    if(argc > 4){
        edge_partitioned = atoi(argv[3]);
        size_of_partion = atoi(argv[4]);

    }

    Update my_out_msg_queues[num_msgQueues][8]; // batching
    uint8_t indices[num_msgQueues] = {0}; // batching

    uint8_t* done = (uint8_t*)(finished_addr+(2*generator_id));// need to fix this, doesnt account for consumers
    //spin on initialized_addr until an update is seen
    
    uint64_t* initialized = (uint64_t*)initalized_addr;

    if(generator_id == 0){
        #ifdef GEM5
            printf("Resetting stats from generator!\n");    
            m5_reset_stats(1, 1<<51);
        #endif
    }



    while(*initialized == 0){
    }
    // uint64_t num_vertices = *initialized;

    Update* messageQueue = (Update*)(buffer_addr); 
    // // identifies address of active list
    // Vertex* activeList = (Vertex*)(activeList_addr + (generator_id*activeList_size));
    AL_element* activeList = (AL_element*)(activeList_addr + (generator_id*activeList_size));


    // Vertex* VL = (Vertex*)VL_addr;
    printf("generator id: %d EL_offset %lu \n",generator_id, edge_partitioned*generator_id * 1024*1024*512);
    Edge* EL = (Edge*)(EL_addr + (edge_partitioned*generator_id * 1024*1024*512)); // 512 MiB per generator
    printf("EL_addr: %p\n", EL);

    uint8_t* finish_flag = (uint8_t*)finished_flag;

    uint8_t g_flag = 0;

    string to_print;
    // int src_id, dst_id, weight;
    // bool printed = false;
    int index = 0; 
    int empty_cycles = 0;
    Update* temp_up = new Update(0,0);
    Update_vector* temp_msgQueue;
    Vertex curr_update = Vertex(0,0,0,0,0);// = activeList[index];
    AL_element curr_al_update = AL_element(0,0,0,0);
    Update_vector* transition = (Update_vector*)malloc(sizeof(Update_vector)); // batching
    

    uint16_t q_sel = 0;
        // printf(" generator id: %d  active_list addr = %p, other pointers: %p, %lu \n",generator_id, activeList,  transition, messageQueue);

            // while(g_flag != 1){
            while(1){

                // curr_update = activeList[index];
                curr_al_update = activeList[index];
                index = (index+1) % 1024;
                
                // if(activeList[index].active == true){
                if(curr_al_update.active == true){
                    // if(curr_al_update.dist == 8192){
                    //     break;
                    // }
                    // printf("Received an update from active list: EL_start: %d  EL_size: %d  distance: %d\n", curr_al_update.EL_start, curr_al_update.EL_size, curr_al_update.dist);
                    empty_cycles = 0;
                    *done = 0;
                    // Vertex curr_update = activeList[index];
                    // activeList[index].active = false;

                    
                    for(uint64_t i = curr_al_update.EL_start; i < curr_al_update.EL_start + curr_al_update.EL_size; i++){
                        temp_up->weight = curr_al_update.dist + EL[i].weight;
                        temp_up->dst_id = EL[i].neighbor;

                        // q_sel = temp_up->dst_id % num_msgQueues; // batching
                        q_sel = temp_up->dst_id / size_of_partion; // batching
                        my_out_msg_queues[q_sel][indices[q_sel]] = *temp_up; //batching
                                                    
                        if(indices[q_sel] == 7){ // batching
                            indices[q_sel] = 0; // batching
                            temp_msgQueue = (Update_vector*)(buffer_addr + (buffer_size*(q_sel))); // batching
                            // printf("temp_msg_queue addr: %p\n", temp_msgQueue); // batching
                            *transition = {my_out_msg_queues[q_sel][0], my_out_msg_queues[q_sel][1], 
                                                            my_out_msg_queues[q_sel][2], my_out_msg_queues[q_sel][3],
                                                            my_out_msg_queues[q_sel][4], my_out_msg_queues[q_sel][5],
                                                            my_out_msg_queues[q_sel][6], my_out_msg_queues[q_sel][7],}; // batching
                            temp_msgQueue[0] = *transition; // batching
                            // memcpy(&temp_msgQueue, transition, sizeof(Update_vector)); // batching
                            // memcpy(&temp_msgQueue, &my_out_msg_queues[q_sel], 8*sizeof(Update)); // batching

                            // printf("generator id: %d, sending message batch to msg_q %d\n", generator_id, q_sel); // batching
                        } // batching
                        else{ // batching
                            indices[q_sel]++; // batching
                        } // batching

                        //to figure out which threads queue to update, we take the dst_id divided by (vertices per thread)
                        // temp_msgQueue = (Update*)(buffer_addr + (buffer_size*(temp_up->dst_id % num_msgQueues)));

                        // *temp_msgQueue = *temp_up; // check address?                     

                    }

                    // num_activeList_updates++;

                }
                else{
                    empty_cycles++;
                    if (empty_cycles > 15000){
                        *done = 1;
                        // g_flag = finish_flag[0];

                    }
                    // do nothing

                }
            }

 printf("generator id: %d done!", generator_id);
    // printf("generator id: %d done!  # of messages sent: %d, # of activeList reads: %d, activelist index = %d\n", generator_id, num_msgs_sent, num_activeList_updates, index);

}