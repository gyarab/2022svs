#!/bin/bash

rm avava-hello
mkdir -p build

python3 -m pip install -r requirements.txt --target build
cp -r hello/* build

python3 -m zipapp -p "/usr/bin/env python3" build

rm -r build
mv build.pyz avava-hello
