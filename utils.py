from re import match
from os import system
from argparse import ArgumentParser

from git_utils import get_diff, get_files_modify_info


def parse_arguments():
    parser = ArgumentParser(description='Create information of significantly modified files by you, depends on git')
    parser.add_argument('destination_path')
    parser.add_argument('author_name')
    parser.add_argument('git_paths')
    return parser.parse_args()


def is_string_important(line):
    is_important = True
    if line == '':
        is_important = False
    if match('^[({)};]+$', line):
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

    for deleted in deleted_files:
        for added in added_files:
            if not deleted.is_moved(added) and added not in product:
                product.append(added)

    return product


def get_files_contains_enough_changes(files):
    satisfied_files = []
    for file in files:
        if file.has_satisfied_changes():
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


def append_added_file_to_diff(file_name, destination_path, project_name, month):
    system('echo \'\n----------------------------------------------------------------\' >> {}/{}/{}/diff'
           .format(destination_path, month, project_name))
    system("echo \'Added new file - {}\' >> {}/{}/{}/diff"
           .format(file_name, destination_path, month, project_name))
    system('echo \'----------------------------------------------------------------\n\' >> {}/{}/{}/diff'
           .format(destination_path, month, project_name))


def append_modified_file_to_fidd(git_path, merge_sha, destination_path, project_name, month, file_name):
    system("echo \'{}\' >> {}/{}/{}/diff"
           .format(get_diff(git_path, merge_sha, file_name), destination_path, month, project_name))


def create_directories_tree(merge_shas, destination_path, project, month):
    system('mkdir {}/{}/{}'.format(destination_path, month, project))
    for idx in merge_shas:
        system('mkdir {}/{}/{}/{}'.format(destination_path, month, project, idx))
