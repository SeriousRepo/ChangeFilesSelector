from os import popen


def retrieve_git_author_email(git_path):
    return popen('git --git-dir {} config user.email'.format(git_path)).read().splitlines()[0]


def get_merges_sha(git_path, author, start_date):
    if not author:
        author = retrieve_git_author_email(git_path)

    merges_sha = popen("git --git-dir {} log "
                       "--merges "
                       "--author='{}' "
                       "--since='{}' "
                       "--pretty=format:%h".format(git_path, author, start_date)
                       ).read().splitlines()
    return merges_sha


def get_split_of_diff_lines(git_path, merge_sha, file_name):
    added_lines = []
    removed_lines = []
    diff = popen('git --git-dir {0} diff '
                 '{1}^1:{2} {1}:{2}'.format(git_path,
                                            merge_sha,
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


def get_file_content(git_path, merge_sha, file_name):
    lines = popen("git --git-dir {} show "
                  "'{}:{}'".format(git_path, merge_sha, file_name)
                  ).read().splitlines()
    return lines


def get_name_status_of_diff(git_path, merge_sha):
    return popen("git --git-dir {0} diff "
                 "--name-status "
                 "'{1}'^1 '{1}'".format(git_path, merge_sha)
                 ).read().splitlines()


def get_file_status(git_path, merge_sha, file_name):
    diffs = popen("git --git-dir {0} diff "
                  "--name-status "
                  "'{1}'^1 '{1}'".format(git_path, merge_sha)
                  ).read().splitlines()
    for diff in diffs:
        if file_name == diff.split()[1]:
            return diff.split()[0]


def get_file_names_of_merge(git_path, merge_sha):
    names = []
    diffs = popen("git --git-dir {0} diff "
                  "--name-status "
                  "'{1}'^1 '{1}'".format(git_path, merge_sha)
                  ).read().splitlines()
    for diff in diffs:
        names.append(diff.split()[1])
    return names


def get_diff(git_path, merge_sha):
    diff = popen('git --git-dir {0} diff '
                 '{1}^1 {1}'.format(git_path,
                                    merge_sha,
                                    )
                 ).read()
    return diff


def get_files_modify_info(git_path, merge_sha):
    return popen("git --git-dir {0} diff "
                 "--numstat "
                 "'{1}'^1 '{1}'".format(git_path, merge_sha)
                 ).read().splitlines()


def get_file_in_revision(git_path, merge_sha, filename):
    return popen('git --git-dir {} show {}:{}'.format(git_path, merge_sha, filename)).read()
