# RNA3Dto2D
## _RNA 3D Structure to 2D_

RNA3Dto2D is a RNA structure converter/visualizer, powered by FR3D.

## Citation
[FR3D](https://www.bgsu.edu/research/rna/software/fr3d.html) is a powerful tool developed by [BGSU](https://www.bgsu.edu) to find small RNA motifs (two to 20 nucleotides) in RNA 3D structures from the Protein Data Bank.  

## Papers
**FR3D: Finding Local and Composite Recurrent Structural Motifs in RNA 3D Structures**
Michael Sarver · Craig L. Zirbel · Jesse Stombaugh · Ali Mokdad · Neocles B. Leontis
[Journal of Mathematical Biology](http://link.springer.com/journal/285). 56, Nos. 1-2, January 2008. [pdf](http://link.springer.com/article/10.1007%2Fs00285-007-0110-x).

## Goal of the tool
The goal of the tool is to convert PDBx/mmCIF files into AAS/BSEQ files and supply a visual output to TIKZ or PNG. We used FR3D to identify base pairs.

## Installation
Start by cloning this repository and executing the script `setup.py`

```sh
git clone https://github.com/draibineAdnane/RnaPython.git
cd RnaPython/3Dto2D/FR3D
python setup.py install
```

### Set up on Python 2.7

*fr3d-python requires PDBx*. Follow [instructions at wwPDB](https://mmcif.wwpdb.org/docs/sw-examples/python/html/) to install PDBx on your local machine and place in your Python path.

### Set up on Python 3.x

In order to use FR3D in Python 3, you will need to install the [mmcif-pdbx](https://pypi.org/project/mmcif-pdbx/) package:

```
pip install mmcif-pdbx
```

This will put the PDBx package in your Python path.

## Usage example
# //TODO:
## Options 
- Input path **(mandatory)**
_If the argument is not a directory and a file is not found, it will be downloaded._
```sh
--input_path <path_to_dir>
--input_path <path_to_pdb>
--input_path <pdb_id>
```
- Output path **(mandatory)**
```sh
-output_FolderPath <path_to_dir>
```
- Output type(s) **(if omitted, the default type is BPSEQ)**
_Structures output file type: **AAS, BPSEQ**_
_Arc diagram output file type: **PNG, TKZ**_
```sh
-o aas,png
--outputFormat tkz
```
- Generates a file containing all the bonds 
_**In this case, the output format is automatically set to "aas" (even if the `-o bpseq` flag is present)**_
`Leontis_Westhof_basepairs = ['cWW', 'cSS', 'cHH', 'cHS', 'cHW', 'cSH', 'cSW', 'cWH', 'cWS', 'tSS', 'tHH', 'tHS', 'tHW', 'tSH', 'tSW', 'tWH', 'tWS', 'tWW']`
```sh
-a
```
- Only generates for specific bonds
```sh
-l cWW
--category tHS,tSS
```
- Generates one file containing all the bonds, and one for each bond found (overrides `-a`).
_**Also in this case, the output format is automatically set to "aas" (even if the `-o bpseq` flag is present).**_
```sh
-aa
```
- Model number to process (if omitted, all model numbers will be processed)
```sh
-mn 1
--modelNumber 1,2,3,4
```

## Extension
### 2dToTkz
To convert existing aas or bpseq files into the tkz format, you can use the `2dToTkz.py` script.

To utilize this feature, follow these steps:

1. Navigate to the `RnaPython/3Dto2D/extension` folder.
2. Use the following command: `python 2dToTkz.py [inputFilePath] [outputFilePath]`

## LICENSE
Apache 2.0
