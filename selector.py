from file import File
from git_utils import get_merges_sha, get_file_names_of_merge, get_file_in_revision
from utils import *

from datetime import datetime
from os import system


def get_all_modified_files(git_path, merge_shas):
    files = []
    for sha in merge_shas:
        files.extend(construct_files_of_merge(git_path, sha))
    return files


def construct_files_of_merge(git_path, merge_sha):
    names = get_file_names_of_merge(git_path, merge_sha)
    files = []
    for name in names:
        file = File(git_path, name, merge_sha)
        files.append(file)
    return files


args = parse_arguments()
destination_path = args.destination_path
author_name = args.author_name
git_paths = args.git_paths.split()

today = datetime.today()
month_name = today.strftime('%B')
first_date = datetime(today.year, today.month, 1)

system('mkdir {}/{}'.format(destination_path, month_name))
for git_path in git_paths:
    project_name = git_path.split('/')[-2]

    merges_sha = get_merges_sha(git_path, author_name, first_date)
    if not len(merges_sha):
        continue
    create_directories_tree(merges_sha, destination_path, project_name, month_name)

    files = get_all_modified_files(git_path, merges_sha)
    files = get_files_except_cmakes(files)
    files = get_files_except_moved(files)
    files = get_files_contains_enough_changes(files)

    print('\nfor {} project created information available in {}/{}/{}, included files:\n'
          .format(project_name, destination_path, month_name, project_name))
    for file in files:
        if file.is_added():
            append_added_file_to_diff(file.name, destination_path, project_name, month_name)
        else:
            append_modified_file_to_fidd(git_path, file.merge_sha, destination_path, project_name, month_name,
                                         file.name)
    for file in files:
        system('echo \'{}\' > {}/{}/{}/{}/{}'
               .format(get_file_in_revision(git_path, file.merge_sha, file.name), destination_path,
                       month_name, project_name, file.merge_sha, file.name.replace('/', '.'))
               )
        print(file.name)
