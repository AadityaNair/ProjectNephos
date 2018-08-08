# ProjectNephos
GSOC 2018 Project: Automate recording and uploading TV Channels to cloud.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Build Status](https://travis-ci.org/AadityaNair/ProjectNephos.svg?branch=master)](https://travis-ci.org/AadityaNair/ProjectNephos)
[![Coverage Status](https://coveralls.io/repos/github/AadityaNair/ProjectNephos/badge.svg?branch=py34-compatibility)](https://coveralls.io/github/AadityaNair/ProjectNephos?branch=py34-compatibility)
[![Requirements Status](https://requires.io/github/AadityaNair/ProjectNephos/requirements.svg?branch=master)](https://requires.io/github/AadityaNair/ProjectNephos/requirements/?branch=master)
[![CodeFactor](https://www.codefactor.io/repository/github/aadityanair/projectnephos/badge)](https://www.codefactor.io/repository/github/aadityanair/projectnephos)


# Introduction
One of the function of the RedHen Organisation is to record and archive Television streams they receive for future
research. Project Nephos is an effort by CCExtractor to automate the entire process. Archiving is done by compressing
and uploading to Google Drive. 
In addition to downloading and archiving, Project Nephos provides the following functionalities:
1. Tagging of videos.
2. Searching archived videos.
3. Sharing videos with other entities 

# Installation

### Using PyPI
Not yet implemented. Will be delivered with v1.0.

### Cloning from source
```bash
git clone https://github.com/AadityaNair/ProjectNephos.git
pip install ./ProjectNephos
```

# Usage
Below is how you would manually use Nephos to perform actions manually. This requires the config file to be present.
More information on the config file in the *Configuration* section.

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

### Permissions
Share uploaded videos with people based on the video tags.
```bash
nephos permission add --for_tags <tag1> <tag2> --share_with <email>
```
This command is persistent. This means that all future videos with the tag will also be shared.
To avoid this action pass `--not_persistent` to the command.

Note, The tags provided follow the OR semantics. i.e. in the above example, every file with the tag _tag1_
**OR** _tag2_ will be shared. 

To view all permissions,
```bash
nephos permission list
```

More information can be found for each sub-command by using the `--help` option after the sub-command 

# Automation
For the most part you want to just specify what to record and when leave Nephos at it. For that:

### Add channels
Add channel to specify where to download stuff from
```bash
nephos channel add --name 'CNN' --ip_string '1.2.3.4:5678'
```
Note that the `name` should be unique for each channel.

#### To view added channels.
```bash
nephos channel list
```

### Add job.
Specify when to download other post download options.
```bash
nephos job add --name <jobname> --channel <channel> --start <starttime> --duration <length> \
               --upload --convert_to <format> --tag <tag1> <tag2>
```
Following are mandatory arguments:<br>
`--name` is the name of the job. This should be unique for each job.<br>
`--channel` is the name of the associated channel. This channel should have already been added by the `channel add` subcommand.<br>
`--start` is the start time of the job written in the popular cron format. For more info on the format go [here](http://www.nncron.ru/help/EN/working/cron-format.htm). This was used as an reference.<br>
`--duration` is how long you want to record. This is provided in minutes.<br>

Rest are optional arguments: 
`--upload` instructs nephos to upload the file to Google Drive. This will most likely be the default case in the future versions. In such a case, this option will be removed. <br>
`--convert_to` makes so that the downloaded file is converted to the provided format before being uploaded.<br>
`--tag` tags the uploaded file with the provided tags.<br>

Note that `--tag` is dependent providing the `--upload` option. If it not provided `--tag` is a NOOP.

### TV Listings
Nephos also has a crude API that supports TV listings.
```bash
nephos schedule add --name <program_name> --channel <channel> --start <starttime> --duration <length> --tags <tag1> <tag2>
````
This syntax is pretty much exactly the same as for the `job add` above. The `tags` are associated with the program.
This allows for a separate syntax to add a job:
```bash
nephos job add --name <jobname> --program_tags <tag1> <tag2> .. \
               --upload --convert_to <format> --tag <tag1> <tag2>
```
This will find all programs with **any** of the provided tags and add them as jobs.

### Initialise Server
This starts the orchestration server which is responsible for the record -> process -> upload pipeline.
This will also create all the relevant directories and perform OAuth with google drive, if not done already.
```bash
nephos init
```
Currently, if a job is added after the server is started, it will not be picked up by the server. So, make sure you
add all the jobs before starting the server. This will be fixed in a later version.

# Configuration
All sorts of files Project Nephos creates can be found in `~/.nephos/`. Of particular use is the *config.ini*
file there. It contains all sorts of configuration information about nephos. A default one will be created for you
when you run `init`.

For more information you should look at the [wiki](https://github.com/AadityaNair/ProjectNephos/wiki).It will be updated frequently.
