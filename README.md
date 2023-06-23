# RNA Python - FR3D

This repository contains our customized version of FR3D with modifications made to the input and output formats.

## Overview

FR3D: short for "Find RNA 3D," is a powerful tool used for searching and annotating RNA 3D structures. It is often referred to as "Fred" for convenience. FR3D supports the mmCIF format and was initially implemented in Matlab, then re-implemented in python by the BGSU RNA Bioinformatics group.

In this repository, we present a modified version of FR3D-Python, providing the same functionality with added functionalities. Our version offers enhanced flexibility in determining the secondary structure of a 3D RNA chain. Specifically, it allows users to specify the type of bonds they wish to display in the output 2D structure. By utilizing this tool, users can obtain the structure in bpseq, aas, or even graphical representations of the arc diagram such as png or tkz (compatible with LaTeX).

Additionally, we have included a tool called `2dToTkz.py` that allows the conversion from aas or bpseq formats to a tkz file, further enhancing the versatility of the output options (more about this at the end of this document).

### Understanding the output

The program `NA_pairwise_interactions.py` generates tab-separated files called `<pdb_id><bondType>_<outputFormat>_<modelNumber>.txt` that list basepair interactions between pairs of nucleotides (an RNA 3D structure can contain 0 or more basepairs). The output format can be chosen between "bpseq", "aas", "tkz" or "png" (last 2 for a graphical representations of the arc diagram).

## Getting Started

### Clone RNA Python - FR3D

```
git clone https://github.com/draibineAdnane/RnaPython.git
cd RnaPython
python setup.py install
```

:warning: Any time files such as `fr3d/cif/reader.py` get edited, you need to rerun the `python setup.py install` command.


### Set up on Python 2.7

*fr3d-python requires PDBx*. Follow [instructions at wwPDB](https://mmcif.wwpdb.org/docs/sw-examples/python/html/) to install PDBx on your local machine and place in your Python path.

### Set up on Python 3.x

In order to use FR3D in Python 3, you will need to install the [mmcif-pdbx](https://pypi.org/project/mmcif-pdbx/) package:

```
pip install mmcif-pdbx
```

This will put the PDBx package in your Python path.

## Running RNA Python - FR3D

Navigate to the [classifiers](path  /fr3d/classifiers ) folder and run the following command to ensure that the installation was successful:

```
python NA_pairwise_interactions.py --help
```

:warning: You will need download and put the file [localpath.py](link /fr3d/localpath.py) to represent your file structure and specify standard input and output paths. 

:warning: The file [localpath.py] needs to be downloaded even if you do not intend to use it !!!

You can than use the `--input` (`-i`) and `--output` (`-o`) flags to specify the location of your input cif files and the output text files.

For example, if you already have the .cif file downloaded, use the `--input` flag to specify the directory your cif file is in,
where <path_to_input> is the path of the folder that contains the file <pdb_id>.cif


```
python NA_pairwise_interactions.py --input <path_to_input> -p <pdb_id>
```

Additionally, if you don't have the cif file in your localpath, you can run

```
python NA_pairwise_interactions.py -p <pdb_id>.cif
```

and this will download the file for processing and run the program from the database.

Output can be specified using the `-ou` or `--output` tags, for example:

```
python NA_pairwise_interactions.py --output <path_to_output> -p <pdb_id>
```

This will write where you wish to output your annotations. If the specified directory doesn't exist, one will be made.

To run the program once [localpath.py] has been downloaded, use the command

```
python NA_pairwise_interactions.py -p <pdb_id>
```

if you want to process the RNA <pbd_id>, otherwise if you want to process the entire content of a folder use just

```
python NA_pairwise_interactions.py
```

## Additional input flags

### -l (--category) 

allows to filter in the output the type of interaction that you want to annotate, if omitted the categorys will automatically be set to the standard
Leontis_Westhof_basepairs = ['cWW', 'cSS', 'cHH', 'cHS', 'cHW', 'cSH', 'cSW', 'cWH', 'cWS', 'tSS', 'tHH', 'tHS', 'tHW', 'tSH', 'tSW', 'tWH', 'tWS', 'tWW'], for example

```
python NA_pairwise_interactions.py -p <pdb_id> -l cWW,tHS,tSS
```

### -o (--outputFormat) 

with this option you can decide the output format, write after -o all the formats that you wish to be outputted separeted by comma ("bpseq", "aas" or for arc diagram "png", "tkz")
if this is omitted the output format is set to bpseq, 
example of output formats:

```
python NA_pairwise_interactions.py -p <pdb_id> -o aas,tkz
```

this will produce txt for both aas and tkz files

### -a

The `-a` flag is a boolean option. When present, it annotates all the specified bonds in a single outputFile. In this case, the output format is automatically set to "aas" (even if the `-o bpseq` flag is present).

Example usage:
```
python NA_pairwise_interactions.py -p <pdb_id> -a
```

### -aa (--outputFormat) 

The `-aa` is a boolean flag, when present it overrides the `-a` flag. When this flag is present the tool will produce 1 file for every bond type found + a file that contains every bond type. Also in this case, the output format is automatically set to "aas" (even if the `-o bpseq` flag is present).

```
python NA_pairwise_interactions.py -p <pdb_id> -aa
```

### -mn (--modelNumber) 

This flag allows you to filter the model number that will be processed, for example

```
python NA_pairwise_interactions.py -p <pdb_id> -mn 1,2,3,4
```

## 2dToTkz

If you want to convert existing aas or bpseq files into the tkz format, you can use the `2dToTkz.py` script.

To utilize this feature, follow these steps:

1. Navigate to the `../fr3d/extension` folder.
2. Use the following command: `python 2dToTkz.py [inputFilePath] [outputFilePath]`

