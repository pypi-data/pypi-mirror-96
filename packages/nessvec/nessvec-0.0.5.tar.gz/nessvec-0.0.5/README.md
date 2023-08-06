# nessvec

## Installation

```console
pip install nessvec
```

OR

```console
$ git clone git@gitlab.com:tangibleai/nessvec
$ cd nessvec
$ pip install -e .
```

## Get Started

```python
>>> from nessvec.util import load_glove
>>> w2v = load_glove()
>>> seattle = w2v['seattle']
>>> seattle
array([-2.7303e-01,  8.5872e-01,  1.3546e-01,  8.3849e-01, ...
>>> portland = w2v['portland']
>>> portland
array([-0.78611  ,  1.2758   , -0.0036066,  0.54873  , -0.31474  ,...
>>> len(portland)
50
>>> from numpy.linalg import norm
>>> norm(portland)
4.417...
>>> portland.std()
0.615...

```

```python
>>> from nessvec.glove import NessVecs
>>> from nessvec.util import cosine_similarity
>>> nv = NessVecs()
>>> cosine_similarity(nv.w2v['seattle'], nv.w2v['portland'])
0.84...
>>> cosine_similarity(nv.w2v['portland'], nv.w2v['seattle'])
0.84...

```

```python
>>> cosine_similarity(nv.w2v['los_angeles'], nv.w2v['mumbai'])
.5

```

##

