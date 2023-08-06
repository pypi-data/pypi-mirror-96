# CarDEC

CarDEC (**C**ount **a**dapted **r**egularized **D**eep **E**mbedded **C**lustering) is a joint deep learning computational tool that is useful for analyses of single-cell RNA-seq data. CarDEC can be used to:

1. Correct for batch effect in the full gene expression space, allowing the investigator remove batch effect from downstream analyses like psuedotime analysis and coexpression analysis. Batch correction is also possible in a low-dimensional embedding space.
2. Denoise gene expression.
3. Cluster cells.

## Installation

Recomended installation procedure is as follows. 

1. Install [Anaconda](https://www.anaconda.com/products/individual) if you do not already have it. 
2. Create a conda environment, and then activate it as follows in terminal.

```
$ conda create -n cardecenv
$ conda activate cardecenv
```

3. Install an appropriate version of python.

```
$ conda install python==3.7
```

4. Install nb_conda_kernels so that you can change python kernels in jupyter notebook.

```
$ conda install nb_conda_kernels
```

5. Finally, install CarDEC.

```
$ pip install CarDEC
```

Now, to use CarDEC, always make sure you activate the environment in terminal first ("conda activate cardecenv"). And then run jupyter notebook. When you create a notebook to run CarDEC, make sure the active kernel is switched to "cardecenv"

## Usage

A [tutorial jupyter notebook](https://drive.google.com/drive/folders/19VVOoq4XSdDFRZDou-VbTMyV2Na9z53O?usp=sharing), together with a dataset, is publicly downloadable.

## Software Requirements
    
- Python >= 3.7
- TensorFlow >= 2.0.1, <= 2.3.1
- scikit-learn == 0.22.2.post1
- scanpy == 1.5.1
- louvain == 0.6.1
- pandas == 1.0.1
- scipy == 1.4.1

## Trouble shooting

Installation on MacOS should be smooth. If installing on Windows Subsystem for Linux (WSL), the user must properly configure their g++ compiler to ensure that the louvain package can be built during installation. If the compiler is not properly configured, the user may encounter a following deprecation error similar to the following.

"DEPRECATION: Could not build wheels for louvain which do not use PEP 517. pip will fall back to legacy 'setup.py install' for these. pip 21.0 will remove support for this functionality. A possible replacement is to fix the wheel build issue reported above."

To fix this error, try to install the libxml2-dev package.