# SiStripHitEffAnalysis
DQM Tools to analyze SiStrip hit efficiencies 

cmsenv at /afs/cern.ch/work/j/jthieman/public/CMSSW_10_1_0/src/

Command Line Option Parser:

Mode 1: $ python EfficiencyModules.py --allruns    

Analyzes the runs for with SiStrip Efficiency Results have been produced.  Creates a list of dictionaries associated with each instance a module is inefficient/below threshold.  Analyzes the list and identifies for how many runs which modules were below threshold, which modules flip-flopped between good and bad and how many times, and the largest number of consecutive runs a module was found to be inefficient.  The results are dumped in .pkl format and are used to produce tracker maps.  In order for the tracker maps functionality to work, you must cmsenv in a CMSSW environment with this functionality.  It is recommended to login to cctrack and cmsenv in the same CMSSW that is used to make the tracker maps. https://twiki.cern.ch/twiki/bin/viewauth/CMS/TrackerOfflineShiftInstructions#

Mode 2: $ python EfficiencyModules.py Current Run Reference Run

Analyzes the current run with respect to the reference run as long SiStrip Efficiency Results have been produced.  Reads in the .pkl's produced from running the code Mode 1 so that the a log file comparing/contrasting the current run and reference run can be appended with the global behavior of modules across all runs for which SiStrip Efficiency Results have been produced.  Creates a comparingruns.log files that includes all the modules that were inefficient in the current run, sorted by sublayer, power supply alias, and then module number.  If a module was inefficient in both the reference run and the current run, consecutive == 1; if a module was inefficient in the current run and not the reference run, consecutive == 0; if a module was inefficient in the reference run but not the current run, consecutive == -1.


(Hard-coded in EfficiencyModules.py) Location of my SiStrip Hit Efficiency Measurement Results:
afsdir='/afs/cern.ch/work/j/jthieman/public/HitEfficiency/GR18'

Useful command (from cctrack) to quickly delete any SiStrip Hit Efficiency Measurement Results logs that were > 20 KB in size:
find run*/standard/Q*/. -size +20k -delete

These results were produced using a slightly modified version of the SiStrip Hit Efficiency Measurement code:
/afs/cern.ch/work/j/jthieman/public/CMSSW_10_1_0/src/StripHitEfficiency/ShifterTools/HitEffDriver.sh, instructions: https://twiki.cern.ch/twiki/bin/view/CMS/TrackerOfflineShiftLeaderInstructions
The changes I made to add printout for efficient modules within .08 above inefficiency threshold in this file:
/afs/cern.ch/work/j/jthieman/public/CMSSW_10_1_0/src/CalibTracker/SiStripHitEfficiency/plugins/SiStripHitEffFromCalibTree.cc
        if(myeff_up < layer_min_eff)
          cout << "Layer " << i <<" ("<< GetLayerName(i) << ")  module " << (*ih).first << " efficiency: " << myeff << " , " << mynum << "/" << myden <<" , upper limit: " << myeff_up << endl;
        else if(myeff_up < layer_min_eff+0.08) // printing message also for modules slighly above (8%) the limit
          cout << "Layer " << i <<" ("<< GetLayerName(i) << ")  module " << (*ih).first << " efficiency: " << myeff << " , " << mynum << "/" << myden <<" , upper limit: " << myeff_up <<" ### This module was not inefficient ### " << endl;
    	    if(myden < nModsMin )
          cout << "Layer " << i <<" ("<< GetLayerName(i) << ")  module " << (*ih).first << " layer " << i << " is under occupancy at " << myden << endl;

Locations of older results that do not print out the efficient modules within .08 above inefficiency threshold:
      Original 2018 Results: /afs/cern.ch/cms/tracker/sistrvalidation/WWW/CalibrationValidation/HitEfficiency
      Archived 2017 and Earlier Results: /eos/cms/store/group/dpg_tracker_strip/comm_tracker/archival/