Python implementations of the Weighted CLuster FuzzykCenters algorithms for fuzzy clustering categorical data:

## Installation:
### Using pip: 
```shell
pip install wcfkcenters
```

### Import the packages:
```shell
from WCFkCenters.WCFkCenters import WCFkCenters
from WCFkCenters import TDef
import numpy as np
```
### Generate a simple categorical dataset:

```shell
X = np.array([[0,0,0],[0,1,1],[0,0,0],[1,0,1],[2,2,2],[2,3,2],[2,3,2]])
y = np.array([0,0,0,0,1,1,1])
```

### LSHk-Representatives (Init): 

```shell
algo = WCFkCenters(X,y ,k=TDef.k, alpha=TDef.alpha)
algo.SetupMeasure("Overlap")
algo.DoCluster()
algo.CalcScore()


```

### Built-in evaluattion metrics:
```shell
algo.CalcFuzzyScore()
```

### Outcome:
```shell
SKIP LOADING distMatrix because: True bd=None yellow
Saving Overlap to: saved_dist_matrices/json/Overlap_None.json
>>> algo.DoCluster()
array([0, 0, 0, 0, 1, 1, 1], dtype=int64)
>>> algo.CalcScore()
Purity: 1.00 NMI: 1.00 ARI: 1.00 Sil:  0.59 Acc: 1.00 Recall: 1.00 Precision: 1.00
(1.0, 1.0, 1.0, 1.0, 1.0, 0.5873015873015872, 0.011969540000001189, -1, 1.0, 1.0, 1.0)
Fuzzy scores PC:1.00 NPC:1.00 FHV↓:0.02 FS↓:-2000.00 XB↓:0.11 BH↓:0.06 BWS:-2000.00 FPC:3.49 SIL_R:0.70 FSIL:0.70 MPO:12.18 NPE:0.01 PE:0.01 PEB:0.01
```

## Parameters:
X: Categorical dataset\
y: Labels of object (for evaluation only)\
n_init: Number of initializations \
n_clusters: Number of target clusters\
max_iter: Maximum iterations\
verbose: \
random_state: 

 
## Outputs:
cluster_representatives: List of final representatives\
labels_: Prediction labels\
u: Fuzzy membership
cost_: Final sum of squared distance from objects to their centroids\
n_iter_: Number of iterations\

## References:
*To be updated*
