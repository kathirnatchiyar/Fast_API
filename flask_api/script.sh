#!/bin/bash

# This is just a test provisioner script
percent=0
for i in {1..20}; do 
    percent=$((percent+5))
    echo "inside the provisioner"
    echo "Provisioning DB is going on..."
    echo "deployment progress - ${percent}"
    sleep 10
done