#!/usr/bin/env python3



from init import *


if README:
    if input('''
    #THIS SCRIPT IS WRITTEN FOR LINUX
    #NO SUPPORT IS OFFERED TO WINDOWS/MAC
    #IF USING THESE SYSTEMS, RUN SCRIPT AT YOUR OWN DISCRETION
    #UNINTENDED CONSEQUENCES MAY OCCUR

    set README to False in settings.py to disable this prompt;
    any input will continue the program >:\t''') != '':
        pass
    else:
        log('cowardly refusing to proceed, consider using gnu/linux',logfile=logfile_out,v=verbose)
        exit()


#MAIN ENTRY POINT


if logfile_overwrite:
    writeFileBytes(logfile_in,b'')

if fastHashing:
    manifestPathPrior = manifestPath
    manifestPathPost = manifestPath


logMsg = 'loading virtual file system'
print(logMsg)
log(logMsg,logfile=logfile_in,v=verbose)

if timidCopy:
    try:
        os.mkdir(vfsDir)
    except Exception as e:
        print("please open and read `settings.py`")
        print("this file is used to set settings and contains useful information")
        print("\nhappy modding!")
        logMsg = f"could not create vfs directory, see error message for further details\n```\n{e}\n```"
        print(logMsg)
        log(logMsg,logfile=logfile_in,v=verbose)
        exit()

    try:
        os.mkdir(manifestPath)
    except Exception as e:
        print("please open and read `startHere.py`")
        print("this file is used to set settings and contains useful information")
        print("\nhappy modding!")
        logMsg = f"could not create vfs directory, see error message for further details\n{e}"
        print(logMsg)
        log(logMsg,logfile=logfile_in,v=verbose)
        exit()


vfsManifest = dict()

modsToWrite = []

command = 'echo "{" > '
command += manifestPathJson
batchProcess({0:command})
jobs = dict()


log(f"adding base game to bottom of load order",logfile=logfile_in,v=verbose)

logMsg = f"files copying backwards for efficiency; no files will be overwritten during copying"
print(logMsg)
log(logMsg,logfile=logfile_in,v=verbose)

modsToWrite.append(baseGameDir)

#checks mods folder for data to load
log(f"reading modded game date",logfile=logfile_in,v=verbose)
for d in os.listdir(modsDir):

    modsToWrite.append(d)

unorderedMods = '\n\t'.join([f for f in modsToWrite])
log(f"unordered mods to load:\n\t{unorderedMods}\n",logfile=logfile_in,v=verbose)
log(f"found {len(modsToWrite) +1 } mods to write",logfile=logfile_in,v=verbose)

log(f"reading load order",logfile=logfile_in,v=verbose)
modsToWrite.sort()

loadOrder = '\n\t'.join([mod for mod in modsToWrite])
log(f"sorted order:\n\t{loadOrder}\n",logfile=logfile_in,v=verbose)


# ignorefiles = set()
# def _ignorefiles(path, names):
#     for f in names:
#         wildCardPath = f"*/{'/'.join([ p for p in path.split('/')][3:])}/{f}"
#         #fullPath = f"{path}/{f}"
#         #print(f"ignoring \'{fullPath}\" and \'{wildCardPath}\'")
#         ignorefiles.add(wildCardPath)
#         #ignorefiles.add(fullPath)
#     return [f for f in ignorefiles]
#

#walk backwards through mods and only write first seen unique file path (noninclusive of mod dir)
for mIdx in range(len(modsToWrite)-1,-1,-1):
    m = modsToWrite[mIdx]
    if mIdx != 0:
        src = f"{modsDir}{m}"
    else:
        src = m
    #
    # for p in glob.glob(vfsDir, recursive=True):
    #     path = f"{src}{p.split(vfsDir)[1]}"
    #     if not os.path.isdir(path):
    #         ignorefiles.add(f"{src}/{path}")
    #         ignorefiles.add(f"{baseGameDir}/{path}")

    logMsg= f"queueing copy of '{src}'s tree to virtual file system"

    if verbose:
            print(logMsg)
    log(logMsg,logfile=logfile_in,v=verbose)
    copyTreeSkeleton(srcPath=src, dstPath=vfsDir)

    logMsg= f"queueing copy of '{src}'s tree to {manifestPathPrior}"
    if verbose:
            print(logMsg)
    log(logMsg,logfile=logfile_in,v=verbose)
    copyTreeSkeleton(srcPath=src, dstPath=f"{manifestPathPrior}/")

    logMsg= f"queueing copy of '{src}'s tree to {manifestPathPost}"
    if verbose:
            print(logMsg)
    log(logMsg,logfile=logfile_in,v=verbose)
    copyTreeSkeleton(srcPath=src, dstPath=f"{manifestPathPost}/")

    for fPath in  glob.glob(f"{src}/**", recursive=True):
        skip = False

        if mIdx != 0:
            splitIdx = 3
        else:
            splitIdx = 2
        mPath = f"{manifestPathPrior}/{'/'.join(fPath.split('/')[splitIdx:])}"
        mPathRoot = '/'.join([ _ for _ in mPath.split('/')][:-1])
        vfsPath = f"{vfsDir}/{'/'.join(fPath.split('/')[splitIdx:])}"


        if os.path.isdir(fPath):
            skip = True
        else:
            for b in blacklist:
                if fPath[:len(b)] == b:
                    skip = True

        if not skip:
            fPath_json = fPath
            mPath_json = mPath
            vfsPath_json = vfsPath
            for tc in troubleChars:
                fPath = fPath.replace(tc,'\\'+tc)
                mPath = mPath.replace(tc,'\\'+tc)
                mPathRoot = mPathRoot.replace(tc,'\\'+tc)
                vfsPath = vfsPath.replace(tc,'\\'+tc)
                if tc not in  (' ','&',"'"):
                    fPath_json = fPath_json.replace(tc,'\\'+tc)
                    mPath_json = mPath_json.replace(tc,'\\'+tc)
                    vfsPath_json = vfsPath_json.replace(tc,'\\'+tc)
            if mPath_json not in vfsManifest:
                logMsg = f"copying:\t{mPath} -> {fPath}"
                if verbose:
                    log(f"creating job to\n\t* touch {mPath},\n\t* hash {fPath} into it,\n\t* copy it to {vfsPath}",logfile=logfile_in,v=verbose)

                mEntry = f"\t\\\"$(cat {mPath})\\\": \\\"{fPath_json}\\\","

                cmdLogging = f"echo \"{logMsg}\" >> {logfile_main}"
                                
                cmdCopying = f"cp {fPath} {vfsPath}"
                
                if fastHashing:
                                 #ls --time-style +%Y%m%d%H%M$S%N -l TESV/SkyrimSE.exe | cut -d ' ' -f6
                    cmdHashing = f"mkdir -p {mPathRoot} && "\
                                 f"touch {mPath}  && "\
                                 f"echo \"{vfsPath_json}.$( ls --time-style +%Y%m%d%H%M -l {vfsPath} | cut -d ' ' -f6 )\" > {mPath}"
                else:
                    cmdHashing = f"mkdir -p {mPathRoot} && "\
                                 f"touch {mPath} && "\
                                 f"md5sum {fPath} | cut -d ' ' -f1 > {mPath}"
                                
                cmdMnfsing = f"echo \"{mEntry}\" >> {manifestPathJson}"
                

                if os.path.exists(vfsPath):
                    command = f"{cmdHashing} && {cmdMnfsing}"
                else:
                    command = f"{cmdCopying} && {cmdHashing} && {cmdMnfsing}"
                if logging:
                    command = f"{cmdLogging} ; {command}"

                #print(f"queueing {command}")
                jobs[len(jobs)] = command
                vfsManifest[mPath_json] = fPath_json



logMsg = f"copying files to {vfsDir}..."
print(logMsg)
log(logMsg,logfile=logfile_in,v=verbose)


batchProcess(jobs,threadcount)


logMsg = f"saving {manifestPathJson}..."
print(logMsg)
log(logMsg,logfile=logfile_in,v=verbose)


command = f"cp {manifestPathJson} {manifestPathJson}.tmp && head -n -1 {manifestPathJson}.tmp > {manifestPathJson} && tail -1 {manifestPathJson}.tmp | cut -d ',' -f1 >> {manifestPathJson} && rm -f {manifestPathJson}.tmp"
batchProcess({0:command},threadcount)


command = 'echo "}" >> '
command += manifestPathJson
batchProcess({0:command},threadcount)


logMsg = "done copying files."
print(logMsg)
log(logMsg,logfile=logfile_in,v=verbose)


logMsg = 'finished loading virtual file system'
print(logMsg)
log(logMsg,logfile=logfile_in,v=verbose)
