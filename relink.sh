#!/usr/bin/env bash

readonly SCRIPT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${SCRIPT_ROOT}"

echo "[1/4] Linking _shared.yml"
rm -f shared.yml
ln -s group_vars/all/_shared.yml shared.yml

echo "[2/4] Linking customize.yml"
rm -f customize.yml
ln -s group_vars/all/customize.yml customize.yml

echo "[3/4] Linking hosts"
rm -f hosts.ini
ln -s inventory/hosts hosts.ini

echo "[4/4] Updating .gitattributes"
tee .gitattributes >/dev/null <<EOF
.gitattributes export-ignore
.gitignore export-ignore
artifacts/.placeholder export-ignore
artifacts/download.py export-ignore
inventory/hosts export-ignore
config.sh export-ignore
relink.sh export-ignore
package.sh export-ignore
README.md export-ignore
EOF
