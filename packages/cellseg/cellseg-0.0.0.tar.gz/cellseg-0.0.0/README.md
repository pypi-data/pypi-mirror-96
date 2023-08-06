# cellseg: Multiclass Cell Segmentation 

[![PyPI version](https://badge.fury.io/py/cellseg.svg)](https://badge.fury.io/py/cellseg) 
![Stage](https://www.repostatus.org/badges/latest/active.svg)
![Test Install](https://github.com/Nelson-Gon/cellseg/workflows/Test%20Install/badge.svg)
![Travis Build](https://travis-ci.com/Nelson-Gon/cellseg.svg?branch=main)
[![PyPI license](https://img.shields.io/pypi/l/cellseg.svg)](https://pypi.python.org/pypi/cellseg/) 
[![Documentation Status](https://readthedocs.org/projects/cellseg/badge/?version=latest)](https://cellseg.readthedocs.io/en/latest/?badge=latest)
[![Total Downloads](https://pepy.tech/badge/cellseg)](https://pepy.tech/project/cellseg)
[![Monthly Downloads](https://pepy.tech/badge/cellseg/month)](https://pepy.tech/project/cellseg)
[![Weekly Downloads](https://pepy.tech/badge/cellseg/week)](https://pepy.tech/project/cellseg)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Nelson-Gon/cellseg/graphs/commit-activity)
[![GitHub last commit](https://img.shields.io/github/last-commit/Nelson-Gon/cellseg.svg)](https://github.com/Nelson-Gon/cellseg/commits/main)
[![GitHub issues](https://img.shields.io/github/issues/Nelson-Gon/cellseg.svg)](https://GitHub.com/Nelson-Gon/cellseg/issues/)
[![GitHub issues-closed](https://img.shields.io/github/issues-closed/Nelson-Gon/cellseg.svg)](https://GitHub.com/Nelson-Gon/cellseg/issues?q=is%3Aissue+is%3Aclosed)

**Introduction**



`cellseg` is a PyTorch (`torch`) based deep learning package aimed at multiclass cell segmentation.

**Installation**

```shell
pip install cellseg 
```
Or if you want to build from source 

```shell
git clone git@github.com:Nelson-Gon/cellseg.git
cd cellseg
python setup.py install 

```

**Development stage**

- [x] Read Tiff Images

- [x] Read Non Tiff Images

- [x] Write Data Transformers and Loaders

- [ ] Write functional model 

- [ ] Modify model weights/layers




**Usage**

```python
# imports data, utils, model 
from cellseg import *
```