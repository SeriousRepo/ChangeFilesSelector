from file import File
from utils import *

from datetime import datetime
import os
from argparse import ArgumentParser


def get_all_modified_files(commit_identifiers, git_path):
    files = []
    for identifier in commit_identifiers:
        files.extend(get_file_params(identifier, git_path))
    return files


def get_file_params(commit_identifier, git_path):
    files_params = []
    modify_infos = get_files_modify_info(git_path, commit_identifier)
    for info in modify_infos:
        files_params.append(info.split())

    statuses = get_files_statuses(commit_identifier, git_path)
    files = []
    for status in statuses:
        file = File(git_path, status[1], status[0], commit_identifier,
                    int(files_params[statuses.index(status)][0]), int(files_params[statuses.index(status)][1]))
        files.append(file)
    return files


parser = ArgumentParser(description='Create information of significantly modified files by you, depends on git')
parser.add_argument('destination_path')
parser.add_argument('author_name')
parser.add_argument('git_paths')
args = parser.parse_args()

destination_path = args.destination_path
author_name = args.author_name
git_paths = args.git_paths.split()

today = datetime.today()
month_name = today.strftime('%B')
first_date = datetime(today.year, today.month, 1)

os.system('mkdir {}/{}'.format(destination_path, month_name))
for git_path in git_paths:
    project_name = git_path.split('/')[-2]

    commit_ids = get_merges_ids(git_path, author_name, first_date)

    create_directories_tree(destination_path, month_name, project_name, commit_ids)

    files = get_all_modified_files(commit_ids, git_path)
    files = get_files_except_cmakes(files)
    files = get_files_except_moved(files)
    files = get_files_contains_enough_changes(files)
    print('\nfor {} project created information available in {}/{}/{}, included files:\n'
          .format(project_name, destination_path, month_name, project_name))
    for file in files:
        if file.is_added():
            append_added_file_to_diff(file.name, destination_path, month_name, project_name)
        else:
            append_modified_file_to_fidd(git_path, file.name, file.commit_identifier,
                                         destination_path, month_name, project_name)
    for file in files:
        os.system('echo \'{}\' > {}/{}/{}/{}/{}'
                  .format(get_file_in_revision(git_path, file.name, file.commit_identifier), destination_path,
                          month_name, project_name, file.commit_identifier, file.name.replace('/', '.'))
                  )
        print(file.name)
