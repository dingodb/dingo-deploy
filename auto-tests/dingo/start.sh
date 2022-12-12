#!/bin/bash 
set -x
nohup docker-compose -f /root/dingo/docker-compose.yml down && docker rmi -f dingodatabase/dingo:latest && docker-compose -f /root/dingo/docker-compose.yml up -d >> /tmp/dingo.log 2>&1 &
