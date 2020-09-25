#!/bin/bash
#db_download.sh
#ssh ubuntu@130.60.24.72

# download database from server 
scp -o ServerAliveInterval=30 -o ServerAliveCountMax=1200 ubuntu@130.60.24.72:/home/ubuntu/Bullinger/app.db .
cp app.db Data/DB_Backups/app_$(date "+%Y.%m.%d-%H.%M.%S").db
