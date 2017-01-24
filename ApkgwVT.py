# -*- coding: utf-8 -*-
"""
Created on Sat Dec 31 19:34:03 2016

@author: jeremy.long - a total Novice
"""


#import relevant modules

import webbrowser
import calendar
from datetime import datetime
from datetime import date
import os
import subprocess
import shutil
import time

#Variables for including User directory in path variables, etc/
homedir = os.environ['HOME']
homeDesktop = os.path.join(os.environ['HOME'], "Desktop")
arecipes = "Egnyte/Shared/Tech Services/Software/Autopkg-cache/"
recipe_run_list = "Egnyte/Shared/Tech Services/Software/Autopkg-cache/recipe-run-list.txt"
autopkgrecipes = os.path.join(os.environ['HOME'], arecipes)
apkgrunlistPath = os.path.join(homedir, recipe_run_list)
arepos = "Egnyte/Shared/Tech Services/Software/AutoPkg/RecipeRepos/"
autopkgrepos = os.path.join(os.environ['HOME'], arepos)


#Variable to turn subdirectories into indexed list items
subdirs = os.listdir(autopkgrecipes)
RepoSubdirs = os.listdir(autopkgrepos)

#Additional variables - an empty list for recently modified dirs, and a list for files to be ignored in iterations
UpdatedDirs = []
IgnoreThese = [".DS_Store",os.path.join(autopkgrecipes, ".DS_Store"),os.path.join(autopkgrecipes, "autopkg_results.plist"),apkgrunlistPath]


#time stamp variables - float value for current time, and float value for an hour ago,
#Today's date as a float, and Today's date in ISO format
Now = time.time()
HourAgo = time.time() - 60*60    
Today = date.today()
TodayISO = date.isoformat(Today)

#Additional Folder path variables - Desktop folder name for collecting updated Pkgs
TodayFolder = str(TodayISO) + "-AutoPkg-Pkgs"
TodayFolderPath = os.path.join(homeDesktop, TodayFolder)


#Function to return git repo URL from local directory path
def GitRepo(FolderName):
    '''Function takes in the name of the given repo directoy, 
       splits the name on the "." into a list, and reassembles as the actual repo URL'''
    URLElements = FolderName.split(".")
    NEWURL = "https://" + URLElements[1] + "." + URLElements[0] + "/" + URLElements[2] + "/" + URLElements[3] + ".git"
    print("Checking for updates at " + NEWURL + "...")    
    return NEWURL

#Function to find updated Pkg file
def FindPkg(ThisFolder):
    '''Takes in the currently iterated folder and identifies the pkg file, 
       then evaluates all existing pkgs, if more than 1 exist, and returns the newest'''
    global autopkgrecipes            
    PkgList = []    
    NewFile = ''    
    TempFolder = os.path.join(autopkgrecipes, ThisFolder)
    FileList = os.listdir(TempFolder)    
    
    for file in FileList:        
        if file.endswith(".pkg"):
            PkgList.append(file)
            
    for x in PkgList:
        Now = time.time()
        filepath = os.path.join(TempFolder, x)
        Ctime = os.path.getctime(filepath)
        Age = Now - Ctime
        Newest = calendar.timegm(time.gmtime())
        if Age < Newest:
            Newest = os.path.getctime(filepath)
            NewFile = x
    
    print("The newest file is:  " + NewFile + "\n\n")            
    return NewFile

#Function to copy updated pkg to directory on desktop
def MovePkg(NewPkg, CurrentDir, DesktopFolder):
    '''Creates directory on ~/Desktop named after today's date, 
        and takes the recently updated pkg file and copies it to this directory'''    
    Source = os.path.join(autopkgrecipes, CurrentDir, NewPkg)    
    Destination = os.path.join(DesktopFolder, NewPkg)    
    shutil.copy2(Source, Destination)
    
########################
#Program Run Processes
########################

#subprocess to run repo updates on all locally existing repos
#print("\n\nUpdating locally available Autopkg Repositories first, this may take some time.  Please stand by...\n")
#

for x in RepoSubdirs:
    if x not in IgnoreThese:
        subprocess.check_output(["autopkg", "repo-update", GitRepo(x)])
        time.sleep(5)


print("Autopkg Repos are Up to Date!\n")


#Run Autopkg with appropriate args for skipping code validation and VirusTotal Analyze

print("\n\nRunning Autopkg Recipes now, this may take some time.  Please stand by...\n")
subprocess.run(["autopkg", "run", "-v", "--post", "io.github.hjuutilainen.VirusTotalAnalyzer/VirusTotalAnalyzer", "-l", str(apkgrunlistPath)], stdout=subprocess.PIPE)
print("Autopkg run complete!  VirusTotal Summary links have been sent to your browser.\n\n")


#Iterate over subdirectories in recipes folders, pulling out directories
#with modified time within last 60 minutes, add to 'UpdatedDirs' List, and copy pkg to Desktop    

print("\nPreparing a desktop folder for the new packages...\n\n")
os.mkdir(TodayFolderPath)

for x in subdirs:
    FullPathX = os.path.join(autopkgrecipes, x)
    lastmod = os.path.getmtime(FullPathX)    
    if FullPathX not in IgnoreThese:  
        if lastmod > HourAgo:
            print(str(x) + " had an updated pkg, ready for flight!")
            print("Copying the updated Pkg to your desktop...")
            MovePkg(FindPkg(FullPathX), FullPathX, TodayFolderPath)
            UpdatedDirs.append(FullPathX)


#Launch JSS browser session - directed to packages upload page 

print("\nTaking you to the JSS to upload packages at your leisure!\n")
webbrowser.open('https://casper.warbyparker.com:8443/packages.html', new=2)

#close open files and print Completion notice
        
