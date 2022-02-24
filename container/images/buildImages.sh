#!/bin/bash

#
# Copyright 2022 DataCanvas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

help() {
   echo ""
   echo "Usage: $0 -a VERSION -b REPOSITORY"
   echo -e "\t-a VERSION: represent the version of current, such as v0.2.0"
   echo -e "\t-b REPOSITORY: local docker or github repository, such as local,github"
   exit 1 # Exit script after printing help
}

while getopts "a:b:" opt
do
   case "$opt" in
      a ) VERSION="$OPTARG" ;;
      b ) REPOSITORY="$OPTARG" ;;
      ? ) help ;; # Print help in case parameter is non-existent
   esac
done

# Print help in case parameters are empty
if [ -z "$VERSION" ] || [ -z "$REPOSITORY" ] 
then
   help
fi

echo -e "0.=============Input: version=$VERSION, repository=$REPOSITORY========="

# stop1. delete old archive package
echo -e "1.=============remove old artifactory files==================="
[ -f dingo.zip ] && rm -rf dingo.zip && rm -rf ./tmp

# step2. unarchive `dingo.zip` and update the configuration 
ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd ../../ && pwd )"
DINGO_ZIP=$(find $ROOT -name dingo.zip)

echo -e "2.=============update dingo.zip with templates==================="
if [ -f "$DINGO_ZIP" ] ; then
    mkdir tmp && unzip $DINGO_ZIP -d tmp/ 
    cp -r ./templates/conf/* ./tmp/conf/ 
    cp -r ./templates/bin/* ./tmp/bin/
    rm -rf ./tmp/conf/config.yaml && rm -rf ./tmp/conf/logback.xml
else
    echo "$DINGO_ZIP does not exist, please copy the dingo.zip to artifactory"
    exit -1
fi

# Archive the dingo.zip package
cd ./tmp && zip -r dingo.zip * && cp dingo.zip .. && cd .. && rm -rf tmp

# step3. docker build the images
echo -e "3.=============build docker images on local machine==================="
DINGO_IMAGE_NAME=dingodb.ubuntu
DINGO_IMAGE_INTERNAL_REPO=172.20.3.185:5000/dingodb/$DINGO_IMAGE_NAME:$VERSION
docker build -t $DINGO_IMAGE_NAME:$VERSION .

# step3. upload the docker images to github or internal

IMAGEID=`docker images | grep $DINGO_IMAGE_NAME | grep $VERSION | awk '{print $3}'`
echo -e "4.=============dingodb $VERSION , current docker image: $DINGO_IMAGE_NAME is: $IMAGEID"


if [ $REPOSITORY == 'local' ]; then
   echo -e "4.1=============>current repository is local, will push image to: $DINGO_IMAGE_INTERNAL_REPO"
   docker tag $IMAGEID $DINGO_IMAGE_INTERNAL_REPO
   docker push $DINGO_IMAGE_INTERNAL_REPO
fi

if [ $REPOSITORY == 'github' ]; then
   echo -e "4.1=============>Current repository is: github"
fi

# step 5: remove the dingo.zip files
[ -f dingo.zip ] && rm -rf dingo.zip 
