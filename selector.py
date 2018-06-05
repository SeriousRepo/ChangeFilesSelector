from file import File

from datetime import datetime
from difflib import SequenceMatcher
import os

cplane_tester_git_path = "~/5g/cplane-performance-tests/.git"
author_name = "<roman.fekete@nokia.com>"


def get_merges_ids(git_path, author, start_date):
    commit_identifiers = os.popen("git --git-dir {} log "
                                  "--merges "
                                  "--author='{}' "
                                  "--since='{}' "
                                  "--pretty=format:%h".format(git_path, author, start_date)
                                  ).read().splitlines()
    return commit_identifiers


def get_file_params(commit_identifier, git_path):
    files_params = []
    diffs = os.popen("git --git-dir {} diff "
                     "--numstat "
                     "'{}'^1 '{}'".format(git_path, commit_identifier, commit_identifier)
                     ).read().splitlines()
    for diff in diffs:
        files_params.append(diff.split())
    diffs = get_files_statuses(commit_identifier, git_path)
    for index in range(0, len(files_params)):
        files_params[index].append(diffs[index])


    files = []

    for file_params in files_params:
        file = File
        file.added_lines_amount = file_params[0]
        file.removed_lines_amount = file_params[1]
        file.name = file_params[2]
        file.commit_identifier = commit_identifier
        files.append(file)

    return files


def get_files_statuses(commit_identifier, git_path):
    statuses = []
    diffs = os.popen("git --git-dir {} diff "
                     "--name-status "
                     "'{}'^1 '{}'".format(git_path, commit_identifier, commit_identifier)
                     ).read().splitlines()
    for status in diffs:
        statuses.append(status[0])

    return statuses





def has_same_deleted_as_added_lines(file):
    return int(file[0]) > 7 and int(file[0]) == int(file[1])


def has_suitable_deleted_file_to_added_file(file1, file2):
    return int(file1[1]) == int(file2[0]) and int(file1[0]) == int(file2[1])


def get_file_statistics(commit_identifiers, git_path):
    files = []
    for identifier in commit_identifiers:
        files.extend(get_file_params(identifier, git_path))
    return files


def get_significantly_modificate_files(files):
    file_names = []
    deleted_files = []
    added_or_moved_files = []
    added_files = []
    probably_moved_files = []
    diffs = []
    for file_stat in files:
        if file_stat[3] == 'M' and has_enough_changes(file_stat):
            file_names.append(file_stat[2])

        if file_stat[3] == 'M' and has_same_deleted_as_added_lines(file_stat):
            diffs.append(os.popen("git --git-dir {} diff "
                                 "{}^1:{} {}:{}".format(cplane_tester_git_path,
                                                        file_stat[4],
                                                        file_stat[2],
                                                        file_stat[4],
                                                        file_stat[2]
                                                        )
                                 ).read().splitlines()
                        )

        if file_stat[3] == 'A' and has_enough_changes(file_stat):
            added_or_moved_files.append(file_stat)

        if file_stat[3] == 'D':
            deleted_files.append(file_stat)

    files_additions = []
    files_deletions = []
    for diff in diffs:
        added_lines = []
        removed_lines = []
        for line in diff:
            if line.startswith("+") and not line.startswith("++"):
                added_lines.append(line)

            elif line.startswith("-") and not line.startswith("--"):
                removed_lines.append(line)
        files_additions.append(added_lines)
        files_deletions.append(removed_lines)

    for file_index in range(0, len(files_additions)):
        satisfy_additions_counter = 0
        for change_index in range(0, len(files_additions[file_index])):
            s = SequenceMatcher(None, files_deletions[file_index][change_index][1:], files_additions[file_index][change_index])
            if s.ratio < .5:
                satisfy_additions_counter += 1
        if satisfy_additions_counter > 7:
            file_names.append(files_stats[2])

    print(file_names)


    #for added_file in added_or_moved_files:
    #    for deleted_file in deleted_files:
    #        if has_suitable_deleted_file_to_added_file(added_file, deleted_file):
    #            probably_moved_files.append(added_file)
    #        elif len(added_files) and added_files[len(added_files) - 1] != added_file:
    #            added_files.append(added_file[2])

    #file_names.extend(added_files)
    #return


today = datetime.today()
first_date = datetime(today.year, today.month, 1)

indexes = get_merges_ids(cplane_tester_git_path, author_name, first_date)

#os.system("mkdir ~/5g/taxbreak_reports/june")

files_stats = get_file_statistics(indexes, cplane_tester_git_path)

#get_significantly_modificate_files(files_stats)


#cd ~/5g/cplane_performance_tests
#git log --merges --author='<roman.fekete@nokia.com>' --since=$first_day --pretty=oneline > merges

#rm ~/5g/taxbreak_reports/wotan_merges

