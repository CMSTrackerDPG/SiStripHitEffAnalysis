#!/usr/bin/env python
from ROOT import * 
import os
import argparse
import pickle


# Inside of afsdir, there is a folder for each run number that contain the logs we want to parse.  A list of directories is made from the directories in there and used to make a list of runs.  The runlist is then sorted so they are in chronological order.

afsdir='/afs/cern.ch/work/j/jthieman/public/HitEfficiency/GR18'
dirlist = os.listdir(afsdir)
globalrunlist=[dir.lstrip('run_') for dir in dirlist if dir.startswith('run_')]
globalrunlist.sort()
#print(' '.join(globalrunlist)) 

# Load in the Module : Power Supply Dict
pickle_modulepowersupply = open("modulepowersupply.pkl","r")
modulepowersupplydict = pickle.load(pickle_modulepowersupply)
pickle_modulepowersupply.close()

# Load in the Module : Power Supply Alias Dict
#pickle_modulepowersupplyalias = open(os.getenv("CMSSW_RELEASE_BASE")+"/src/CalibTracker/SiStripDCS/data/StripDetIDAlias.pkl","r")
pickle_modulepowersupplyalias = open("StripDetIDAlias.pkl","r")
modulepowersupplyaliasdict = pickle.load(pickle_modulepowersupplyalias)
pickle_modulepowersupplyalias.close()

# A list of all the subsystems

subsyslist = ["TIBL1", "TIBL2", "TIBL3", "TIBL4", 
              "TOBL1", "TOBL2", "TOBL3", "TOBL4", "TOBL5", "TOBL6", 
              "TIDD1", "TIDD2", "TIDD3", 
              "TECD1", "TECD2", "TECD3", "TECD4", "TECD5", "TECD6", "TECD7", "TECD8", "TECD9",
              # "Tracker", "TIB", "TOB", "TID", "TEC"
             ]

# A dictionary that has the subsystems as the keys, and the number of modules in those subsystems as the values

subsystotalmodules = {'TECD1': 816.0, 'TOBL2': 1152.0, 'TECD3': 816.0, 'TECD2': 816.0, 'TECD5': 720.0, 'TECD4': 720.0, 'TECD7': 624.0, 'TECD6': 720.0, 'TIDD2': 272.0, 'TIDD3': 272.0, 'TIDD1': 272.0, 'TOBL5': 792.0, 'TID': 816.0, 'Tracker': 15148.0, 'TOB': 5208.0, 'TECD9': 544.0, 'TIB': 2724.0, 'TIBL4': 648.0, 'TOBL3': 648.0, 'TOBL1': 1008.0, 'TOBL6': 888.0, 'TIBL1': 672.0, 'TIBL2': 864.0, 'TIBL3': 540.0, 'TEC': 6400.0, 'TOBL4': 720.0, 'TECD8': 624.0}

# A dictionary that connects the local subsystem layers to the global layers of the entire tracker.

subsyslayer = {"TIBL1" : "Layer 1","TIBL2" : "Layer 2","TIBL3" : "Layer 3","TIBL4" : "Layer 4","TOBL1" : "Layer 5","TOBL2" : "Layer 6","TOBL3" : "Layer 7","TOBL4" : "Layer 8","TOBL5" : "Layer 9","TOBL6" : "Layer 10","TIDD1" : "Layer 11","TIDD2" : "Layer 12","TIDD3" : "Layer 13","TECD1" : "Layer 14","TECD2" : "Layer 15","TECD3" : "Layer 16","TECD4" : "Layer 17","TECD5" : "Layer 18","TECD6" : "Layer 19","TECD7" : "Layer 20","TECD8" : "Layer 21","TECD9" : "Layer 22"}



def mkmoduledictlist( runlist ):

    "This function takes in a list of runs and produces a moduledictlist"

    moduledictlist=[]

    for run in runlist:
       
       filename = afsdir+'/run_'+run+'/standard/QualityLog/'+'EfficiencyResults_'+run+'.txt'

       if os.path.exists(filename):

           print "Processing Run Into ModuleDict: " + run
       
           file = open(filename, "r")

           filelines = file.readlines()

           if len(filelines) < 225:

               thresholddict={}
               
               for line in filelines:

                   moduledict = {}

                   tokens = line.split()
                   if len(tokens)>2 and tokens[2] == 'threshold':
                         if tokens[6][:1] == '<':
                             thresholddict.update({tokens[0]+tokens[1]:float(tokens[6].lstrip('<'))})
                         else:
                             thresholddict.update({tokens[0]+tokens[1]:float(tokens[6])})
                   if len(tokens)>6 and tokens[6]=='efficiency:':
                        moduledict.update({'Layer':tokens[0]+tokens[1],
                            'Subsystem':tokens[2].lstrip("(")+tokens[3].rstrip(")"),
                            'Module':int(tokens[5]), 'Efficiency':float(tokens[7]),
                            'SignaltoTotal':tokens[9], 'Run':int(run)})
                        if str(moduledict['Module']) in modulepowersupplydict.keys(): moduledict.update({'PowerSupply' : modulepowersupplydict[str(moduledict['Module'])] })
                        else: moduledict.update({'PowerSupply' : "N/A" })

                        if moduledict['Module'] in modulepowersupplyaliasdict.keys(): moduledict.update({'PowerSupplyAlias' : modulepowersupplyaliasdict[moduledict['Module']] })
                        else: moduledict.update({'PowerSupplyAlias' : "N/A" })

                   if len(tokens) > 13 and tokens[12]=='limit:':
                        moduledict.update({'EfficiencyUpperLimit':float(tokens[13])})


                   #Append moduledict with the threshold for that layer
                   for key, value in thresholddict.items():
                        if 'Layer' in moduledict.keys() and moduledict['Layer'] == key:
                            if value > 0: moduledict.update({'Threshold':value})
                            else: moduledict.update({'Threshold':'N/A'})

                   if 'Threshold' in moduledict.keys():
                       if moduledict['Threshold'] > moduledict['EfficiencyUpperLimit']: moduledict.update({'Inefficient':'Yes'})
                       else: moduledict.update({'Inefficient':'No'})

                   elif 'Module' in moduledict.keys(): moduledict.update({'Inefficient':'N/A'})

                   if moduledict != {} and 'Module' in moduledict.keys(): moduledictlist.append(moduledict)

                   #print moduledict

           else: 
               print filename + " has " + str(len(filelines))  + " lines of code (~145 is ideal).  This could indicate that there are insufficient statistics to conclusively determine inefficiency for more than 0.5% of  modules and so this run and its log will not be included in the analysis."

           file.close()

    return moduledictlist


def mkinefficientmodulelist( moduledictlist ):

    "This functions takes in a list of moduledict's and returns a list of unique detID's"

    inefficientmodulelist = []

    #for m, module in enumerate(moduledict['Module'] for moduledict in moduledictlist):
    #    
    #    inefficientmodulelist.append(module)
 
    for moduledict in moduledictlist:
        if moduledict['Inefficient'] == 'Yes':
            inefficientmodulelist.append(moduledict['Module'])

    inefficientmodulelist = sorted(list(set(inefficientmodulelist)))

    #print inefficientmodulelist
    return inefficientmodulelist


def mkdictrunlist( moduledictlist ):

    "This functions takes in a list of moduledict's and returns a list of unqiue run numbers"

    dictrunlist = []

    for r, run in enumerate(moduledict['Run'] for moduledict in moduledictlist):
        dictrunlist.append(run)
    
    dictrunlist = sorted(list(set(dictrunlist)))

    #print dictrunlist
    return dictrunlist


def mkmodulerunlist( moduledictlist, module ):

    "This functions takes in a list of moduledict's and a module ID and then returns a list of unqiue run numbers"
    
    modulerunlist = []
    
    for moduledict in moduledictlist:
        if module == moduledict['Module'] and moduledict['Inefficient'] == 'Yes':
            modulerunlist.append(moduledict['Run'])

    #print modulerunlist
    return modulerunlist


def analyzemoduledictlist ( moduledictlist ):
    "This function takes in a list of moduledict's and identifies for how many runs which modules were below threshold, which modules flip-flopped between good and bad and how many times, and the largest number of consecutive runs a module was found to be inefficient"
    
    numrunsflipfloppeddict = {}
    maxnumrunsconsecutivedict = {}
    numrunsinefficientdict = {}

    inefficientmodulelist = mkinefficientmodulelist(moduledictlist)
    dictrunlist = mkdictrunlist(moduledictlist)

    for m, module in enumerate(inefficientmodulelist):
        
        moduleconsecutive = 0
        moduleconsecutivemax = 0
        moduleflipflop = 0

        modulerunlist = mkmodulerunlist(moduledictlist,module)

        for n, run in enumerate(dictrunlist):
            if int(dictrunlist[n-1]) in modulerunlist:
                if int(dictrunlist[n]) in modulerunlist:
                    moduleconsecutive = moduleconsecutive + 1
                    if moduleconsecutive > moduleconsecutivemax: moduleconsecutivemax = moduleconsecutive
                else:
                    moduleflipflop = moduleflipflop + 1
                    moduleconsecutive = 0
            else:
                if int(dictrunlist[n]) in modulerunlist:
                    moduleflipflop = moduleflipflop + 1
                    moduleconsecutive = 1
                    if moduleconsecutive > moduleconsecutivemax: moduleconsecutivemax = moduleconsecutive
        numrunsflipfloppeddict.update({module : moduleflipflop})
        maxnumrunsconsecutivedict.update({module : moduleconsecutivemax})
        numrunsinefficientdict.update({module  : len(modulerunlist)})

    analysisresult = [numrunsinefficientdict, maxnumrunsconsecutivedict, numrunsflipfloppeddict]

    return analysisresult



def main():
    # Command Line Option Parser: 
    # Mode 1: $ python EfficiencyModules.py --allruns 
    # Mode 2: $ python EfficiencyModules.py <Current Run> <Reference Run> 

    parser = argparse.ArgumentParser(description='Either run in --allruns mode to make global dictionaries or with command line arguments for comparing a run against a reference, or for ')
    parser.add_argument('--allruns', action='store_true', default = False, help='Create a new dictionaries for all runs and dump as pickles.')
    parser.add_argument('currentrun', action='store', type=int, default = 0, nargs = '?', help='This is the run to be compared against the reference.')
    parser.add_argument('referencerun', action='store', type=int, default = 0, nargs = '?', help='This is the reference to compare against the current run.')
    args = parser.parse_args()


    # Mode 1: Across all runs for global behavior     $ python EfficiencyModules.py --allruns

    if args.allruns:

        # Here we make a moduledictlist, which is appended for each instance of module being below threshold with a dictionary that contains the run number, module ID, efficiency, upper limit on efficiency, and signal-to-noise ratio.

        moduledictlist = mkmoduledictlist(globalrunlist)

        sortedmoduledictlist=sorted(moduledictlist, key=lambda k: (k['Module'],k['Run']))

        #print sortedmoduledictlist

        analysisresults = analyzemoduledictlist(sortedmoduledictlist)
        numrunsinefficientdict = analysisresults[0]
        maxnumrunsconsecutivedict = analysisresults[1]
        numrunsflipfloppeddict = analysisresults[2]

        #print numrunsinefficientdict
        #print maxnumrunsconsecutivedict
        #print numrunsflipfloppeddict

        #sortednumrunsflipfloppeddict = sorted(numrunsflipfloppeddict.items(), key=lambda k: k[1], reverse = True)
        #sortedmaxnumrunsconsecutivedict = sorted(maxnumrunsconsecutivedict.items(), key=lambda k: k[1], reverse = True)
        sortednumrunsinefficientdict = sorted(numrunsinefficientdict.items(), key=lambda k: k[1], reverse = True)
        print sortednumrunsinefficientdict

        """
        # This block of code is for characterizing and partitioning the inefficient modules based on frequency of inefficiency

        IneffientModuleFrequency = TH1D('','IneffientModuleFrequency',25,0,100)
        for value in numrunsinefficientdict.values():
            IneffientModuleFrequency.Fill(value)
        IneffientModuleFrequencyCanvas = TCanvas('IneffientModuleFrequency', '', 600, 400)                                              
        IneffientModuleFrequencyCanvas.SetLogy()
        IneffientModuleFrequency.Draw()
        IneffientModuleFrequencyCanvas.SaveAs('IneffientModuleFrequency.pdf') 

        A =[]
        DifferenceA = TH1D('','DifferenceA from Threshold',44,-.1,1) 
        for key, value in numrunsinefficientdict.items():
            if value > 0 and value < 5 :
                for dict in sortedmoduledictlist:
                    if dict['Inefficient'] == 'Yes' and dict['Module'] == key:
                        DifferenceA.Fill(dict['Threshold'] - dict['EfficiencyUpperLimit'])
                A.append(key)
        DifferenceACanvas = TCanvas('DifferenceA', '', 600, 400)                      
        DifferenceACanvas.SetLogy()
        DifferenceA.Draw()                                                   
        DifferenceACanvas.SaveAs('DifferenceA.png')
        print(A)

        B = []
        DifferenceB = TH1D('','DifferenceB from Threshold',44,-.1,1) 
        for key, value in numrunsinefficientdict.items():
            if value > 55 and value < 65 :
                for dict in sortedmoduledictlist:
                    if dict['Inefficient'] == 'Yes' and dict['Module'] == key:
                        DifferenceB.Fill(dict['Threshold'] - dict['EfficiencyUpperLimit'])
                B.append(key)
        DifferenceBCanvas = TCanvas('DifferenceB', '', 600, 400)                      
        DifferenceBCanvas.SetLogy()
        DifferenceB.Draw()                                                            
        DifferenceBCanvas.SaveAs('DifferenceB.png')
        print(B)

        C = []
        DifferenceC = TH1D('','DifferenceC from Threshold',44,-.1,1) 
        for key, value in numrunsinefficientdict.items():
            if value > 71 and value < 81 :
                for dict in sortedmoduledictlist:
                    if dict['Inefficient'] == 'Yes' and dict['Module'] == key:
                        DifferenceC.Fill(dict['Threshold'] - dict['EfficiencyUpperLimit'])
                C.append(key)
        DifferenceCCanvas = TCanvas('DifferenceC', '', 600, 400)                      
        DifferenceCCanvas.SetLogy()
        DifferenceC.Draw()                                                            
        DifferenceCCanvas.SaveAs('DifferenceC.png')
        print(C)

        """

        # Dump pkl's

        pickle_moduledictlist = open("moduledictlist.pkl","w")
        pickle.dump(sortedmoduledictlist,pickle_moduledictlist)
        pickle_moduledictlist.close()

        pickle_numrunsinefficient = open("numrunsinefficient.pkl","w")
        pickle.dump(numrunsinefficientdict,pickle_numrunsinefficient)
        pickle_numrunsinefficient.close()

        pickle_numrunsflipflopped = open("numrunsflipflopped.pkl","w")
        pickle.dump(numrunsflipfloppeddict,pickle_numrunsflipflopped)
        pickle_numrunsflipflopped.close()

        pickle_maxnumrunsconsecutive = open("maxnumrunsconsecutive.pkl","w")
        pickle.dump(maxnumrunsconsecutivedict,pickle_maxnumrunsconsecutive)
        pickle_maxnumrunsconsecutive.close()


        # Make Tracker Maps

        numrunsinefficienttxt = open('TrkMapNumRunsInefficient.txt','w')    
        for key, value in numrunsinefficientdict.items():        
            numrunsinefficienttxt.writelines( str(key) + " " + str(value) + "\n" )
        numrunsinefficienttxt.close()
        os.system("print_TrackerMap TrkMapNumRunsInefficient.txt NumberRunsInefficient TrkMapNumRunsInefficient.png")

        numrunsflipfloppedtxt = open('TrkMapNumRunsFlipFlopped.txt','w')    
        for key, value in numrunsflipfloppeddict.items():        
            numrunsflipfloppedtxt.writelines( str(key) + " " + str(value) + "\n" )
        numrunsflipfloppedtxt.close()
        os.system("print_TrackerMap TrkMapNumRunsFlipFlopped.txt NumberRunsFlipFlopped TrkMapNumRunsFlipFlopped.png")

        maxnumrunsconsecutivetxt = open('TrkMapMaxNumRunsConsecutive.txt','w')    
        for key, value in maxnumrunsconsecutivedict.items():        
            maxnumrunsconsecutivetxt.writelines( str(key) + " " + str(value) + "\n" )
        maxnumrunsconsecutivetxt.close()
        os.system("print_TrackerMap TrkMapMaxNumRunsConsecutive.txt MaxNumberRunsConsecutive TrkMapMaxNumRunsConsecutive.png")



    # Mode 2: $ python EfficiencyModules.py <Current Run> <Reference Run>

    else:

        if args.currentrun == 0:
            print "No current run specified"

        if args.referencerun == 0:
            print "No reference run specified"

        if str(args.currentrun) not in globalrunlist: 
            print "No log file for current run"
        if str(args.referencerun) not in globalrunlist: 
            print "No log file for referencerun"

        comparisonrunlist = [str(args.currentrun),str(args.referencerun)]

        # Here we make a moduledictlist, which is appended for each instance of module being below threshold with a dictionary that contains the run number, module ID, efficiency, threshold, and signal-to-noise ratio.  From these, the difference from threshold, signal, and noise can also be extracted and used to update the dictionary.

        moduledictlist = mkmoduledictlist(comparisonrunlist)

        sortedmoduledictlist = sorted(moduledictlist, key=lambda k: (k['Subsystem'],k['PowerSupplyAlias'],k['PowerSupply'],k['Module'],k['Run']))
        #print sortedmoduledictlist


        #    Load in the global pickles that were already produced by running the code in Mode 1

        pickle_numrunsinefficient = open("numrunsinefficient.pkl","r")
        numrunsinefficientdict = pickle.load(pickle_numrunsinefficient)
        pickle_numrunsinefficient.close()

        pickle_numrunsflipflopped = open("numrunsflipflopped.pkl","r")
        numrunsflipfloppeddict = pickle.load(pickle_numrunsflipflopped)
        pickle_numrunsflipflopped.close()

        pickle_maxnumrunsconsecutive = open("maxnumrunsconsecutive.pkl","r")
        maxnumrunsconsecutivedict = pickle.load(pickle_maxnumrunsconsecutive)
        pickle_maxnumrunsconsecutive.close()

        pickle_globalmoduledictlist = open("moduledictlist.pkl","r")
        globalmoduledictlist = pickle.load(pickle_globalmoduledictlist)
        pickle_globalmoduledictlist.close()


        # Check if the current run and reference run are in the globalmoduledictlist and append them if not

        if str(args.currentrun) not in globalrunlist: 
            print "ModuleDict's for the current run are not in globalmoduledictlist; appending them now"
            for dict in sortedmoduledictlist:
                if dict['Run'] == args.currentrun: globalmoduledictlist.append(dict)

        if str(args.referencerun) not in globalrunlist: 
            print "ModuleDict's for the reference run are not in globalmoduledictlist; appending them now"
            for dict in sortedmoduledictlist:
                if dict['Run'] == args.referencerun: globalmoduledictlist.append(dict)


        # Let's make lists of the modules that were bad in both the current and reference runs, that flopped from good in the reference to bad in the current run, etc.

        moduleconsecutivelist = []
        modulefloppedbadlist = []
        modulefloppedgoodlist = []

        comparisondict = {}
        
        for m, module in enumerate(moduledict['Module'] for moduledict in sortedmoduledictlist):

            modulerunsbadlist = []

            for moduledict in sortedmoduledictlist:
                if moduledict['Module'] == module and moduledict['Run'] == args.currentrun and moduledict['Inefficient'] == 'Yes': modulerunsbadlist.append(args.currentrun)
                elif moduledict['Module'] == module and moduledict['Run'] == args.referencerun and moduledict['Inefficient'] == 'Yes': modulerunsbadlist.append(args.referencerun)

            if args.currentrun in modulerunsbadlist:            
                if args.referencerun in modulerunsbadlist:
                    moduleconsecutivelist.append(module)
                else:
                    modulefloppedbadlist.append(module)

            else:
                if args.referencerun in modulerunsbadlist:
                    modulefloppedgoodlist.append(module)

        # Now create the log file comparing the inefficient modules of the current run to the reference run

        logfile = open('Comparing'+str(args.referencerun)+'to'+str(args.currentrun)+'.log','w')

        logfile.write("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ \n")
        logfile.write("---------------------------------------------------------------------Inefficient Modules-------------------------------------------------------------------------------------- \n")
        logfile.write("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ \n")
        logfile.write("Subsystem \t Power Supply \t \t DetID \t \t Efficiency \t Signal/Total \t Threshold \t Upper Limit \t Consecutive \t MaxConsecutive\t Flip-Flopped \t Total \n")
        logfile.write("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ \n")


        for moduledict in sortedmoduledictlist:

            # Need to be careful here and initialize everything as 'N/A' or 'None', in case, i.e., the module never crossed the inefficiency threshold (empty global information) but came close

            modulethreshold = 'N/A'
            if 'Threshold' in moduledict.keys(): modulethreshold = str(moduledict['Threshold'])

            moduleupperlimit = 'N/A'
            if 'EfficiencyUpperLimit' in moduledict.keys(): moduleupperlimit = str(moduledict['EfficiencyUpperLimit'])

            moduleefficiency = "N/A"
            if 'Efficiency' in moduledict.keys(): moduleefficiency = str(moduledict['Efficiency'])
            if len(moduleefficiency) < 7: 
                for i in range(0,8 - len(moduleefficiency)): 
                    moduleefficiency = moduleefficiency + "0"
            modulesignaltototal = "N/A"
            if 'SignaltoTotal' in moduledict.keys(): modulesignaltototal = str(moduledict['SignaltoTotal'])
            if len(modulesignaltototal) < 4: modulesignaltototal = " " + modulesignaltototal + " "
            if len(modulesignaltototal) < 6: modulesignaltototal = " " + modulesignaltototal + " "

            # moduleconsecutivereference key: 1: inefficient in both current and reference runs, 0: inefficient in current run, but not in reference run, -1: inefficient in reference run, but not in current run

            moduleconsecutivereference = "0"
            if moduledict['Module'] in moduleconsecutivelist: moduleconsecutivereference = "1"
            if moduledict['Module'] in modulefloppedbadlist: moduleconsecutivereference = "0"
            if moduledict['Module'] in modulefloppedgoodlist: moduleconsecutivereference = "-1"

            if moduledict['Module'] in maxnumrunsconsecutivedict.keys(): 
                modulemaxnumrunsconsecutive = str(maxnumrunsconsecutivedict[moduledict['Module']])
            else:
                modulemaxnumrunsconsecutive = "None"

            if moduledict['Module'] in numrunsflipfloppeddict.keys(): 
                modulenumrunsflipflopped = str(numrunsflipfloppeddict[moduledict['Module']])
            else:
                modulenumrunsflipflopped = "None"

            if moduledict['Module'] in numrunsinefficientdict.keys(): 
                modulenumrunsinefficient = str(numrunsinefficientdict[moduledict['Module']])
            else:
                modulenumrunsinefficient = "None"

            if moduledict['Inefficient'] == 'Yes':

                comparisondict.update({moduledict['Module']:moduleconsecutivereference})


            if moduledict['Run'] == args.currentrun and moduledict['Inefficient'] == 'Yes':

                logfile.write( moduledict['Subsystem'] + " \t \t " + 
                               moduledict['PowerSupplyAlias'] + " \t " +  
                               str(moduledict['Module']) + " \t " + 
                               moduleefficiency + " \t " + 
                               modulesignaltototal + " \t "  + 
                               modulethreshold + " \t " + 
                               moduleupperlimit + " \t " + 
                               moduleconsecutivereference + " \t \t " + 
                               modulemaxnumrunsconsecutive + " \t \t " +
                               modulenumrunsflipflopped + " \t \t " + 
                               modulenumrunsinefficient + 
                               "\n")

            elif moduledict['Run'] == args.referencerun and moduleconsecutivereference == "-1" and moduledict['Inefficient'] == 'Yes':

                # Since these modules were inefficient in the reference run, but not in the current run, the log gets filled with some columns empty

                logfile.write( moduledict['Subsystem'] + " \t \t " + 
                               moduledict['PowerSupplyAlias'] + " \t " +  
                               str(moduledict['Module']) + " \t " + 
                               "--------" + " \t " + 
                               "--------" + " \t " + 
                               "--------" + " \t " + 
                               "--------" + " \t " + 
                               moduleconsecutivereference + " \t \t " + 
                               modulemaxnumrunsconsecutive + " \t \t " +
                               modulenumrunsflipflopped + " \t \t " + 
                               modulenumrunsinefficient + 
                               "\n")

        # This second part of the log file contains information about efficient modules that were close to the inefficiency threshold

        logfile.write("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ \n")
        logfile.write("---------------------------------------------------------------------Efficient Modules---------------------------------------------------------------------------------------- \n")
        logfile.write("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ \n")
        logfile.write("Subsystem \t Power Supply \t \t DetID \t \t Efficiency \t Signal/Total \t Threshold \t Upper Limit \t Consecutive \t MaxConsecutive\t Flip-Flopped \t Total \n")
        logfile.write("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ \n")


        for moduledict in sortedmoduledictlist:

            modulethreshold = 'N/A'
            if 'Threshold' in moduledict.keys(): modulethreshold = str(moduledict['Threshold'])

            moduleupperlimit = 'N/A'
            if 'EfficiencyUpperLimit' in moduledict.keys(): moduleupperlimit = str(moduledict['EfficiencyUpperLimit'])

            moduleefficiency = "N/A"
            if 'Efficiency' in moduledict.keys(): moduleefficiency = str(moduledict['Efficiency'])
            if len(moduleefficiency) < 7: 
                for i in range(0,8 - len(moduleefficiency)): 
                    moduleefficiency = moduleefficiency + "0"
            modulesignaltototal = "N/A"
            if 'SignaltoTotal' in moduledict.keys(): modulesignaltototal = str(moduledict['SignaltoTotal'])
            if len(modulesignaltototal) < 4: modulesignaltototal = " " + modulesignaltototal + " "
            if len(modulesignaltototal) < 6: modulesignaltototal = " " + modulesignaltototal + " "

            moduleconsecutivereference = "0"
            if moduledict['Module'] in moduleconsecutivelist and moduledict['Inefficient'] == 'Yes': moduleconsecutivereference = "1"
            if moduledict['Module'] in modulefloppedbadlist: moduleconsecutivereference = "0"
            if moduledict['Module'] in modulefloppedgoodlist: moduleconsecutivereference = "-1"

            if moduledict['Module'] in maxnumrunsconsecutivedict.keys(): 
                modulemaxnumrunsconsecutive = str(maxnumrunsconsecutivedict[moduledict['Module']])
            else:
                modulemaxnumrunsconsecutive = "None"

            if moduledict['Module'] in numrunsflipfloppeddict.keys(): 
                modulenumrunsflipflopped = str(numrunsflipfloppeddict[moduledict['Module']])
            else:
                modulenumrunsflipflopped = "None"

            if moduledict['Module'] in numrunsinefficientdict.keys(): 
                modulenumrunsinefficient = str(numrunsinefficientdict[moduledict['Module']])
            else:
                modulenumrunsinefficient = "None"

            if moduledict['Run'] == args.currentrun and moduledict['Inefficient'] == 'No':
                logfile.write( moduledict['Subsystem'] + " \t \t " + 
                               moduledict['PowerSupplyAlias'] + " \t " +  
                               str(moduledict['Module']) + " \t " + 
                               moduleefficiency + " \t " + 
                               modulesignaltototal + " \t " + 
                               modulethreshold + " \t " + 
                               moduleupperlimit + " \t " + 
                               moduleconsecutivereference + " \t \t " + 
                               modulemaxnumrunsconsecutive + " \t \t " +
                               modulenumrunsflipflopped + " \t \t " + 
                               modulenumrunsinefficient + 
                               "\n")

        logfile.write("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ \n")

        logfile.close()

        # Make Tracker Maps

        comparisontxt = open('TrkMapComparing'+str(args.currentrun)+'to'+str(args.referencerun)+'.txt','w')    

        for key, value in comparisondict.items():        
            comparisontxt.writelines( str(key) + " " + str(value) + "\n" )
        comparisontxt.close()
        os.system('print_TrackerMap '+'TrkMapComparing'+str(args.currentrun)+'to'+str(args.referencerun)+'.txt'+' Comparing'+str(args.currentrun)+'to'+str(args.referencerun)+' TrkMapComparing'+str(args.currentrun)+'to'+str(args.referencerun)+'.png 4500 False False -1 1')


##############################

if __name__ == "__main__":

    main()

##############################  
