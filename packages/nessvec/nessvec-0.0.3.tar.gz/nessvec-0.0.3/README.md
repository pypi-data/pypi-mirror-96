# nessvec

## Installation

>>>
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

```
##

