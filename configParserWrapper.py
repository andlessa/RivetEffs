#!/usr/bin/env python

#A wrapper for ConfigParser which allows to evaluate expressions
#in the parameters. The expressions should be of the type ${expr}.
#References for other parameters in the parser should be in the format section:parameter.

from configparser import SafeConfigParser,ExtendedInterpolation


class ConfigParserExt(SafeConfigParser):
    
    
    def __init__(self,*args,**kargs):
        SafeConfigParser.__init__(self,*args,**kargs)
        self._interpolation = ExtendedInterpolation()
        self.optionxform = str


    def toDict(self,raw=True):
        """
        Convert parser to dictionary.
        If raw=True, will return the raw values, otherwise it will
        try to evaluate them.
        """
        
        parserDict = {}
        for s in self.sections():
            parserDict[s] = {}
            for var in self.options(s):
                parserDict[s][var] = self.get(s,var,raw=raw)
        
        return parserDict
        
    def get(self,*args,**kargs):
        """
        Return value with expressions evaluated
        """
        
        #First try to call get directly
        try:
            val = super(SafeConfigParser, self).get(*args,**kargs)
            return val
        #If fails, get the raw expression and try to evaluate it.
        except:
            if not kargs:
                kargs = {}
            kargs['raw'] = True
            #Get raw expression:
            val = super(SafeConfigParser, self).get(*args,**kargs)            
            expr = val[:]
            
            maxrecursion = 100*len(self.sections())
            irec = 0
            while "${" in expr and irec < maxrecursion:
                irec += 1
                exprBlock = expr[expr.find("${")+2:expr.find("}",expr.find("${"))]
                exprNew = exprBlock[:]
                #Get values for variables appearing in exprBlock
                for s in self.sections():
                    for var in self.options(s):
                        varName = "%s:%s" %(s,var)
                        if varName in exprNew:
                            exprNew = exprNew.replace(varName,str(self.get(s,var)))
                try:
                    v = eval(exprNew)                    
                except:
                    v = exprNew
                expr = expr.replace("${"+exprBlock+"}",str(v)) 
            
            if irec == maxrecursion:
                print("ERROR:::Could not evaluate expression: %s \nAre expression defined recursively?" %val)

            return expr
        
    def getstr(self,*args,**kargs):
        
        return str(self.get(*args,**kargs))
        



if __name__ == "__main__":
    
    parFile = 'eff_parameters_default.ini'
    
    parser = ConfigParserExt( inline_comment_prefixes=( ';', ) )
    ret = parser.read(parFile)
    ret = parser.read('slha-parameters.ini')
    
#     print(parser.get("MadGraphPars","mg5out"))
    print(parser.options("slhaCreator-replace"))
    
    
    
            