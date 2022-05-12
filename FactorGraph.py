from matplotlib import rc
from matplotlib import pyplot as plt

rc("font", family="serif", size=14)
rc("text", usetex=True)
plt.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]

import os
import daft
fig_width= 5 
fig_height= 8
node_scale = 1.75
pgm = daft.PGM([fig_width, fig_height], origin=[0, 0], observed_style="shaded")

# Functions
pgm.add_node(daft.Node(name="pG", content=r"$p(g|i,d)$",x=1, y=1, shape="rectangle", scale=node_scale))
pgm.add_node(daft.Node(name="pD", content=r"$p(d)$",x=1, y=2.5, shape="rectangle", scale=node_scale))
pgm.add_node(daft.Node(name="pI", content=r"$p(i)$",x=1, y=4, shape="rectangle", scale=node_scale))
pgm.add_node(daft.Node(name="pS", content=r"$p(s|i)$",x=1, y=5.5, shape="rectangle", scale=node_scale))
pgm.add_node(daft.Node(name="pL", content=r"$p(l|g)$",x=1, y=7, shape="rectangle", scale=node_scale))

# RVs
pgm.add_node(daft.Node(name="G", content=r"$G$",x=4, y=1, shape="ellipse", scale=node_scale))
pgm.add_node(daft.Node(name="D", content=r"$D$",x=4, y=2.5, shape="ellipse", scale=node_scale))
pgm.add_node(daft.Node(name="I", content=r"$I$",x=4, y=4, shape="ellipse", scale=node_scale))
pgm.add_node(daft.Node(name="L", content=r"$L$",x=4, y=5.5, shape="ellipse", scale=node_scale))
pgm.add_node(daft.Node(name="S", content=r"$S$",x=4, y=7, shape="ellipse", scale=node_scale))

# Edges
directed=False
pgm.add_edge("pG", "G",directed)
pgm.add_edge("pG", "I",directed)
pgm.add_edge("pG", "D",directed)

pgm.add_edge("pD", "D",directed)

pgm.add_edge("pI", "I",directed)

pgm.add_edge("pS", "S",directed)
pgm.add_edge("pS", "I",directed)

pgm.add_edge("pL", "L",directed)
pgm.add_edge("pL", "G",directed)

# Render and save.
pgm.render()
pgm.figure.savefig("figure.pdf")
pgm.figure.savefig("figure.png", dpi=150)
