from file import File
from git_utils import get_merges_sha, get_file_names_of_merge, get_file_in_revision
from utils import *

from datetime import date
from os import system

args = parse_arguments()

today = date.today()
month_name = date.today().strftime('%B')
start_date = date(today.year, today.month, 1)


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


def get_files(git_path, merges_sha):
    files = get_all_modified_files(git_path, merges_sha)
    files = get_files_except_moved(files)
    if args.skip_cmakes:
        files = get_files_except_cmakes(files)
    if args.skip_small:
        files = get_files_contains_enough_changes(files, args.skip_small)
    return files


system('mkdir {}/{}'.format(args.destination, month_name))
for git_path in args.git_paths:
    project_name = git_path.split('/')[-2]

    merges_sha = get_merges_sha(git_path, args.author, start_date)

    if not len(merges_sha):
        continue
    create_directories_tree(merges_sha, args.destination, project_name, month_name)
    generate_diffs(git_path, merges_sha, args.destination, project_name, month_name)

    files = get_files(git_path, merges_sha)

    print('\nfor {} project created information available in {}/{}/{}, included files:\n'
          .format(project_name, args.destination, month_name, project_name))
    for file in files:
        print(file.name)
        filename = '{}/{}/{}/{}/{}'.format(args.destination, month_name, project_name,
                                           file.merge_sha, file.name.replace('/', '.'))
        with open(filename, 'w') as f:
            f.write(get_file_in_revision(git_path, file.merge_sha, file.name))
