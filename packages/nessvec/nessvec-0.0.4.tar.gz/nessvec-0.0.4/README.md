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
>>> from nessvec import util
>>> w2v = util.load_glove()
>>> w2v['seattle']
array([-2.7303e-01,  8.5872e-01,  1.3546e-01,  8.3849e-01, ...
>>> w2v['portland']
array([-0.78611  ,  1.2758   , -0.0036066,  0.54873  , -0.31474  ,...

>>> from nessvec.glove import NessVecs
>>> nv = NessVecs()
>>> util.cosine_similarity(nv.w2v['seattle'], nv.w2v['portland'])
.85
>>> util.cosine_similarity(nv.w2v['portland'], nv.w2v['seattle'])

>>> util.cosine_similarity(nv.w2v['los_angeles'], nv.w2v['mumbai'])
.5
```

##

