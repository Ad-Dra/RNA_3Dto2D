# RNA Python - FR3D

Our custom version of FR3D with some changes to the output formats

[FR3D](https://www.bgsu.edu/research/rna/software/fr3d.html) stands for "Find RNA 3D" and is commonly pronounced "Fred". FR3D enables searching and annotating RNA 3D structures and supports the [mmCIF](https://mmcif.wwpdb.org) format.

Originally [written in Matlab](https://github.com/BGSU-RNA/FR3D), this repository is a re-implementation of FR3D in Python. FR3D and FR3D Python are developed by the [BGSU RNA Bioinformatics group](http://rna.bgsu.edu).

### Understanding the output

The program `NA_pairwise_interactions.py` generates tab-separated files called `<pdb_id><bondType><outputFormat>_<modelNumber>.txt` that list basepair interactions between pairs of nucleotides (an RNA 3D structure can contain 0 or more basepairs). The output format can be chosen between "bpseq" and "aas".

## Installation 

### Clone RNA Python - FR3D


git clone "ourReposLink"
cd RnaPython
python setup.py install


:warning: Any time files such as `fr3d/cif/reader.py` get edited, you need to rerun the `python setup.py install` command.


### Set up on Python 2.7

*fr3d-python requires PDBx*. Follow [instructions at wwPDB](https://mmcif.wwpdb.org/docs/sw-examples/python/html/) to install PDBx on your local machine and place in your Python path.

### Set up on Python 3.x

In order to use FR3D in Python 3, you will need to install the [mmcif-pdbx](https://pypi.org/project/mmcif-pdbx/) package:


pip install mmcif-pdbx


This will put the PDBx package in your Python path.

## Running RNA Python - FR3D

Navigate to the [classifiers](fr3d/classifiers) folder and run the following command to ensure that the installation was successful:

python NA_pairwise_interactions.py --help

:warning: You will need download and put the file [localpath.py](https://github.com/draibineAdnane/RnaPython/blob/dev/fr3d/localpath.py) to represent your file structure and specify standard input and output paths.

:warning: The file [localpath.py] needs to be downloaded even if you do not intend to use it !!!

You can than use the `--input` (`-i`) and `--output` (`-o`) flags to specify the location of your input cif files and the output text files.

For example, if you already have the .cif file downloaded, use the `--input` flag to specify the directory your cif file is in,
where <path_to_input> is the path of the folder that contains the file <pdb_id>.cif

python NA_pairwise_interactions.py --input <path_to_input> -p <pdb_id>

Additionally, if you don't have the cif file in your localpath, you can run

python NA_pairwise_interactions.py -p <pdb_id>.cif

and this will download the file for processing and run the program from the database.

Output can be specified using the `-ou` or `--output` tags, for example:

python NA_pairwise_interactions.py --output <path_to_output> -p <pdb_id>


This will write where you wish to output your annotations. If the specified directory doesn't exist, one will be made.

To run the program once [localpath.py] has been downloaded, use the command


python NA_pairwise_interactions.py -p <pdb_id>


if you want to process the RNA <pbd_id>, otherwise if you want to process the entire content of a folder use just


python NA_pairwise_interactions.py


## Additional input flags

### -l (--category) 

allows to filter in the output the type of interaction that you want to annotate, if omitted the categorys will automatically be set to the standard
Leontis_Westhof_basepairs = ['cWW', 'cSS', 'cHH', 'cHS', 'cHW', 'cSH', 'cSW', 'cWH', 'cWS', 'tSS', 'tHH', 'tHS', 'tHW', 'tSH', 'tSW', 'tWH', 'tWS', 'tWW'], for example


python NA_pairwise_interactions.py -p <pdb_id> -l cWW,tHS,tSS


### -o (--outputFormat) 

allows to filter in the output the type of interaction that you want to annotate  ("bpseq" or "aas")
if this is omitted the output format is set to bpseq, for example


python NA_pairwise_interactions.py -p <pdb_id> -o aas


### -a

this is a boolean flag, if present all the bonds specified will be annotated into the same outputFile, in this case the output format is automatically set to "aas" (even if the flag -o bpseq) is present, for example


python NA_pairwise_interactions.py -p <pdb_id> -a


### -aa (--outputFormat) 

allows to filter in the output the type of interaction that you want to annotate  ("bpseq" or "aas")
if this is omitted the output format is set to bpseq, for example

python NA_pairwise_interactions.py -p <pdb_id> -aa

### -mn (--modelNumber)

This flag allows you to filter the model number that will be processed, for example

python NA_pairwise_interactions.py -p <pdb_id> -mn 1,2,3,4
