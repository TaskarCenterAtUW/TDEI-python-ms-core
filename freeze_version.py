#!/usr/bin/env python

import os
import git
import json
import subprocess

from datetime import date


def get_last_version() -> str:
    """Return the version number of the last release."""
    json_string = (
        subprocess.run(
            ["gh", "release", "view", "--json", "tagName"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        .stdout.decode("utf8")
        .strip()
    )

    return json.loads(json_string)["tagName"]


def bump_patch_number(version_number: str) -> str:
    """Return a copy of `version_number` with the patch number incremented."""
    major, minor, patch = version_number.split(".")
    return f"{major}.{minor}.{int(patch) + 1}"


project_path = os.path.dirname(os.path.abspath(__file__))
version_file_path = '{}/version.py'.format(project_path)

repo = git.Repo(search_parent_directories=True)
sha = repo.head.object.hexsha

build_date = date.today().strftime('%Y-%m-%d')

try:
    last_version_number = get_last_version()
except subprocess.CalledProcessError as err:
    if err.stderr.decode("utf8").startswith("HTTP 404:"):
        # The project doesn't have any releases yet.
        version = "0.0.1"
    else:
        raise
else:
    version = bump_patch_number(last_version_number)

with open(version_file_path, 'w+') as version_file:
    version_file.write("version = '{}'\n".format(version))
    version_file.write("lastCommit = '{}'\n".format(sha))
    version_file.write("lastCommitShort = '{}'\n".format(
        repo.git.rev_parse(sha, short=1)))
    version_file.write("buildDate = '{}'\n".format(build_date))
