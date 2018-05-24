# RivetEffs
Holds the basic code to compute efficiencies using Rivet

## Basic Installation ##

The following codes must be installed:
  * [Rivet](https://rivet.hepforge.org/)
  * [HepMC](http://lcgapp.cern.ch/project/simu/HepMC/)
  * [FastJet](http://fastjet.fr/)
  * [Pythia8](http://home.thep.lu.se/~torbjorn/pythia8/)

The script installer.sh will try to fetch the appropriate tarballs and install them.



## Running ##

For computing efficiencies from SLHA files using Pythia and Rivet:

```
./runGetEffs.py -p <parfile>
```

The above code takes a parameter file
(eff_parameters.ini), where several parameters are defined (default parameters are defined
in [eff_parameters_default.ini](./eff_parameters_default.ini).
It will then run Pythia and Rivet for a specific analyses or set of analyses, resulting in
a yoda file (or a list of yoda files if the input is a folder).

The parameter file accepts a list of inputFiles. In this case Pythia and Rivet will be run in parallel
for each file, according to the number of cpu (processes) set in options.

A set of yoda files can then be used to extract an efficiency map using:

```
./yodaParser.py -f <yodaFolder> -s <slhaFolder> -x <pdg for x-axis mass> -y <pdg for y-axis mass>
```

The output is a text file with a simple table of efficiencies for each signal region as
a function of the defined x and y masses.

