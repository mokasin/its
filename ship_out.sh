#!/bin/bash

echo "Version: "
read VERSION

mkdir -p shipout/its_$VERSION &> /dev/null
cp its.py its.default.conf shipout/its_$VERSION/

cd shipout

tar cjf its_$VERSION.tar.bz2 its_$VERSION/its.py its_$VERSION/its.default.conf

rm -r its_$VERSION
