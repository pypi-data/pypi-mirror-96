# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import time
from setuptools import setup, find_packages
from os import chdir, path, environ

chdir(path.abspath(path.dirname(__file__)))
version = __import__("reco_utils.__init__").VERSION

# Get the long description from the README file
with open("README.md", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

HASH = environ.get("HASH", None)
if HASH is not None:
    version += ".post" + str(int(time.time()))

DEPENDENCIES = [
    'flask==1.1.1',
    'requests==2.24.0',
    'pandas==1.1.3',
    'azureml-sdk[notebooks,tensorboard]==1.22.0',
    'azure-storage-blob<12.8.0',
    'azure-cli-core==2.19.1',
    'azure-mgmt-cosmosdb==6.0.0',
    'black>=18.6b4',
    'category_encoders>=1.3.0',
    'dataclasses>=0.6',
    'hyperopt==0.2.5',
    'idna==3.1',
    'locustio==0.999',
    'memory-profiler>=0.54.0',
    'nbconvert==6.0.7',
    'pydocumentdb>=2.3.3',
    'pymanopt==0.2.5',
    'xlearn==0.40a1',
    'tensorflow==2.4.1',
    'transformers==4.3.2',
    'tensorflow==2.4.0',
    'scrapbook>=0.5.0',
    'bottleneck==1.2.1',
    'dask>=0.17.1',
    'fastparquet>=0.1.6',
    'ipykernel>=4.6.1',
    'jupyter>=1.0.0',
    'lightfm==1.15',
    'matplotlib>=2.2.2',
    'mock==2.0.0',
    'nltk>=3.4',
    'numpy>=1.13.3',
    'pytorch-cpu>=1.0.0',
    'seaborn>=0.8.1',
    'scikit-learn>=0.19.1',
    'scipy>=1.0.0',
    'scikit-surprise>=1.0.6',
    'swig==3.0.12',
    'lightgbm==2.2.1',
    'cornac>=1.1.2',
    'papermill>=2.2.0',
    'tqdm>=4.31.1',
]

name = environ.get("LIBRARY_NAME", "pre_reco_utils")

setup(
    name=name,
    version=version,
    description="Recommender System Utilities",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/microsoft/recommenders",
    author="RecoDev Team at Microsoft",
    author_email="RecoDevTeam@service.microsoft.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="recommendations recommenders recommender system engine machine learning python spark gpu",
    package_dir={"reco_utils": "reco_utils"},
    packages=find_packages(where=".", exclude=["tests", "tools", "examples"]),
    install_requires=DEPENDENCIES,
    python_requires=">=3.6, <4",
)
