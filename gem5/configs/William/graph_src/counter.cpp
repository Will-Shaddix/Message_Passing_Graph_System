#include <stdio.h>
#include <stdlib.h>
#include "../graph_types.h"
#include <fstream>

#ifdef GEM5
#include "gem5/m5ops.h"
#endif

const uint64_t buffer_addr = 0x100000000; // change buffer_addr to MessageQueues[], add 4096 to each message queue
const uint64_t EL_addr = 0x600000000;
const uint64_t VL_addr = 0x2000000000;
const uint64_t initalized_addr = 0x200000000;
const uint64_t finished_addr = 0x300000000;
const uint64_t finished_flag = 0x310000000;
const uint64_t activeList_addr = 0x400000000;

const uint64_t msg_queue_size = 4096;
const uint64_t activeList_size = 65536;


int main(int argc, char* argv[]) {

    // Dont use with gem5!!!!
    // Edge* EL = (Edge*)malloc(4096 * sizeof(Edge) * 200);
    // Vertex* VL = (Vertex*)malloc(4096 * sizeof(Vertex) * 2);
#ifdef GEM5
printf("GEM5 is defined\n");
#endif
    uint16_t num_cores = 2;

    if(argc > 1){
        num_cores = atoi(argv[1]);
    }

    Update* messageQueue = (Update*)(buffer_addr); 
    AL_element* activeList = (AL_element*)activeList_addr;

    


    // Your code here
    
    Edge* EL = (Edge*)EL_addr;
    Vertex* VL = (Vertex*)VL_addr;
    uint64_t* initalized = (uint64_t*)initalized_addr;
    uint8_t* finished = (uint8_t*)finished_addr;
    uint8_t* finish_flag = (uint8_t*)finished_flag;
    finish_flag[0] = 0;

    bool is_Weighted = false;
    uint64_t num_nodes = 81305;
    uint64_t EL_start;

    uint16_t initial = 0;

    printf("starting waiting loop!\n");
    for(int i = 0; i < 220000; i++){
        num_nodes++;
        // if(i % 5000 == 0){
        //     printf("i = %d\n", i);
        // }
    }

    #ifdef GEM5
        printf("Resetting stats!\n");    
        m5_reset_stats(1, 1<<51);
    #endif
    
    Update initial_update = Update(0, initial);
    *messageQueue = initial_update;

    printf("writing to initalized\n");
    *initalized = num_nodes;
    
    uint64_t done = 0;
    uint64_t counter = 0;
    uint64_t print_counter = 0;
    
    while(counter < 50){
        print_counter++;
        done = finished[0];
        for(int j = 1; j <10000;j++){

        }

        for(int i = 1; i < num_cores; i++){
            if(print_counter%20000 == 0){
                printf("Finished[%d] = %d\n", i, finished[i]);
            }
            done &= finished[i];
        }

        if(print_counter%20000 == 0){
                printf("\n");
            }
        
        if(done == 1){
            if(VL[1].dist != 65535){
                counter++;
            }
        }
        else{
            counter = 0;
        }
    }


    // int prints[6] = {4038, 3927, 3271, 591, 3709, 1524}; // random vALUES TO CHECK CORRECTNESS
        int prints[6] = {1, 10, 32, 67, 89, 103}; // random vALUES TO CHECK CORRECTNESS


    for(int i = 0; i < 6; i++){
        printf("VL[%d]: dist: %d, id: %d\n", prints[i], VL[prints[i]].dist, VL[prints[i]].id);
    }
            


    #ifdef GEM5
        m5_exit(0);
    #endif
    
    printf("Writing to finish flag!\n");
    // shared flag implementation
    finish_flag[0] = 1;

    //AL 8192 for dist
    AL_element al_update = AL_element(8192, 1, 1, 1);
    Update done_update = Update(8192, 0);

    for(int z = 0; z < (num_cores/2); z++){
        messageQueue = (Update*)(buffer_addr + (z*msg_queue_size));
        activeList = (AL_element*)(activeList_addr + (z*activeList_size));
        *messageQueue = done_update;
        *activeList = al_update;
    }

    return 0;
}
