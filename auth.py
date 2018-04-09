from github import Github
import os


def get_github():
    USER = os.environ.get('GH_USER')
    SECRET = os.environ.get('GH_SECRET')

    if not USER or not SECRET:
        raise ValueError('Missing environment variable: GH_USER or GH_SECRET')

    return Github(USER, SECRET)
