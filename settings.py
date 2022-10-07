#!/usr/bin/env python3

import os

README = True


#change this to True if you want to enable all logging output
verbose = False

#disables logging; may provide boost in performance
#only use if you are sure everything works fine on your system first
logging = True

#change this to False if you want to disable log overwrite
#(useful for tracking changes or troubleshooting load order overwrites)
logfile_overwrite = True

#change this if you want to log processing events to a different file (used for ./onLoad.py)
logfile_main = './vfs_main.log'

#change this if you want to log intake events to a different file (used for ./onLoad.py)
logfile_in = './vfs_in.log'

#change this if you want to log outtake events to a different file (used for ./onUnload.py)
logfile_out = './vfs_out.log'


#`./onLoad.py` is used to load the virtual file system either for the first time
#   or after load order changes
#
#`./onUnload.py` is used to save changes to the virtual file system to a seperate
#   directory that overwrites all other data on load
#
#`./rename.py` takes a directory path as an argument and is used to forcefully rename
#   all files and folders in that path to their lowercase variant, (recursive)
#
#
#
#   please note that this script will refuse to work if there are overlapping files
#
#   for instance, the following will fail:
#   $ ls mods/
#   fileA   filea   Filea
#   $ ./rename.py mods/

#change this if you want the game to always run from a specific directory once the vfs is loaded
workDir = os.getcwd()

#change this to your base game backup directory
#IMPORTANT: DO NOT USE YOUR STEAM FOLDER, BACK IT UP TO A SEPERATE LOCATION AND POINT THIS SCRIPT AT THE BACKUP
baseGameDir = #'./SSE.backup/'

#change this to your mods directory
#currently supported convention is to unpack each mod seperately into it's own directory, with the file structure mirroring the contents of the root game directory 1:1
#   content examples `./SSE.mods/00-skse/skse64_loader.exe`,
#                    `./SSE.mods/01-ussep/data/ussep.esp`
#     point to where `^-this-is-^` specifically, fully inclusive, on your system
#                                             -p.s. (the trailing slash matters)
modsDir = #'./SSE.mods/'

#change this if you want to save the virtual file system to a different folder
#this is the folder that the game should be run from
#relative uplinks are buggy (i.e. do not use `./../TESV`, './TESV' should work fine as long as you load from the same place every time)
vfsDir = './vfs'#'/home/john/Games/TESV'

#change these you want the game to save manifest data to a different directory
#-p.s. (the lack of trailing slash matters)
manifestPath = './mfs'
manifestPathPrior = f"{manifestPath}/prior"
manifestPathPost = f"{manifestPath}/post"
manifestPathJson = './manifest.json'

#change this to your overwrite directory in your mods directory
#for instance, if you are numbering your mod directories for load order purposes from 0-99, a value of "./<mods directory>/99-overwrite" will load last;
#a seperate folder such as "./<mods directory>/98-cold_overwrite" is recommended for .ini and other files you want to load last but never accidentally replace
#currently supported convention is to unpack each mod seperately into it's own directory, with the file structure mirroring the contents of the root game directory 1:1;
#as an example for skyrim:
#```
#   $ ls ./SSE.mods/
#   00-executable_patch/
#   01-skse/
#   02-ussep/
#   03-skyui/
#   ...
#
#   $ ls ./SSE.mods/01-skse/
#   data/
#   src/
#   skse64_x_x_xxx.dll
#   skse64_loader.exe
#   ...
#```
overwriteDir = #f"{modsDir}99-overwrite"


#disable this if you don't care about the vfs already existing on disk when loading
#(this option may have strange and unintended consequences, such as rogue files in the overwrite)
timidCopy = False

#enable this if you want to automatically delete the vfs and manifest after the unload script completes
#note that the load script will fail if an existing vfs dir exists, to prevent data loss
#enabling this flag should not lose files, as changes are written to the overwrite_directory
removeDuringUnload = False

#add entries to prevent certain files from being loaded
blacklist = {}


#add entries to prevent certain characters from being loaded
#use if you run into file not found errors on manifest dump
troubleChars = {' ','&',"'",'"','$','(',')','`'}

#change to increase/decrease threadcount during manifest dump
#safe value is your cpu core count ("nicest" performance)
#'overclock' value is 3x your cpu core count ("fastest" performance; will grind ur cpu)
# (recommended values between 1-256 depending on system.
# set it to your core count if you do not know what to set it to
#
#  values higher than 8 are not recommended unless you
#  are certain the load your processer can handle is not
#  exceeded.
#
#  ctds, bsods, and segfaults lurk- beware.)
threadcount=8

#sets amount of retries on hashing before doubling the timeout period below
maxHashFails = 1

#sets timeout period between hashing failures
hashFailsTimeout = 1


#enabling this sets the file hashing to only compare file meta data rather than bitwise content
#current implementation seems borked when removeDuringUnload and/or timidCopy are False
# use at own risk, always check 99-overwrite after unloading if you want to be safe
fastHashing = True
