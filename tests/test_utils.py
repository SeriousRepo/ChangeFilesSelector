from src.utils import *


class TestStringImportanceChecks(object):
    def test_when_empty_string(self):
        empty_string = ''
        assert is_string_important(empty_string) is False

    def test_when_only_non_important_chars_in_string(self):
        single_brace_string = '{'
        mixed_not_important_string = '{(<>[](){;});}'
        assert is_string_important(single_brace_string) is False
        assert is_string_important(mixed_not_important_string) is False

    def test_when_important_chars_in_string(self):
        string_starts_with_important_chars = 'int a{};'
        string_starts_with_non_important_chars = '[](){return 1;}'
        assert is_string_important(string_starts_with_important_chars) is True
        assert is_string_important(string_starts_with_non_important_chars) is True

    def test_when_whitespaces_in_string(self):
        all_whitespaces_string = '\t\n   \t\r'
        mixed_string = '\treturn 0;'
        assert is_string_important(all_whitespaces_string) is False
        assert is_string_important(mixed_string) is True

    def test_when_namespace_in_string(self):
        namespace_declaration_string = 'namespace std'
        using_declaration = 'using namespace std;'
        namespace_between_strings = '} // namespace std'

        assert is_string_important(namespace_declaration_string) is False
        assert is_string_important(using_declaration) is True
        assert is_string_important(namespace_between_strings) is False
