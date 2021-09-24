import pytest

"""
Need to write tests for the following (for each column value):
    result from _stage_change is correct result
    result from _stage_change can be submitted successfully, regardless of input (int, str, etc)
        [these tests (therefore the column value itself) should run so that incorrect inputs are handled within
        eric, before submission]
    following change commit, getting the moncli value is similar to the value submitted
    following change commit, getting the eric values are the same as the value submitted
"""


class TestTextValue:

    @pytest.fixture(scope='class')
    def read_only_text_column_value(self, moncli_read_only_item):
        return moncli_read_only_item.get_column_value('text')

    @pytest.fixture(scope='class')
    def eric_text_value(self, eric_system_item):
        return eric_system_item.text

    def test_moncli_string_and_eric_string_match(self, eric_read_only_item, read_only_text_column_value):
        moncli = read_only_text_column_value.text
        eric = eric_read_only_item.text.value
        assert moncli == eric

    def test_staged_changes_are_correct(self, eric_system_item):
        new_value = 'test_staged_changes_are_correct VALUE'  # Test value to assert
        eric_system_item.text.value = new_value
        assert eric_system_item._staged_changes[eric_system_item.text.id] == new_value
