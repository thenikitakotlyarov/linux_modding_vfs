#!/bin/bash

DEFAULT_EXEC='skse64_loader.exe'

logfile='vfs_main.log'

./onLoad.py

if [[ -d vfs ]]; then
    echo "virtual file systems appears to have succesfully loaded;"
    echo "running game"
    cd vfs
    ./run.sh $DEFAULT_EXEC >> ../$logfile
    cd ../

    ./onUnload.py


    echo "done! exitting successfully"


else
    echo "virtual file system failed to load; exiting gracefully"
    exit


fi
