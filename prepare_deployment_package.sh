#!/usr/bin/env bash

rm -f target.zip
rm -rf target/

if [ `git status -s | wc -l` -gt 0 ]; then
  echo 'Warning! Uncommitted files will not be included in the deplyment package.'
fi
git clone --no-hardlinks . target/
rm -rf target/.git

pip install -r requirements.txt --target target/

cd target/
zip -q9r ../target.zip .
cd ..
rm -rf target/
