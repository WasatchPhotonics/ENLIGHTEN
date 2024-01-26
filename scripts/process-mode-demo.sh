#!/bin/bash

################################################################################
# This script runs ENLIGHTEN within a "keepalive" wrapper.  If ENLIGHTEN 
# terminates abnormally (for instance, because memory growth exceeded specified
# limits or maximum runtime) and returns a non-zero exit code, the script 
# automatically relaunches ENLIGHTEN.  
#
# This is useful in process-monitoring deployments where it is understood that 
# various things may cause the computer or the program to terminate from time to 
# time, but that the key thing is that the program re-spawn and continue 
# monitoring the sample source.
################################################################################

ENLIGHTEN_GUI=$HOME/Enlighten-4.0.35/EnlightenGUI  # <-- customize for your env
LOGFILE=$HOME/run_enlighten.out     # holds output from this script
MAX_MEMORY_GROWTH=100               # 100% = 2x initial size
LOG_LEVEL=critical                  # debug|info|critical

log_info() 
{
    local MSG="$1"
    echo "$(date) $MSG" | tee --append $LOGFILE
}

log_info "----------------------------------------------"
log_info "run_enlighten started"

# keep re-running ENLIGHTEN until the process exits cleanly upon operator command
DONE=false
while ! $DONE
do
    log_info "spawning ENLIGHTEN"

    $ENLIGHTEN_GUI \
        --max-memory-growth $MAX_MEMORY_GROWTH \
        --log-level $LOG_LEVEL \
        1>/dev/null \
        2>~/enlighten.err 

    EXIT_CODE=$?
    log_info "ENLIGHTEN exited with $EXIT_CODE"

    if [ $EXIT_CODE -eq 0 ]
    then
        log_info "Exited cleanly...quitting" 
        DONE=true
    else
        log_info "Exited with error code $EXIT_CODE...respawning in 5 sec" 
        sleep 5
    fi
done

log_info "run_enlighten closed"
