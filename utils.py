import re
import os


def is_important_string(line):
    is_important = True
    if line == '':
        is_important = False
    if re.match('^[({)};]+$', line):
        is_important = False
    return is_important


def get_merges_ids(git_path, author, start_date):
    commit_identifiers = os.popen("git --git-dir {} log "
                                  "--merges "
                                  "--author='{}' "
                                  "--since='{}' "
                                  "--pretty=format:%h".format(git_path, author, start_date)
                                  ).read().splitlines()
    return commit_identifiers


def get_diff_lines(git_path, commit_identifier, file_name):
    added_lines = []
    removed_lines = []
    diff = os.popen('git --git-dir {} diff '
                    '{}^1:{} {}:{}'.format(git_path,
                                           commit_identifier,
                                           file_name,
                                           commit_identifier,
                                           file_name
                                           )
                    ).read().splitlines()
    for line in diff:
        if line.startswith('+') and not line.startswith('++'):
            line = ''.join(line.split())
            added_lines.append(line[1:])
        if line.startswith('-') and not line.startswith('--'):
            line = ''.join(line.split())
            removed_lines.append(line[1:])

    return added_lines, removed_lines


def get_added_lines_amount(diff_lines):
    count = 0
    for line in diff_lines:
        if line.startswith('+'):
            count += 1
    return count


def get_removed_lines_amount(diff_lines):
    count = 0
    for line in diff_lines:
        if line.startswith('-'):
            count += 1
    return count


def get_file_content(file_name, commit_id, git_path):
    lines = os.popen("git --git-dir {} show "
                     "'{}:{}'".format(git_path, commit_id, file_name)
                     ).read().splitlines()
    return lines


def get_files_statuses(commit_identifier, git_path):
    statuses = []
    diffs = os.popen("git --git-dir {} diff "
                     "--name-status "
                     "'{}'^1 '{}'".format(git_path, commit_identifier, commit_identifier)
                     ).read().splitlines()
    for status in diffs:
        statuses.append(status.split())

    return statuses


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


def get_diff(git_path, file_name, commit_id):
    diff = os.popen('git --git-dir {0} diff '
                    '{1}^1:{2} {1}:{2}'.format(git_path,
                                               commit_id,
                                               file_name
                                               )
                    ).read()
    return diff


def get_files_contains_enough_changes(files):
    satisfied_files = []
    for file in files:
        if file.has_satisfied_changes():
            satisfied_files.append(file)

    return satisfied_files


def get_files_modify_info(git_path, commit_id):
    return os.popen("git --git-dir {0} diff "
                    "--numstat "
                    "'{1}'^1 '{1}'".format(git_path, commit_id)
                    ).read().splitlines()


def create_directories_tree(path, month, project, commit_ids):
    os.system('mkdir {}/{}/{}'.format(path, month, project))
    for idx in commit_ids:
        os.system('mkdir {}/{}/{}/{}'.format(path, month, project, idx))


def get_file_in_revision(git_path, filename, revision):
    return os.popen('git --git-dir {} show {}:{}'.format(git_path, revision, filename)).read()


def append_added_file_to_diff(file_name, destination, month, project_name):
    os.system('echo \'\n----------------------------------------------------------------\' >> {}/{}/{}/diff'
              .format(destination, month, project_name))
    os.system("echo \'Added new file - {}\' >> {}/{}/{}/diff"
              .format(file_name, destination, month, project_name))
    os.system('echo \'----------------------------------------------------------------\n\' >> {}/{}/{}/diff'
              .format(destination, month, project_name))


def append_modified_file_to_fidd(git_path, file_name, commit_id, destination, month, project_name):
    os.system("echo \'{}\' >> {}/{}/{}/diff"
              .format(get_diff(git_path, file_name, commit_id), destination, month, project_name))