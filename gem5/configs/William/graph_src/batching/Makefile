CXX=g++
CXXFLAGS=-Wall -Wextra -pedantic -std=c++11
#GEM5_ROOT ?= ../../../../gem5
GEM5_ROOT ?= /home/wshaddix/numa_gem5/gem5

counter: counter.cpp
	$(CXX) $(CXXFLAGS) -o counter counter.cpp

counter-gem5: counter.cpp
	$(CXX) $(CXXFLAGS) -o counter counter.cpp -static -I$(GEM5_ROOT)/include -DGEM5 -L$(GEM5_ROOT)/util/m5/build/x86/out -lm5

consumer: consumer.cpp
	$(CXX) $(CXXFLAGS) -o consumer consumer.cpp

generator: generator.cpp
	$(CXX) $(CXXFLAGS) -o generator generator.cpp

generator_al: generator_al.cpp
	$(CXX) $(CXXFLAGS) -o generator_al generator_al.cpp

generator_al_partition: generator_al_partioned.cpp
	$(CXX) $(CXXFLAGS) -o generator_al_partitioned generator_al_partioned.cpp
	
consumer_al_partition: consumer_al_partioned.cpp
	$(CXX) $(CXXFLAGS) -o consumer_al_partitioned consumer_al_partioned.cpp

generator_partition_asm: generator_al_partioned.cpp
	$(CXX) $(CXXFLAGS)  -S -fverbose-asm -o generator_partitioned_asm generator_al_partioned.cpp

consumer_partition_asm: consumer_al_partioned.cpp
	$(CXX) $(CXXFLAGS)  -S -fverbose-asm -o consumer_partitioned_asm consumer_al_partioned.cpp

generator-gem5: generator_al.cpp
	$(CXX) $(CXXFLAGS) -o generator_al generator_al.cpp -static -I$(GEM5_ROOT)/include -DGEM5 -L$(GEM5_ROOT)/util/m5/build/x86/out -lm5

consumer_al: consumer_al.cpp
	$(CXX) $(CXXFLAGS) -o consumer_al consumer_al.cpp

consumer_asm: consumer_al.cpp
	$(CXX) $(CXXFLAGS)  -S -fverbose-asm -o consumer_asm consumer_al.cpp

generator_asm: generator_al.cpp
	$(CXX) $(CXXFLAGS)  -S -fverbose-asm -o generator_asm generator_al.cpp

counter_asm: counter.cpp
	$(CXX) $(CXXFLAGS)  -S -fverbose-asm -o counter_asm counter.cpp

consumer_batch: consumer_batch.cpp
	$(CXX) $(CXXFLAGS) -o consumer_batch consumer_batch.cpp

al: generator_al consumer_al

# make all 
all: counter consumer generator

all-gem5: counter-gem5 consumer generator

clean:
	rm -f counter consumer generator
	