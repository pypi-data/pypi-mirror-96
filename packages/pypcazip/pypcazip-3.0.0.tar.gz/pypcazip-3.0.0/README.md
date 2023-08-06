# pyPcazip: PCA-based trajectory file compression. #


pyPcazip uses Principal Component Analysis (PCA) to compress molecular dynamics (MD) trajectory files.

The approach is (controllably) lossy, but in the right situations is very effective:

* When the system behaviour is not diffusive (avoid ions and solvent).
* When the trajectory is free of periodic boundary condition artifacts.
* When loss of information about global translation and rotation is not an issue.

The current code (V3) is a complete re-write of the previous version (V2) and incompatible with it. For information about V2,
please see the [Wiki](https://bitbucket.org/ramonbsc/pypcazip/wiki/Home).

## Background:

Taking a trajectory as a \[n_frames, n_coordinates] 2D array (n_coordinates=3\*n_atoms), PCA allows this to be
deconstructed into an \[n_scores, n_coordinates] 2D array of *eigenvectors* plus an \[n_frames, n_scores] 2D 
array of *scores* (where typically, n_scores << n_coordinates), plus an \[n_coordnates] vector for the *mean* structure (global translation and rotation of the system
being, conventionally, removed prior to analysis).

The total number of values in the trajectory is (n_frames * n_coordinates), in the PCA deconstruction this becomes
(n_scores * n_coordinates + n_frames * n_scores + n_coordinates). So if we have a trajectory of 10000 frames, 
each of 600 coordinates, that by PCA can be represented to satisfactory accuracy by, say, 200 scores, then:

    Original size = 600 * 10000 = 6,000,000
    Compressed size = 600 * 200 + 10000 * 200 + 600 = 2,120,600

I.e, PCA has the potential to achieve a about 3-fold compression.

PyPcazip implements this strategy, in addition using data compression techniques (similar to those used in the GROMACS xtc
format) to achive even smaller file sizes.


## Installation

From pip:

    pip install pypcazip
	
## Usage:

To compress a trajectory file:

    pyPcazip traj.xtc traj.pcz
	
To uncompress a trajectory file:

    pyPcaunzip traj.pcz traj.dcd
	
Pypcazip can read and write any of the trajectory file formats supported by [MDTraj](http://mdtraj.org). 
Some file formats may require a compatible parameter/topology file to be available:

    pyPcazip traj.mdcrd traj.pcz -p system.prmtop
	
## Advanced usage: tuning compression parameters

PyPcazip uses a hybrid compression approach. Each trajectory frame is approximated using the PCA approach described above, then the residual reconstruction error is encoded using conventional bit-packing techniques.
As a result there are three tunable parameters, though the defaults should work
well for most cases:

The percentage of the total variance captured by PCA defaults to 0.75, but can be tweaked:

    pyPcazip traj.dcd traj.pcz -p system.pdb --explained_variance 0.9

In general though we find that adjusting this parameter has marginal effect.

The accuracy with which the eigenvectors are stored can also be adjusted. The default scaling factor (100) works for most systems but on very large or small ones it may be worth changing by +/- an order of magnitude, perhaps:

    pyPcazip traj.dcd traj.pcz -p system.pdb --eigenvector_scale 1000

The accuracy with which the residual reconstruction error is stored can also be altered, this parameter has the most direct effect on the accuracy/compression balance. Values of between 50 and 800 may be worth investigating, and as a special case it can be set to zero, in which case no residuals are stored at all and the accuracy of the process depends purely on the PCA part of the process. In such cases it will almost certainly be neccessary to raise the default value of --explained_variance to 0.95 or greater:

    pyPcazip traj.dcd traj.pcz -p system.pdb --residual_scale 0 --explained_variance 0.97
 


## Who do I talk to? ##

* charles.laughton@nottingham.ac.uk (This version)
* ardita.shkurti@nottingham.ac.uk (Previous versions, Repo admin)
* rgoni@mmb.pcb.ub.es (Previous versions, Repo owner/admin)

## Other contributors: ##

* e.breitmoser@epcc.ed.ac.uk
* ibethune@epcc.ed.ac.uk
* kwabenantim@yahoo.com

![logos.jpg](https://bitbucket.org/repo/XRMEjz/images/965878357-logos.jpg)
