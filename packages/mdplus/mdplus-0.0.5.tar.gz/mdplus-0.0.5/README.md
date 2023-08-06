# MDPlus: Python tools for molecular modelling. #

## Introduction

*MDPlus* brings together a number of tools related to the setup and analysis of molecular simulations:

* PCA - the Principal Component Analysis library as used by [pyPcazip](https://claughton.bitbucket.io/pypcazip.html).
  
* GLIMPS - a machine learning method for backmapping coarse-grained structures to finer-grained ones.

* REFINE - a constraints-based approach to the refinement of approximate molecular models.

----------

## Installation:

Easiest via pip:
```
pip install mdplus
```

---------------

## Getting started:


### API overview

For maximum compatibility with other Python-based MD simulation processing packages, All tools operate on simple arrays of coordinate data (typically [n_frames, n_atoms, 3] `numpy` arrays).

All tools have a similar API, modelled on the *transformer* object approach that used by many of the utilities in `scipy` and `scikit-learn`. 

### PCA

An instance of a PCA transformer is fit to an ensemble of structures, to obtain the eigenvectors, eigenvalues and mean. This trained transformer can then be used to transform further coordinate sets of the same system into the PCA space, and vice-versa:

```
from mdplus.pca import PCA

pca_transformer = PCA()
pca_transformer.fit(traj) # traj should be an [n_frames, n_atoms, 3] numpy array
scores = pca_transformer.transform(traj) # scores will be an [n_frames, n_components] numpy array
reconstituted_traj = pca_transformer.inverse_transform(scores)
```

### GLIMPS

While tools to transform high-resolution models to lower resolution ones (e.g. atomistic to coarse-grained) are relatively available and/or easy to implement, the reverse - "back-mapping" - is typically much harder. Given a training set of high-resolution structures and their low-resolution counterparts obtained by application of a forward-mapping tool, GLIMPS learns the reverse transform from the low resolution dataset to the higher resolution one, and once trained can back-map further low-resolution models. 

```
from mdplus.multiscale import GLIMPS

backmapper = GLIMPS()
backmapper.fit(cg_training_traj, fg_training_traj) # matched pairs of low and high resolution structures
fg_structure = backmapper.transform(cg_structure)
```

### REFINE

REFINE implements *SHAKE*-type constraints based refinement of approximate molecular structures. It can be a useful post-processor for structures obtained from PCA inverse transforms or from GLIMPS. REFINE learns the set of constraints from a training set of "good" molecular structures, and can then refine further approximate structures:

```
from mdplus.refinement import REFINE

refiner = REFINE()
refiner.fit(training_traj) # A diverse collection of good-quality structures
refined_traj = refiner.transform(crude_traj)
```

-----------------

## Who do I talk to?

* charles.laughton@nottingham.ac.uk



```python

```
