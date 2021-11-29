#!/bin/bash

while true
do
    
    echo $(date) : docker run --rm -ti -v $(realpath ../work):/mnt jorf:ftps python /opt/jorf/config/docker.yml
    docker run --rm -ti -v $(realpath ../work):/mnt jorf:ftps python main.py /opt/jorf/config/docker.yml
    
    echo "$(date) : end of process"
    sleep 3600
    sleep 3600
    sleep 3600
done
