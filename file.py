

class File:
    name = ''
    change_status = ''
    commit_identifier = ''
    added_lines = []
    added_lines_amount = 0
    removed_lines = []
    removed_lines_amount = 0

    def has_enough_changes(self):
        return self.added_lines_amount - self.removed_lines_amount > 7

    def is_suitable_with(self, file_to_compare):
        is_added_equal_to_removed = self.added_lines_amount == file_to_compare.removed_lines_count
        is_removed_equal_to_added = self.removed_lines_amount == file_to_compare.added_lines_count
        return is_added_equal_to_removed and is_removed_equal_to_added
