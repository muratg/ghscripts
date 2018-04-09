# Github helper scripts

## Installation

Note: you'll need a Python3.6.* installation.  

- `python -m venv venv`
- `source ./venv/bin/activate`
- `pip install -r requirements.txt`
- `export GH_USER=<your_user_name>`
- `export GH_SECRET=<your_secret_token>`

## Script: labelize.py

Applies the labels to the given repos. Description and color. Any existing label with the same name will be overwritten. 

- Usage: python labelize update data/repos.txt data/labels.txt 

