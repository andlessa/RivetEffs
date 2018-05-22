## Makefile, static linking. Pythia8 is fetched and built
## automatically.
## on a mac, for now please use the DYLD_LIBRARY_PATH variable  
## for pythia8.exe to find the shared object.

homeDIR = $(shell pwd)

CXX      := g++
PYTHIA8HOME := $(homeDIR)/pythia8230
HEPMCHOME := $(homeDIR)
FASTJETHOME := $(homeDIR)
CXXFLAGS := -O3 -I$(PYTHIA8HOME)/include -I$(PYTHIA8HOME)/include/Pythia8/ -I$(HEPMCHOME)/include -I$(FASTJETHOME)/include -I$(ROOTSYS)/include
LDFLAGS  := -L$(PYTHIA8HOME)/lib/ -L$(PYTHIA8HOME)/lib -Wl,-rpath,$(PYTHIA8HOME)/lib
XMLDOC   := $(PYTHIA8HOME)/share/Pythia8/xmldoc


all: main_pythia.exe


main_pythia.exe: main_pythia.cc
	echo $(XMLDOC) > xml.doc
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ main_pythia.cc -lpythia8 -ldl -DGZIPSUPPORT -lz -I$(HEPMCHOME)/include -L$(HEPMCHOME)/lib -Wl,-rpath,$(HEPMCHOME)/lib -lHepMC  -L$(FASTJETHOME)/lib -Wl,-rpath,$(FASTJETHOME)/lib -lfastjet -L$(ROOTSYS)/lib -Wl,-rpath,$(ROOTSYS)/lib `$(ROOTSYS)/bin/root-config --glibs`

