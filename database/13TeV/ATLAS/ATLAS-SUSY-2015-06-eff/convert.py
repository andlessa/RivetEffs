#!/usr/bin/env python

"""
.. module:: convert
   :synopsis: used to create info.txt and the <txname>.txt files.

"""
import sys
import os
import argparse

argparser = argparse.ArgumentParser(description = \
'create info.txt, txname.txt, twiki.txt and sms.py')
argparser.add_argument ( '-utilsPath', '--utilsPath',
			                   help = 'path to the package smodels_utils',\
					               type = str )
argparser.add_argument ( '-smodelsPath', '--smodelsPath',
			                   help = 'path to the package smodels_utils',\
                         type = str )
argparser.add_argument ('-t', '--ntoys',
    help = 'number of toys to throw',\
    type = int, default=200000  )
args = argparser.parse_args()

if args.utilsPath:
    utilsPath = args.utilsPath
else:
    databaseRoot = '../../../'
    sys.path.append(os.path.abspath(databaseRoot))
    from utilsPath import utilsPath
    utilsPath = databaseRoot + utilsPath

if args.smodelsPath:
    sys.path.append(os.path.abspath(args.smodelsPath))

sys.path.append(os.path.abspath(utilsPath))
from smodels_utils.dataPreparation.inputObjects import MetaInfoInput,DataSetInput
from smodels_utils.dataPreparation.databaseCreation import databaseCreator
from smodels_utils.dataPreparation.massPlaneObjects import x, y, z

DataSetInput.ntoys = args.ntoys

#+++++++ global info block ++++++++++++++
info = MetaInfoInput('ATLAS-SUSY-2015-06')
info.url = 'http://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/SUSY-2015-06/'
info.sqrts = 13
info.lumi = 3.2
info.prettyName = '2-6 jets, 0 lep'
info.private = False
info.arxiv =  'https://arxiv.org/abs/1605.03814'
info.contact = 'ATLAS collaboration'
info.publication = 'http://link.springer.com/article/10.1140/epjc/s10052-016-4184-8'
info.comment = 'Efficiency maps created using Pythia 8.230 and Rivet 2.6.0'
#info.supersedes =
#info.supersededBy =

datasets = {"SR2jl": {'observedN' : 263, 'expectedBG' : 283, 'bgError' : 24, 'index' : 0},
            "SR2jm": {'observedN' : 191, 'expectedBG' : 191, 'bgError' : 21, 'index' : 1},
            "SR2jt": {'observedN' : 26, 'expectedBG' : 23, 'bgError' :  4, 'index' : 2},
            "SR4jt": {'observedN' : 7, 'expectedBG' : 4.1, 'bgError' : 1.1, 'index' : 3},
            "SR5j": {'observedN' : 7, 'expectedBG' : 13.2, 'bgError' : 2.2, 'index' : 4},
            "SR6jm": {'observedN' : 4, 'expectedBG' : 6.9, 'bgError' : 1.5, 'index' : 5},
            "SR6jt": {'observedN' : 3, 'expectedBG' : 4.2, 'bgError' : 1.2, 'index' : 6}}

for SR,data in datasets.items():
    #+++++++ dataset block ++++++++++++++
    dataset = DataSetInput(SR)
    dataset.setInfo(dataType = 'efficiencyMap', dataId = SR, observedN = data['observedN'], 
                     expectedBG = data['expectedBG'] , bgError = data['bgError'])
    T1 = dataset.addTxName('T1')
    T1.checked = 'NO'
    T1.constraint ="[[['jet','jet']],[['jet','jet']]]"
    T1.conditionDescription = None
    T1.condition = None
    T1.source = "SModelS"
    #+++++++ next mass plane block ++++++++++++++
    T1_1 = T1.addMassPlane( [[x,y]]*2 )
    T1_1.addSource('efficiencyMap', 'orig/ATLAS_2016_I1458270_eff.dat', 'txt', 
                    coordinateMap = {x : 0, y : 1, 'eff' : data['index']+2})
    T1_1.addSource( 'obsExclusion', 'orig/Obs_Line_T1.dat', 'txt')
    T1_1.addSource( 'expExclusion', 'orig/Exp_Line_T1.dat', 'txt')
databaseCreator.create()

