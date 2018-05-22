#!/usr/bin/env python

#Uses a parameter file to compute the corresponding efficiencies.
#The calculation goes through the following steps
# 1) Run Pythia (main_pythia.exe) using an SLHA file and pythia card file as inputs
# 2) Runs Rivet along with pythia
# 3) Runs yodaParser.py to read Rivet output and convert it to a efficiency table

#First tell the system where to find the modules:
import sys,os
from configParserWrapper import ConfigParserExt
import logging
import subprocess
import time,datetime
import itertools
import multiprocessing

FORMAT = '%(levelname)s in %(module)s.%(funcName)s() in %(lineno)s: %(message)s at %(asctime)s'
logging.basicConfig(format=FORMAT,datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)

    

  

def Run_pythia(parser,inputFile):
    """
    Runs Pythia8 using the parameters given in parser
    and the input SLHA file 
   
    :param parser: ConfigParser object with all the parameters needed
    :param inputFile: path to the SLHA file
    """
    
    pars = parser.toDict(raw=False)["PythiaOptions"]    
    if not os.path.isfile(pars['execfile']):
        logger.error('Pythia executable %s not found' %pars['execfile'])
        return False
    
    if not os.path.isfile(pars['pythiacfg']):
        logger.error('Pythia config file %s not found' %pars['pythiacfg'])
        return False
    
    #Create output dirs, if do not exist:
    try:
        os.makedirs(os.path.dirname(pars['pythiaout']))
    except:
        pass
    
    
    #Run Pythia
    logger.info('Running pythia for %s' %inputFile)
    #Create FIFO file
    if os.path.isfile(pars['pythiaout']):
        os.remove(pars['pythiaout'])
    os.system('mkfifo %s' %pars['pythiaout'])
    subprocess.Popen('./%s -f %s -c %s -o %s -n %s &' %(pars['execfile'],
                                                          inputFile,pars['pythiacfg'],pars['pythiaout'],pars['nevts'])
                           ,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    


def Run_rivet(parser):
    """
    Runs Rivet using the parameters given in parser
   
    :param parser: ConfigParser object with all the parameters needed
    """
    
    fifoFile = parser.toDict(raw=False)["PythiaOptions"]['pythiaout']
    pars = parser.toDict(raw=False)["RivetOptions"]    
    
    #Create output dirs, if do not exist:
    try:
        os.makedirs(os.path.dirname(pars['rivetout']))
    except:
        pass
    
    
    #Run Pythia
    logger.info('Running Rivet for %s' %fifoFile)
    run = subprocess.Popen('rivet %s -a %s -o %s' %(fifoFile,pars['analyses']
                                                            ,pars['rivetout'])
                           ,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    
    os.remove(fifoFile)    
    output,errorMsg= run.communicate()
    logger.debug('Rivet error:\n %s \n' %errorMsg)
    logger.debug('Rivet output:\n %s \n' %output)
     
    logger.info("Finished Rivet run")


def runAll(parserDict):
    """
    Runs Madgraph, Pythia and the SLHA creator for a given set of options.
    :param parserDict: a dictionary with the parser options.
    """
    
    t0 = time.time() 
    
    parser = ConfigParserExt()
    parser.read_dict(parserDict)    
  
    #Run Pythia
    if parser.getboolean("options","runPythia"):
        inputFile = parser.getstr("PythiaOptions","inputFile")
        if not os.path.isfile(inputFile):
            logger.error("Input file %s for Pythia not found" %inputFile)
        else:                
            Run_pythia(parser, inputFile)
            logger.debug("Pythia run submitted")
                
    #Run Rivet:
    if parser.getboolean("options","runRivet"):    
        Run_rivet(parser)
        logger.debug("Rivet run submitted")

          
    logger.info("Done in %3.2f min" %((time.time()-t0)/60.))
    now = datetime.datetime.now()
    
    return "Finished run at %s" %(now.strftime("%Y-%m-%d %H:%M"))



if __name__ == "__main__":

    import argparse    
    ap = argparse.ArgumentParser( description=
            "Run Pythia and Rivet in order to compute efficiencies for a given model." )
    ap.add_argument('-p', '--parfile', default='eff_parameters_default.ini',
            help='path to the parameters file. Parameters not defined in the parfile will be read from eff_parameters_default.ini')
    ap.add_argument('-l', '--loglevel', default='error',
            help='verbose level (debug, info, warning or error). Default is error')


    t0 = time.time()

    args = ap.parse_args()
    
    level = args.loglevel.lower()
    levels = { "debug": logging.DEBUG, "info": logging.INFO,
               "warn": logging.WARNING,
               "warning": logging.WARNING, "error": logging.ERROR }
    if not level in levels:
        logger.error ( "Unknown log level ``%s'' supplied!" % level )
        sys.exit()
    logger.setLevel(level = levels[level])    

    parser = ConfigParserExt( inline_comment_prefixes=( ';', ) )
    ret = parser.read('eff_parameters_default.ini')   
    ret = parser.read(args.parfile)
    if ret == []:
        logger.error( "No such file or directory: '%s'" % args.parfile)
        sys.exit()
        
    
    ncpus = parser.getint("options","ncpu")
    if ncpus  < 0:
        ncpus =  multiprocessing.cpu_count()

    pool = multiprocessing.Pool(processes=ncpus)
    children = []
    #Loop over model parameters and submit jobs
    inputFiles = parser.get("PythiaOptions","inputFile")
    try:
        inputFiles = eval(inputFiles)
    except:
        pass
    if not isinstance(inputFiles,list):
        inputFiles = [inputFiles]
    for infile in inputFiles:
        print('Running for',infile)
        newParser = ConfigParserExt()
        newParser.read_dict(parser.toDict())       
        newParser.set("PythiaOptions","inputFile",infile)
        parserDict = newParser.toDict(raw=False) #Must convert to dictionary for pickling
        runAll(parserDict)
        p = pool.apply_async(runAll, args=(parserDict,))        
        children.append(p)
        if len(children) == 1:
            #Compile pythia code just once:
            if parser.get("PythiaOptions",'execfile') != 'None':
                os.system("make %s" %parser.get("PythiaOptions",'execfile'))            
            time.sleep(15)  #Let first job run for 15s in case it needs to create shared folders
       
    #Wait for jobs to finish:
    print('child=',len(children))
    output = [p.get() for p in children]
    for out in output:
        print(out)

    print("\n\nDone in %3.2f min" %((time.time()-t0)/60.))
            
