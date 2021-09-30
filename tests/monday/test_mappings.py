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


class TestTextValue:

    @pytest.fixture(scope='class')
    def read_only_text_column_value(self, moncli_read_only_item):
        return moncli_read_only_item.get_column_value('text')

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

    @pytest.mark.parametrize('input_type', [
        ['random', 'list', 'entries'],  # Arbitrary test value
        {'dict': 'value'},  # Arbitrary test value
        object  # Arbitrary test value
    ])
    def test_incorrect_input_raises_type_error(self, input_type, eric_system_item):
        """Tests that supplying the text column with a non int or str argument raises a type error"""
        with pytest.raises(ValueError) as e_info:
            print(input_type)
            eric_system_item.text.value = input_type


class TestNumberValue:

    @pytest.fixture(scope='class')
    def read_only_number_column_value(self, moncli_read_only_item):
        return moncli_read_only_item.get_column_value('numbers6')

    @pytest.fixture(scope='class')
    def test_value(self):
        return float(93610468310.9257)

    def test_moncli_string_and_eric_string_match(self, eric_read_only_item, read_only_number_column_value):
        """Tests whether the number values of the read only test item are the same for the moncli object and
        the eric object"""
        moncli = str(read_only_number_column_value.number)
        eric = eric_read_only_item.numbers.value
        assert moncli == eric

    def test_staged_changes_are_correct(self, eric_system_item, test_value):
        """Tests that staging a change for a number value will generate the correct _staged_changes dictionary"""
        new_value = test_value  # Arbitrary Test value to assert
        eric_system_item.numbers.value = new_value
        assert eric_system_item._staged_changes[eric_system_item.numbers.id] == str(new_value)

    def test_committed_changes_match_new_eric_value(self, eric_system_item, test_value):
        """Tests that committing change to a standard value still allows retrieval of the eric value and that this
        value is the same as the test input"""
        test_value = test_value  # Arbitrary Test value to assert
        eric_system_item.numbers.value = test_value
        eric_system_item.commit()
        new_eric = BaseItem(eric_system_item.id)
        new_eric_value = new_eric.numbers.value
        assert new_eric_value == str(test_value)

    def test_committed_changes_match_new_moncli_value(self, test_value, eric_system_item, clients_object):
        """Tests that committing change to a standard value still allows retrieval of the moncli value and that this
        value is the same as the test input"""
        test_value = test_value  # Arbitrary Test value to assert
        eric_system_item.numbers.value = test_value
        eric_system_item.commit()
        new_moncli_item = clients_object.monday.system.get_items(ids=[eric_system_item.id])[0]
        new_moncli_value = str(new_moncli_item.get_column_value(id=eric_system_item.numbers.id).text)
        assert new_moncli_value == str(test_value)

    @pytest.mark.parametrize('input_type', [
        ['random', 'list', 'entries'],  # Arbitrary test value
        {'dict': 'value'},  # Arbitrary test value
        object  # Arbitrary test value
    ])
    def test_incorrect_input_raises_type_error(self, input_type, eric_system_item):
        """Tests that supplying the number column with a non int or str argument raises a type error"""
        with pytest.raises(ValueError) as e_info:
            print(input_type)
            eric_system_item.text.value = input_type


class TestStatusValue:

    @pytest.fixture(scope='class')
    def read_only_status_column_value(self, moncli_read_only_item):
        return moncli_read_only_item.get_column_value('status')

    @pytest.fixture(scope='class')
    def test_index(self):
        return 0

    @pytest.fixture(scope='class')
    def test_label(self):
        return 'Test Label'

    def test_moncli_label_and_eric_label_match(
            self,
            eric_read_only_item,
            read_only_status_column_value
    ):
        """Tests whether the label value of the read only test item is the same for the moncli object and
        the eric object"""
        assert read_only_status_column_value.label == eric_read_only_item.status.label

    def test_moncli_index_and_eric_index_match(
            self,
            eric_read_only_item,
            read_only_status_column_value
    ):
        """Tests whether the index value of the read only test item is the same for the moncli object and
        the eric object"""
        assert read_only_status_column_value.index == int(eric_read_only_item.status.index)

    def test_staged_changes_are_correct_when_a_label_is_used_to_effect_change(
            self,
            eric_system_item,
            test_label,
            test_index
    ):
        """Tests that staging a change for a status value using a label will generate the correct
        _staged_changes dictionary"""
        eric_system_item.status.label = test_label
        assert eric_system_item._staged_changes[eric_system_item.status.id]['index'] == test_index

    def test_staged_changes_are_correct_when_an_index_is_used_to_effect_change(
            self,
            eric_system_item,
            test_index
    ):
        """Tests that staging a change for a status value using an index will generate the correct
        _staged_changes dictionary"""
        eric_system_item.status.index = test_index
        assert eric_system_item._staged_changes[eric_system_item.status.id]['index'] == test_index

    def test_committed_changes_through_label_match_new_eric_value(
            self,
            eric_system_item,
            test_label
    ):
        """Tests that committing change to a standard value still allows retrieval of the eric value and that this
        value is the same as the test input"""
        test_value = test_label  # Arbitrary Test value to assert
        eric_system_item.status.label = test_value
        eric_system_item.commit()
        new_eric = BaseItem(eric_system_item.id)
        new_eric_value = new_eric.status.label
        assert new_eric_value == test_value

    def test_committed_changes_through_index_match_new_eric_value(
            self,
            eric_system_item,
            test_index
    ):
        """Tests that committing change to a standard value still allows retrieval of the eric value and that this
        value is the same as the test input"""
        test_value = test_index  # Arbitrary Test value to assert
        eric_system_item.status.index = test_value
        eric_system_item.commit()
        new_eric = BaseItem(eric_system_item.id)
        new_eric_value = new_eric.status.index
        assert new_eric_value == test_value

    def test_committed_changes_match_new_moncli_value(
            self,
            eric_system_item,
            clients_object,
            test_label
    ):
        """Tests that committing change to a standard value still allows retrieval of the moncli value and that this
        value is the same as the test input"""
        eric_system_item.status.label = test_label
        eric_system_item.commit()
        new_moncli_item = clients_object.monday.system.get_items(ids=[eric_system_item.id])[0]
        new_moncli_value = str(new_moncli_item.get_column_value(id=eric_system_item.status.id).label)
        assert new_moncli_value == test_label

    @pytest.mark.parametrize('input_type', [
        ['random', 'list', 'entries'],  # Arbitrary test value mimicking a list
        {'dict': 'value'},  # Arbitrary test value mimicking a dictionary
        object  # Arbitrary test value mimicking an object
    ])
    def test_incorrect_input_raises_type_error(self, input_type, eric_system_item):
        """Tests that supplying the number column with a non int or str argument raises a type error"""
        with pytest.raises(ValueError) as e_info:
            eric_system_item.text.value = input_type

    @pytest.mark.parametrize('index_label', [
        'AN INCORRECT LABEL',  # Arbitrary test value mimicking an incorrect label
        8723568538653486,  # Arbitrary test value mimicking an incorrect index
    ])
    def test_incorrect_label_input_raises_value_error(self, eric_system_item, index_label):
        """Tests that attempting to change a ststus column with a label that does not exist raises a ValueError"""
        with pytest.raises(ValueError) as e_info:
            eric_system_item.status.value = index_label
