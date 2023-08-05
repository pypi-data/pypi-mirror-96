
![](/images/delaunay.jpg)


# Visualizations of Manifolds

- [x] Regular Grid

# Installation
```bashs
pip install manifold-plotter
```

# Usage

```python
import manifold_plotter as mp
import md_pro as md
import matplotlib.pyplot as plt

mygrid = {"x_grid": 5, "y_grid": 4, "x_min": -10, "x_max": 10, "y_min": -7.5, "y_max": 7.5}

# points
P = md.get_meshgrid_points(**mygrid)
# plot the nodes
mp.plot_patches(P)
plt.show()
```


... should produce:

![](/images/regular_grid.png)


# Citation

Please cite following document if you use this python package:
```
TODO
```


Image source: https://www.pexels.com/photo/full-frame-shot-of-architectural-structure-248921/?download-size=640x480