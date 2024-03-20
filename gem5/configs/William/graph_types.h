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
    uint32_t id : 32;
    uint64_t EL_start : 48;
    uint32_t EL_size : 31; // Degree
    bool active : 1;

    Vertex(uint64_t dist, uint64_t id, uint64_t EL_start, uint32_t EL_size, bool active):
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



struct __attribute__ ((packed)) AL_element
{
    uint16_t dist : 15;
    // uint16_t id : 10; // dont need this
    uint32_t EL_start : 32;
    uint16_t EL_size : 16; // Degree
    bool active : 1;
   

    AL_element(uint16_t dist, uint32_t EL_start, uint16_t EL_size, bool active):
        dist(dist),
        EL_start(EL_start),
        EL_size(EL_size),
        active(active)
    {} 

    std::string to_string() {
      std::string ret = "";
      ret += "AL_element{dist: " + std::to_string(dist) + ", El_start: " +
              std::to_string(EL_start) + "}";
      return ret;
    }
};

typedef AL_element AL_vector[8];
// struct __attribute__ ((packed)) Al_vector
// {
//     // uint16_t weight : 16;
//     // uint64_t dst_id : 48;
//     //uint64_t src_id : 48;

//     AL_element v1[8];
//     // AL_element v2;
//     // AL_element v3;
//     // AL_element v4;
//     // AL_element v5;
//     // AL_element v6;
//     // AL_element v7;
//     // AL_element v8;

//     // std::string to_string()
//     // {
//     //     //return csprintf("Update{weight: %u, dst_id: %lu}", weight, dst_id);
//     // }

//     Al_vector(): v1{*AL_element(0, 0, 0, 0)}//, v2(AL_element(0,0)), v3(AL_element(0,0)), v4(AL_element(0,0)), v5(AL_element(0,0)), v6(AL_element(0,0)), v7(AL_element(0,0)), v8(AL_element(0,0)) {}

//     Al_vector(AL_element* my_v1)://, AL_element my_v2, AL_element my_v3, AL_element my_v4, AL_element my_v5, AL_element my_v6, AL_element my_v7, AL_element my_v8):
//         v1(my_v1)// ,
//         // v2(my_v2),
//         // v3(my_v3),
//         // v4(my_v4),
//         // v5(my_v5),
//         // v6(my_v6),
//         // v7(my_v7),
//         // v8(my_v8)
//     {}
// };

struct __attribute__ ((packed)) Update
{
    // uint16_t weight : 16;
    // uint64_t dst_id : 48;
    //uint64_t src_id : 48;

    uint16_t weight : 16;
    uint64_t dst_id : 48;

    // std::string to_string()
    // {
    //     //return csprintf("Update{weight: %u, dst_id: %lu}", weight, dst_id);
    // }

    Update(): weight(0), dst_id(0) {}

    Update(uint16_t weight, uint64_t dst_id):
        weight(weight),
        dst_id(dst_id)
    {}
};


struct __attribute__ ((packed)) Update_vector
{
    // uint16_t weight : 16;
    // uint64_t dst_id : 48;
    //uint64_t src_id : 48;

    Update v1;
    Update v2;
    Update v3;
    Update v4;
    Update v5;
    Update v6;
    Update v7;
    Update v8;

    // std::string to_string()
    // {
    //     //return csprintf("Update{weight: %u, dst_id: %lu}", weight, dst_id);
    // }

    Update_vector(): v1(Update(0,0)), v2(Update(0,0)), v3(Update(0,0)), v4(Update(0,0)), v5(Update(0,0)), v6(Update(0,0)), v7(Update(0,0)), v8(Update(0,0)) {}

    Update_vector(Update my_v1, Update my_v2, Update my_v3, Update my_v4, Update my_v5, Update my_v6, Update my_v7, Update my_v8):
        v1(my_v1),
        v2(my_v2),
        v3(my_v3),
        v4(my_v4),
        v5(my_v5),
        v6(my_v6),
        v7(my_v7),
        v8(my_v8)
    {}
};

typedef Update outgoing_msgs[8];