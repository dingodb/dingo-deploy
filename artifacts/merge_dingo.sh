#!/bin/bash
set -x

NEW_DIR=$(cd `dirname $0`; pwd)
echo ${NEW_DIR}
cd ${NEW_DIR}
mkdir dingo
tar -zxvf dingo-store.tar.gz -C dingo
unzip dingo.zip -d dingo
rm -f dingo/conf/coordinator.yaml
rm -f dingo/conf/store.yaml
if [ -d dingo/dingo ]; then
        echo "dingo.zip have two layer"
        cp -rf  dingo/dingo/* dingo/
        rm -rf dingo/dingo
fi
cd dingo
tar -czvf ../dingo.tar.gz ./*
cd ..
rm -rf dingo