from difflib import SequenceMatcher

from utils import is_important_string, get_diff_lines, get_file_content


class File:
    def __init__(self, git_path, name, status, commit_id, added_lines_amount, removed_lines_amount):
        self.name = name
        self.status_of_file_change = status
        self.commit_identifier = commit_id
        self.added_lines = []
        if self.is_modified():
            self.added_lines, self.removed_lines = get_diff_lines(git_path, self.commit_identifier, self.name)
        if self.is_added():
            self.added_lines = get_file_content(self.name, self.commit_identifier, git_path)
            self.removed_lines = []
        if self.is_deleted():
            self.added_lines = []
            self.removed_lines = get_file_content(self.name, self.commit_identifier + '^1', git_path)
        self.added_lines_amount = added_lines_amount
        self.removed_lines_amount = removed_lines_amount

    def is_modified(self):
        return self.status_of_file_change == 'M'

    def is_added(self):
        return self.status_of_file_change == 'A'

    def is_deleted(self):
        return self.status_of_file_change == 'D'

    def is_cmake_file(self):
        return self.name.endswith('CMakeLists.txt')

    def has_enough_changes(self):
        return (self.added_lines_amount - self.removed_lines_amount) > 7

    def has_same_deleted_as_added_lines(self):
        return self.added_lines_amount == self.removed_lines_amount

    def is_moved(self, file_to_compare):
        is_amount_of_added_equal_to_removed = self.added_lines_amount == file_to_compare.removed_lines_amount
        is_amount_of_removed_equal_to_added = self.removed_lines_amount == file_to_compare.added_lines_amount
        is_added_same_as_removed_lines = self.added_lines == file_to_compare.removed_lines
        is_removed_same_as_added_lines = self.removed_lines == file_to_compare.added_lines

        is_moved = is_amount_of_added_equal_to_removed and \
                   is_amount_of_removed_equal_to_added and \
                   is_added_same_as_removed_lines and \
                   is_removed_same_as_added_lines

        return is_moved

    def changes_amount_without_moved_lines(self, moved_lines_amount):
        return self.added_lines_amount - self.removed_lines_amount - 2 * moved_lines_amount

    def has_satisfied_changes(self):
        is_satisfied = False
        moved_lines_counter = 0
        important_added = []
        important_removed = []

        for added in self.added_lines:
            if is_important_string(added):
                important_added.append(added)
        for removed in self.removed_lines:
            if is_important_string(removed):
                important_removed.append(removed)

        for added in important_added:
            for removed in important_removed:
                s = SequenceMatcher(None, removed, added)
                if s.ratio() > 0.8:
                    moved_lines_counter += 1
                    break
        if len(important_added) - moved_lines_counter > 7:
            is_satisfied = True
        return is_satisfied
