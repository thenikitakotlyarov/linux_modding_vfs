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
    writeFileBytes(logfile_out,b'')


if fastHashing:
    manifestPathPrior = manifestPath
    manifestPathPost = manifestPath


logMsg = 'unloading virtual file system'
print(logMsg)
log(logMsg,logfile=logfile_out,v=verbose)


priorFiles = loadJson(manifestPathJson)
#log(f"PRIOR:\t{priorFiles}",logfile=logfile_out,v=verbose)

postFiles = dict()
vfsManifest = dict()

command = 'echo "{" > '
command += manifestPathJson
batchProcess({0:command})
jobs = dict()



#walk the virtual file system and establish manifest post-game
log('looking for changes compared to prior to game running',logfile=logfile_out,v=verbose)

for fPath in  glob.glob(f"{vfsDir}/**", recursive=True):
        skip = False
        if os.path.isdir(fPath):
            skip = True
        else:
            for b in blacklist:
                if fPath[:len(b)] == b:
                    skip = True

        if not skip:

            splitIdx = 2
            mPath = f"{manifestPathPost}/{'/'.join(fPath.split('/')[splitIdx:])}"
            mPathRoot = '/'.join([ _ for _ in mPath.split('/')][:-1])
            overwritePath = f"{overwriteDir}/{'/'.join(fPath.split('/')[splitIdx:])}"
            fPath_json = fPath
            mPath_json = mPath
            logMsg = f"linking logically:\t{mPath} -> {fPath}"
            for tc in troubleChars:
                fPath = fPath.replace(tc,'\\'+tc)
                mPath = mPath.replace(tc,'\\'+tc)
                mPathRoot = mPathRoot.replace(tc,'\\'+tc)
                if tc not in  (' ','&',"'"):
                    fPath_json = fPath_json.replace(tc,'\\'+tc)
                    mPath_json = mPath_json.replace(tc,'\\'+tc)
                    logMsg = logMsg.replace(tc,'\\'+tc)
            if mPath_json not in vfsManifest:
                if verbose:
                    log(f"creating job to touch {mPath} and hash {fPath} into it",logfile=logfile_in,v=verbose)

                mEntry = f"\t\\\"$(cat {mPath})\\\": \\\"{fPath_json}\\\","

                cmdLogging = f"echo \"{logMsg}\" >> {logfile_main}"
                                
                if fastHashing:
                                 #ls --time-style +%Y%m%d%H%M$S%N -l TESV/SkyrimSE.exe | cut -d ' ' -f6
                    cmdHashing = f"mkdir -p {mPathRoot} && "\
                                 f"touch {mPath}  && "\
                                 f"echo \"{fPath_json}.$( ls --time-style +%Y%m%d%H%M -l {fPath} | cut -d ' ' -f6 )\" > {mPath}"
                else:
                    cmdHashing = f"mkdir -p {mPathRoot} && "\
                                 f"touch {mPath} && "\
                                 f"md5sum {fPath} | cut -d ' ' -f1 > {mPath}"
                                
                cmdMnfsing = f"echo \"{mEntry}\" >> {manifestPathJson}"
                
                command = f"{cmdHashing} && {cmdMnfsing}"
                if logging:
                    command = f"{cmdLogging} ; {command}"
                #print(f"queueing {command}")
                jobs[len(jobs)] = command
                vfsManifest[mPath_json] = fPath_json



logMsg = f"hashing files to {manifestPathPost}..."
print(logMsg)
log(logMsg,logfile=logfile_in,v=verbose)


batchProcess(jobs,threadcount)


logMsg = f"saving {manifestPathJson}..."
print(logMsg)
log(logMsg,logfile=logfile_in,v=verbose)


command = f"cp {manifestPathJson} {manifestPathJson}.tmp && head -n -1 {manifestPathJson}.tmp > {manifestPathJson} && tail -1 {manifestPathJson}.tmp | cut -d ',' -f1 >> {manifestPathJson}"
batchProcess({0:command},threadcount)


command = 'echo "}" >> '
command += manifestPathJson
batchProcess({0:command},threadcount)


postFiles = loadJson(manifestPathJson)

changes = False
for fileHash in postFiles:
    fileSrc = postFiles[fileHash]
    if fileHash not in priorFiles:
        changes = True
        #log(f"{fileSrc} detected as new file!",logfile=logfile_out,v=verbose)
        log(f"\twriting {fileSrc} to overwrite",logfile=logfile_out,v=verbose)
        writeChanges(fileSrc)
    else:
        pass
        # if priorFiles[fileSrc] == postFiles[fileSrc]:
        #     #log(f"{fileSrc} unchanged",logfile=logfile_out,v=verbose)
        #     pass
        # else:
        #     log(f"{fileSrc} changes detected!",logfile=logfile_out,v=verbose)
        #     log(f"\tsrc: {priorFiles[fileSrc]}\n"\
        #           "\t-> dst: {postFiles[fileSrc]}",logfile=logfile_out,v=verbose)
        #     log(f"\twriting {fileSrc} to overwrite",logfile=logfile_out,v=verbose)
        #     writeChanges(fileSrc)

if not changes:
    logMsg = "no changes found; no files copied"
    print(logMsg)
    log(logMsg,logfile=logfile_out,v=verbose)
else:
    logMsg = "changes were found; files were copied"
    print(logMsg)
    log(logMsg,logfile=logfile_out,v=verbose)

    
        
if removeDuringUnload:
    log('done, removing vfs',logfile=logfile_out,v=verbose)
    shutil.rmtree(vfsDir)
    log('done, removing manifest',logfile=logfile_out,v=verbose)
    shutil.rmtree('./manifest')


logMsg = 'finished unloading virtual file system'
print(logMsg)
log(logMsg,logfile=logfile_out,v=verbose)
