#!/usr/bin/env python

import os
import git

from datetime import date


project_path = os.path.dirname(os.path.abspath(__file__))
version_file_path = '{}/version.py'.format(project_path)


year = date.today().year % 2000
month = date.today().month
day_of_month = date.today().day
version_format = '{}.{}.{}'.format(year, month, day_of_month)
repo = git.Repo(search_parent_directories=True)
sha = repo.head.object.hexsha

version = '%s.dev0+git.%s' % (version_format, repo.git.rev_parse(sha, short=1))
buildDate = date.today().strftime('%Y-%m-%d')
if not repo.head.is_detached and repo.active_branch.name == 'master':
    version = version_format

with open(version_file_path, 'w+') as version_file:
    version_file.write("version = '{}'\n".format(version))
    version_file.write("lastCommit = '{}'\n".format(sha))
    version_file.write("lastCommitShort = '{}'\n".format(
        repo.git.rev_parse(sha, short=1)))
    version_file.write("buildDate = '{}'\n".format(buildDate))
