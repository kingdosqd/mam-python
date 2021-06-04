#!/usr/bin/env python3
# -*-  codeing : utf-8 -*-


from setuptools import setup, Extension

bbc_module = Extension("_bbc_lib", sources = ['bbc_lib_wrap.cxx', 'bbc_lib.cpp'],)  

setup(name = 'bbc_lib',version = '1.0',author = 'shang_qd',description = 'bbc C++ lib',
        author_email = 'shang_qd@qq.com',packages = ['bbc'],
        ext_modules = [bbc_module],py_modules = ['bbc_lib'],) 
