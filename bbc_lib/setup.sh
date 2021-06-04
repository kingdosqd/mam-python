#!/usr/bin/env bash

swig -python -c++ bbc_lib.i
#python3 setup.py build test
python3 setup.py build_ext --inplace
python3 test.py

cp bbc_lib.py ../
cp _bbc* ../

rm -rf __pycache__
rm -rf build
rm bbc_lib_wrap.cxx
rm _bbc*
rm bbc_lib.py
