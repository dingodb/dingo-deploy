#!/usr/bin/env bash

set -e

readonly SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${SCRIPT_ROOT}"

# shellcheck disable=SC2155
export dist_product=$(grep "^name: " artifacts/config.yml | sed -e "s/^name: //")
# shellcheck disable=SC2155
export dist_version=$(grep "^version: " artifacts/config.yml | sed -e "s/^version: //")

function indent() { sed "s/^/  👉 /"; }

# shellcheck disable=SC2154
installer_name=ansible-${dist_product}-${dist_version}
echo "#---------------------------------------------------------"
echo "#️ ⏳️ Creating installer: ${installer_name}"
echo "#---------------------------------------------------------"

echo "✅ Downloading artifacts"
artifacts/download.py 2>&1 | indent

echo "✅ Packaging ${installer_name}"
git archive --format=tar --prefix=${installer_name}/ HEAD -o ${installer_name}.tar
echo "✅ Adding artifacts to installer tarball"
mkdir -p ${installer_name}
ln -s ../artifacts ${installer_name}/artifacts
# shellcheck disable=SC2207
export TARBALLS=( $(artifacts/download.py resolve 2>/dev/null) )
# shellcheck disable=SC2068
for tarball in ${TARBALLS[@]}; do
  echo "  👉 $(basename ${tarball})"
  tar -rf ${installer_name}.tar ${installer_name}/artifacts/$(basename ${tarball})
done
rm -rf ${installer_name}
echo "😁 Done"
