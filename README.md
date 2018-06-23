# ProjectNephos
GSOC 2018 Project: Automate recording and uploading TV Channels to cloud.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Build Status](https://travis-ci.org/AadityaNair/ProjectNephos.svg?branch=master)](https://travis-ci.org/AadityaNair/ProjectNephos)
[![Coverage Status](https://coveralls.io/repos/github/AadityaNair/ProjectNephos/badge.svg?branch=master)](https://coveralls.io/github/AadityaNair/ProjectNephos?branch=master)
[![Requirements Status](https://requires.io/github/AadityaNair/ProjectNephos/requirements.svg?branch=master)](https://requires.io/github/AadityaNair/ProjectNephos/requirements/?branch=master)
[![CodeFactor](https://www.codefactor.io/repository/github/aadityanair/projectnephos/badge)](https://www.codefactor.io/repository/github/aadityanair/projectnephos)


# Introduction
One of the function of the RedHen Organisation is to record and archive Television streams they receive for future
research. Project Nephos is an effort by CCExtractor to automate the entire process. Archiving is done by compressing
and uploading to Google Drive. 
In addition to downloading and archiving, Project Nephos provides the following functionalities:
1. Tagging of videos.
2. Searching archived videos.
3. Sharing videos with other entities (Not yet implemented.)

# Installation

### Using PyPI
Not yet implemented. Will be delivered with v1.0.

### Cloning from source
```bash
git clone https://github.com/AadityaNair/ProjectNephos.git
pip install ./ProjectNephos
```

# Usage
Currently only manual usage is developed. More will be added as project goes on.

### Initialisation
Create all the relevant directories and perform OAuth with google drive  
```bash
nephos init
```

### Uploading files
```bash
nephos upload <filename>
```

### Searching
```bash
nephos search --name <name> --tags <tag1> <tag2> ... --do_and
```
Search for files with `<name>` and/or tags `<tag1> <tag2> ...`.
The and/or part will be decided by the `do_and` parameter. If specified, all parameters (name, tags) will be joined
by an AND i.e it will search for *"<name> AND <tag1> AND <tag2> ..."*  
If not, ANDs will be replaced by ORs.

Atleast one of `--name` and `--tags` is required.

### Tagging
```bash
nephos tag --for_name <name> --add_tags <tag1> <tag2> ...
```
This searches for all instances that contain `<name>` and for each of them, add the provided tags.

### Processing
```bash
nephos process <input_file> <output_file>
```
Converts the input file to output file. The formats are guessed by their extensions.

More information can be found for each sub-command by using the `--help` option after the sub-command 
# Configuration
All sorts of files Project Nephos creates can be found in `~/.nephos/`. Of particular use is the *config.ini*
file there. It contains all sorts of configuration information about nephos. A default one will be created for you
when you run `init`.

For more information you should look at the [wiki](https://github.com/AadityaNair/ProjectNephos/wiki).It will be updated frequently.