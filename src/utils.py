from re import match
from os import system
from argparse import ArgumentParser

from git_utils import get_diff, get_files_modify_info


def parse_arguments():
    parser = ArgumentParser(description='Create information of significantly modified files by you, depends on git')
    parser.add_argument('git_paths', nargs='+')
    parser.add_argument('-d', '--destination', help='Where to generate files', type=str, default='.')
    parser.add_argument('-a', '--author', help='Find changes made by provided author', type=str)
    parser.add_argument('-c', '--skip-cmakes', help='CMakeList.txt files will be skipped', action='store_true')
    parser.add_argument('-s', '--skip-small', help='Files with less added lines than provided value will be skipped', type=int)
    return parser.parse_args()


def is_string_important(line):
    is_important = True
    if not line:
        is_important = False
    if line.isspace():
        is_important = False
    if match('^[({[<>l\])};]+$', line):
        is_important = False
    if 'namespace' in line and 'using' not in line:
        is_important = False
    return is_important


def get_files_except_cmakes(files):
    product = []
    for file in files:
        if not file.is_cmake_file():
            product.append(file)
    return product


def get_files_except_moved(files):
    deleted_files = []
    added_files = []
    product = []
    for file in files:
        if file.is_deleted():
            deleted_files.append(file)
        if file.is_added():
            added_files.append(file)
        if file.is_modified():
            product.append(file)
    if not deleted_files:
        return files

    for added in added_files:
        for deleted in deleted_files:
            if not deleted.is_moved(added) and added not in product:
                product.append(added)
    return product


def get_files_contains_enough_changes(files, satisfy_lines_amount):
    satisfied_files = []
    for file in files:
        if file.has_satisfied_changes(satisfy_lines_amount):
            satisfied_files.append(file)

    return satisfied_files


def get_added_lines_amount(git_path, merge_sha, file_name):
    infos = get_files_modify_info(git_path, merge_sha)
    for info in infos:
        if info.split()[2] == file_name:
            return info.split()[0]


def get_removed_lines_amount(git_path, merge_sha, file_name):
    infos = get_files_modify_info(git_path, merge_sha)
    for info in infos:
        if info.split()[2] == file_name:
            return info.split()[1]


def generate_diffs(git_path, merge_shas, destination_path, project, month):
    for sha in merge_shas:
        with open('{}/{}/{}/{}/diff'.format(destination_path, month, project, sha), 'w') as file:
            file.write(get_diff(git_path, sha))


def create_directories_tree(merge_shas, destination_path, project, month):
    system('mkdir {}/{}/{}'.format(destination_path, month, project))
    for sha in merge_shas:
        system('mkdir {}/{}/{}/{}'.format(destination_path, month, project, sha))
