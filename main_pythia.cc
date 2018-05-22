// An example recasting code for applying the selection from ATLAS-CONF-2017-026

#include <iostream>
#include "Pythia8/Pythia.h"
#include "Pythia8Plugins/HepMC2.h"
#include <algorithm>
#include <stdlib.h>
#include <ctime>
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>


using namespace Pythia8;


int run(int nevents, const string & cfgfile, const string & infile,
		 const string & outfile)
{

  // Interface for conversion from Pythia8::Event to HepMC event.
  HepMC::Pythia8ToHepMC ToHepMC;

  // Specify file where HepMC events will be stored.
//  if ( outfile.find(".fifo") != std::string::npos ){ 
//      mkfifo(outfile.c_str(),0666);
//  }
  HepMC::IO_GenEvent ascii_io(outfile, std::ios::out);


  std::srand(500);
  // Generator. Shorthand for the event.
  Pythia pythia("",false); //Set printBanner to false
  Event& event = pythia.event;
  pythia.readFile( cfgfile );
  if ( infile.find(".slha") != std::string::npos ){
    cout << "Using SLHA file as input" << endl;
    pythia.readString("SLHA:file = " + infile);
    if ( nevents < 0) {
    	nevents = 100;
    	cout << "Negative number of events for SLHA input. Setting nevents to " << nevents << endl;
    }
  }
  else{
    cout << "Using LHE file as input" << endl;
    pythia.readString("Beams:frameType = 4");
    pythia.readString("Beams:LHEF = " + infile);
  }


  //Get access to particle data:
  ParticleData& pData = pythia.particleData;

  // Initialize.
  pythia.init();


  int iAbort = 0;
  float nCuts = 0.;

  // Begin event loop.
  int iEvent = 0;
  while (iEvent < nevents or nevents < 0){

    // Generate events. Quit if failure.
    if (!pythia.next()) {
      if (pythia.info.atEndOfFile()) break;
      if (++iAbort < 10) continue;
      cout << " Event generation aborted prematurely, owing to error!\n";
      break;
    }
    ++iEvent;

    // Construct new empty HepMC event and fill it.
    // Units will be as chosen for HepMC build; but can be changed
    // by arguments, e.g. GenEvt( HepMC::Units::GEV, HepMC::Units::MM)
    HepMC::GenEvent* hepmcevt = new HepMC::GenEvent();
    ToHepMC.fill_next_event( pythia, hepmcevt );

    // Write the HepMC event to file. Done with it.
    ascii_io << hepmcevt;
    delete hepmcevt;

  // End of event loop.
  }

  // Final statistics, flavor composition and histogram output.
  pythia.stat();

  // Done.
  return 0;
}


void help( const char * name )
{
	  cout << "syntax: " << name << " [-h] [-f <slhafile/lhefile>] [-n <number of events>] [-c <pythia cfg file>]" << endl;
	  cout << "        -f <slhafile/lhefile>:  input SLHA or LHE file [test.slha]" << endl;
	  cout << "        -o <outputfile>:  output HepMC file [out.hepmc]" << endl;
	  cout << "        -c <pythia config file>:  pythia config file [pythia8.cfg]" << endl;
	  cout << "        -n <number of events>:  Number of events to be generated. If negative, run all events in LHE input [-1]" << endl;
  exit( 0 );
};

int main( int argc, const char * argv[] ) {
  float weight = 1.;
  int nevents = -1;
  string slhafile = "test.slha";
  string outfile = "out.hepmc";
  string cfgfile = "pythia8.cfg";
  for ( int i=1; i!=argc ; ++i )
  {
    string s = argv[i];
    if ( s== "-h" )
    {
      help ( argv[0] );
    }

    if ( s== "-c" )
    {
      if ( argc < i+2 ) help ( argv[0] );
      cfgfile = argv[i+1];
      i++;
      continue;
    }


    if ( s== "-n" )
    {
      if ( argc < i+2 ) help ( argv[0] );
      nevents = atoi(argv[i+1]);
      i++;
      continue;
    }


    if ( s== "-f" )
    {
      if ( argc < i+2 ) help ( argv[0] );
      slhafile = argv[i+1];
      i++;
      continue;
    }
    if ( s== "-o" )
    {
      if ( argc < i+2 ) help ( argv[0] );
      outfile = argv[i+1];
      i++;
      continue;
    }


    cout << "Error. Argument " << argv[i] << " unknown." << endl;
    help ( argv[0] );
  };

  int r = run(nevents, cfgfile, slhafile, outfile);

  return 0;
}
