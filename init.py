#!/usr/bin/env python3


import os
import shutil
import sys
import json
import glob
import pathlib
import hashlib
import urllib
import subprocess
import time

from datetime import datetime as datetime

from settings import *



def log(msg, logfile=logfile_main, v=verbose):
    if logging:
        msg = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} :\t{msg}\n"
        if v:
            print(msg , end='')
        with open(logfile, 'a') as lf:
            lf.write(msg)


def md5hash(fPath):
    log(f"hashing '{fPath}'")
    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

    md5 = hashlib.md5()

    with open(fPath, 'rb') as fObj:
        while True:
            data = fObj.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)

        fHash = md5.hexdigest()

    log(f"finished hashing '{fPath}'")
    return fHash


def batchProcess(jobs=dict(), threadcount=threadcount):
    '''
    multithreader for processing hashes faster

    jobs, DICT: takes a file path list as input:
        (full paths highly recommended,
         relative paths must all start from the same root)
        { INT: job_id_A: STR: 'command to run',
          INT: job_id_B: STR: 'command to run',
          ...,
          INT: job_id_N: STR: 'command to run'
          }

    threadcount, INT:   takes a thread count integer as input:
        (recommended values between 1-256 depending on system.

         values higher than 8 are not recommended unless you
         are certain the load your processer can handle is not
         exceeded.

         ctds, bsods, and segfaults lurk- beware.)

    '''
    jobLength = len(jobs)
    tc = jobLength if threadcount == 0 else threadcount
    def processer(jobs=jobs,tc=tc):
        for J in range(0, jobLength, tc):
            batch = []
            batchRange = jobLength - 1 if jobLength < J + tc else J + tc - 1

            #print(f"{J/jobLength}%",end='')
            log(f"running batch {J} -> {batchRange} / {jobLength}")
            for jobIdx in range(J, batchRange+1):
                # if jobIdx % int( jobLength / 1000 ) == 0:
                #     print('.',end='')
                log(f"spawning sub {jobIdx} to exec `{jobs[jobIdx]}`")
                shell = True if type(jobs[jobIdx]) == str else False
                p = subprocess.Popen(jobs[jobIdx],
                                    shell=shell,
                                    stdout=subprocess.PIPE)
                batch.append(p)
            runningBatchCount = len(batch)
            while len(batch) > 0:
                toRemove = []
                for p in batch:
                    if p.poll() is not None:
                        toRemove.append(p)
                for p in toRemove:
                    batch.remove(p)
            log(f"finished batch {J} -> {batchRange}")



    log(f"job length: {jobLength}")
    log(f"batch processing in {tc} threads/batch:")
    # if verbose:
    #     log(f"```\n{jobs}\n```")

    processer()
    time.sleep(1)

    logMsg = f"finished processing all {jobLength+ 1} jobs"
    #print(logMsg)
    log(logMsg)



def dumpJson(fPath, dump):
    log(f"dumping into '{fPath}'")
    with open(fPath, "w") as manifestFile:
        json.dump(dump, manifestFile)
    log(f"finished dumping into '{fPath}'")
    return 0

def loadJson(fPath):
    log(f"loading '{fPath}'")
    with open(fPath, "r") as manifestFile:
        output = json.load(manifestFile)
    log(f"finished loading '{fPath}'")
    return output


def readFileBytes(fPath):
    log(f"reading bytes directly from '{fPath}'")
    with open(fPath, "rb") as fObj:
        f = fObj.read()
    log(f"finished reading bytes directly from '{fPath}'")
    return f

def writeFileBytes(fPath, data):
    log(f"writing bytes directly to '{fPath}'")
    try:
        with open(fPath, "wb") as fObj:
            fObj.write(data)
        log(f"finished writing bytes directly to '{fPath}'")
        return 0
    except Exception as e:
        log(f"failed writing bytes directly to '{fPath}'")
        return f"{e}"


def copyTreeSkeleton(srcPath, dstPath):
    log(f"copying directory skeleton from '{srcPath}' to '{dstPath}'")
    def keep_only_dirs(path, files):
        to_ignore = [
            fname for fname in files
            if not os.path.isdir(os.path.join(path, fname))
            ]
        return to_ignore

    # This works for python3 (<3.8), BUT the target directory MUST not exist
    shutil.copytree(srcPath, dstPath, ignore=keep_only_dirs, dirs_exist_ok=True)
    log(f"finished copying directory skeleton from '{srcPath}' to '{dstPath}'")


def copyFile(srcPath, dstPath):
    log(f"copying file from '{srcPath}' to '{dstPath}'")
    try:
        shutil.copyfile(srcPath, dstPath)

        log(f"finished copying file from '{srcPath}' to '{dstPath}'")
        return 0
    except Exception as e:
        log(f"failed copying file from '{srcPath}' to '{dstPath}'")
        return f"{e}"

def writeChanges(fileSrc=vfsDir):
    log(f"checking for changes to {fileSrc} post game; PLEASE DO NOT TERMINATE PREEMPTIVELY AS VALUABLE DATA CAN BE LOST")
    fileDest = '/'.join([ p for p in fileSrc.split('/') ][2:])
    dirDest = '/'.join([ p for p in fileDest.split('/') ][:-1])
    fileDest = f"{overwriteDir}/{fileDest}"
    dirDest = f"{overwriteDir}/{dirDest}"
    log(f"\tcopying from {fileSrc} to {fileDest}")
    result = copyFile(fileSrc,fileDest)
    if result == 0:
        log('\tsuccessfully copied')
    else:
        log(f"\t{result}")
        result = writeFileBytes(fileDest,readFileBytes(fileSrc))
        if result == 0:
            log('\tsuccessfully copied via direct write')
        else:
            log(f"\t{result}")
            log(f"\tdirectory to be made:\t{dirDest}")
            #os.mkdir(dirDest)
            pathlib.Path(dirDest).mkdir(parents=True, exist_ok=True)

            result = writeFileBytes(fileDest,readFileBytes(fileSrc))
            if result == 0:
                log('\tsuccessfully copied via direct write')
            else:
                log('\tfailed to copy; proceeding without')
    log(f"finished checking for changes to {fileSrc} post game;")



if logfile_overwrite:
    writeFileBytes(logfile_main,b'')
