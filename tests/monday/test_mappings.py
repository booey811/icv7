import pytest

from icv7.monday.base import BaseItem

"""
Need to write tests for the following (for each column value):
    result from _stage_change is correct result
    result from _stage_change can be submitted successfully, regardless of input (int, str, etc)
        [these tests (therefore the column value itself) should run so that incorrect inputs are handled within
        eric, before submission]
    following change commit, getting the moncli value is similar to the value submitted
    following change commit, getting the eric values are the same as the value submitted
"""


@pytest.fixture(scope='class')
def read_only_text_column_value(moncli_read_only_item):
    return moncli_read_only_item.get_column_value('text')


@pytest.fixture(scope='class')
def read_only_number_column_value(moncli_read_only_item):
    return moncli_read_only_item.get_column_value('numbers6')


class TestTextValue:

    def test_moncli_string_and_eric_string_match(self, eric_read_only_item, read_only_text_column_value):
        """Tests whether the text values of the read only test item are the same for the moncli object and
        the eric object"""
        moncli = read_only_text_column_value.text
        eric = eric_read_only_item.text.value
        assert moncli == eric

    def test_staged_changes_are_correct(self, eric_system_item):
        """Tests that staging a change for a text value will generate the correct _staged_changes dictionary"""
        new_value = 'test_staged_changes_are_correct VALUE'  # Arbitrary Test value to assert
        eric_system_item.text.value = new_value
        assert eric_system_item._staged_changes[eric_system_item.text.id] == new_value

    def test_committed_changes_match_new_eric_value(self, eric_system_item):
        """Tests that committing change to a standard value still allows retrieval of the eric value and that this
        value is the same as the test input"""
        test_value = 'test_staged_changes_are_correct VALUE'  # Arbitrary Test value to assert
        eric_system_item.text.value = test_value
        eric_system_item.commit()
        new_eric = BaseItem(eric_system_item.id)
        new_eric_value = new_eric.text.value
        assert new_eric_value == test_value

    def test_committed_changes_match_new_moncli_value(self, eric_system_item, clients_object):
        """Tests that committing change to a standard value still allows retrieval of the moncli value and that this
        value is the same as the test input"""
        test_value = 'test_staged_changes_are_correct VALUE'  # Arbitrary Test value to assert
        eric_system_item.text.value = test_value
        eric_system_item.commit()
        new_moncli_item = clients_object.monday.system.get_items(ids=[eric_system_item.id])[0]
        new_moncli_value = new_moncli_item.get_column_value(id=eric_system_item.text.id).text
        assert new_moncli_value == test_value

    @pytest.mark.parametrize('input', [
        ['random', 'list', 'entries'],          # Arbitrary test value
        {'dict': 'value'},                      # Arbitrary test value
        object                                  # Arbitrary test value
    ])
    def test_incorrect_input_raises_type_error(self, input, eric_system_item):
        """Tests that supplying the text column with a non int or str argument raises a type error"""
        with pytest.raises(ValueError) as e_info:
            print(input)
            eric_system_item.text.value = input


class TestNumberValue:

    def test_moncli_string_and_eric_string_match(self, eric_read_only_item, read_only_number_column_value):
        """Tests whether the number values of the read only test item are the same for the moncli object and
        the eric object"""
        moncli = read_only_number_column_value.number
        eric = eric_read_only_item.numbers.value
        assert moncli == eric

    def test_staged_changes_are_correct(self, eric_system_item):
        """Tests that staging a change for a text value will generate the correct _staged_changes dictionary"""
        new_value = 'test_staged_changes_are_correct VALUE'  # Arbitrary Test value to assert
        eric_system_item.text.value = new_value
        assert eric_system_item._staged_changes[eric_system_item.text.id] == new_value

    def test_committed_changes_match_new_eric_value(self, eric_system_item):
        """Tests that committing change to a standard value still allows retrieval of the eric value and that this
        value is the same as the test input"""
        test_value = 'test_staged_changes_are_correct VALUE'  # Arbitrary Test value to assert
        eric_system_item.text.value = test_value
        eric_system_item.commit()
        new_eric = BaseItem(eric_system_item.id)
        new_eric_value = new_eric.text.value
        assert new_eric_value == test_value

    def test_committed_changes_match_new_moncli_value(self, eric_system_item, clients_object):
        """Tests that committing change to a standard value still allows retrieval of the moncli value and that this
        value is the same as the test input"""
        test_value = 'test_staged_changes_are_correct VALUE'  # Arbitrary Test value to assert
        eric_system_item.text.value = test_value
        eric_system_item.commit()
        new_moncli_item = clients_object.monday.system.get_items(ids=[eric_system_item.id])[0]
        new_moncli_value = new_moncli_item.get_column_value(id=eric_system_item.text.id).text
        assert new_moncli_value == test_value

    @pytest.mark.parametrize('input', [
        ['random', 'list', 'entries'],          # Arbitrary test value
        {'dict': 'value'},                      # Arbitrary test value
        object                                  # Arbitrary test value
    ])
    def test_incorrect_input_raises_type_error(self, input, eric_system_item):
        """Tests that supplying the text column with a non int or str argument raises a type error"""
        with pytest.raises(ValueError) as e_info:
            print(input)
            eric_system_item.text.value = input
