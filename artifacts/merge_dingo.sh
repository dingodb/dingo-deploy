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
cp ${NEW_DIR}/sqlline-*-SNAPSHOT-jar-with-dependencies.jar libs/
# sed修改store-gflags.conf、index-gflags.conf、coordinator-gflags.conf的变量值
#sed -i 's/-min_system_disk_capacity_free_ratio=0.05/-min_system_disk_capacity_free_ratio=0.05/g' conf/store-gflags.conf
#sed -i 's/-min_system_memory_capacity_free_ratio=0.10/-min_system_memory_capacity_free_ratio=0.10/g' conf/store-gflags.conf
#sed -i 's/-storage_worker_num=32/-storage_worker_num=32/g' conf/store-gflags.conf
#
#sed -i 's/-min_system_disk_capacity_free_ratio=0.05/-min_system_disk_capacity_free_ratio=0.05/g' conf/index-gflags.conf
#sed -i 's/-min_system_memory_capacity_free_ratio=0.10/-min_system_memory_capacity_free_ratio=0.10/g' conf/index-gflags.conf
#sed -i 's/-storage_worker_num=16/-storage_worker_num=16/g' conf/index-gflags.conf
#
#sed -i 's/-max_hnsw_memory_size_of_region=2147483648/-max_hnsw_memory_size_of_region=2147483648/g' conf/coordinator-gflags.conf
tar -czvf ../dingo.tar.gz ./*
cd ..
rm -rf dingo