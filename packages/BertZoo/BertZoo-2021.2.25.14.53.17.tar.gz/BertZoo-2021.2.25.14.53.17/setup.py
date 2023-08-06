#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.iapp
# @File         : setup
# @Time         : 2019-06-17 16:12
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :


import os
import time
from pathlib import Path
from setuptools import find_packages, setup

# rename
package_name = Path(__file__).absolute().parent.name
version = time.strftime("%Y.%m.%d.%H.%M.%S", time.localtime())

with open("README.md", encoding='utf-8') as f:
    long_description = f.read()


def get_requirements():
    _ = './requirements.txt'
    if os.path.isfile(_):
        with open(_, encoding='utf-8') as f:
            return f.read().split('\n')


setup(
    name=package_name,
    version=version,
    url=f'https://github.com/Jie-Yuan/{package_name}',
    keywords=["tool wheel", "yuanjie", 'utils'],
    description=('description'),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='YuanJie',
    author_email='313303303@qq.com',
    maintainer='JieYuan',
    maintainer_email='313303303@qq.com',
    license='Apache',
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.*']},
    platforms=["all"],
    # python_requires='>=3.6',
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
    ],

    install_requires=get_requirements(),

    entry_points={
        'console_scripts': [
            'x-cli=x.cli:cli'
        ]
    }

)

if __name__ == '__main__':
    print(__file__)
