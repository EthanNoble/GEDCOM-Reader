# GEDCOM Reader

A reader and writer for the GEDCOM specifications 5.5.1 and 5.5.5. Links to download the official specifications from [https://www.gedcom.org/](https://www.gedcom.org/)
- [5.5.1](https://www.gedcom.org/specs/GEDCOM551.zip)
- [5.5.5](https://www.gedcom.org/specs/GEDCOM555.zip)

Since 5.5.1 is the widely used industry standard (Ancestry.com uses it for example), this project's long-term goal is to implement an all-encompassing parser that can handle GEDCOM files written in both specifications.

_Note that this project is a work in progress, so the full implementation of reading and writing functionalities are not present. A full list of implemented capabilities can be found in the [State of the Repo](#state-of-the-repo) section_

# Environment Setup for Contributing
Python Version `3.12.3`

Clone the repository

`git clone https://github.com/EthanNoble/GEDCOM-Reader.git`

Navigate to the cloned directory

`cd GEDCOM-Reader`

Create a virtual environemnt for easy package management

`python -m venv venv`

To activate the virtual environment during development

`source venv/bin/activate`

To deactive, run

`deactivate`

Make sure to activate the virtual environemnt and then install the dependencies from `requirements.txt`

`pip install -r requirements.txt`

Create a python file in the root project directory named anything, you can use `main.py`

`touch main.py`

In your new python file, add this code to run the parser on a GEDCOM file

```
from src.file import File
import src.enums as enums

gedcom_file = File('ABSOLUTE_PATH_TO_GEDCOM_FILE')
gedcom_file.jsonify(True, enums.JSONField.IND, enums.JSONField.FAM)
```

Run the script to execute the parser on your GEDCOM file

# Contributions

If you contribute to implementing a previously unimplemtented specification feature/requirement, please append the details of the change to the [State of the Repo](#state-of-the-repo) section following the format of the given example.

You MUST only reference page numbers from the 5.5.1 or 5.5.5 specifications from gedcom.org given in the [GEDCOM Reader](#gedcom-reader) section.

# Regression Testing
After implementing a spec feature, or editing an existing implemented feature, it would be ideal to have a suite of regression tests against known GEDCOM files to ensure that it does create unintended consequences. I would love someone to help me figure out how to do this :D

# State of the Repo

_If a specification requirement is not explicitely mentioned in this section, you may assume that it is not implemented yet (CONT and CONC tags, for example, are definitely not implemented... but can be easily implemented with a little effort). A full roadmap of all spec features and their implementation progress is still in the works_

A contribution to this list must begin with a line specifying exactly where in the specifications it was derived from. It must follow this regex pattern

`__(5\.5\.1|5\.5\.5)__: Chapter [1-9][0-9]* Section _.+_, Page [1-9][0-9]*`

And an example that follows this pattern (note the markdown stylings from the regex)

__5.5.5__: Chapter 1 Section _CONC & CONT_, Page 41
- Implemented the functionalities of the CONC and CONT tags early on in the parsing stage, so that we can build the logical line value before any other parsing is performed. This simplifies the process, ensuring that we don't have to handle these tags during later stages of parsing line values.
