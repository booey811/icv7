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
        assert eric_system_item.staged_changes[eric_system_item.text.id] == new_value

    def test_committed_changes_match_new_eric_value(self, eric_system_item):
        """Tests that committing change to a standard value still allows retrieval of the eric value and that this
        value is the same as the test input"""
        test_value = 'test_staged_changes_are_correct VALUE'  # Arbitrary Test value to assert
        eric_system_item.text.value = test_value
        eric_system_item.commit()
        new_eric = BaseItem(eric_system_item.mon_id)
        new_eric_value = new_eric.text.value
        assert new_eric_value == test_value

    def test_committed_changes_match_new_moncli_value(self, eric_system_item, clients_object):
        """Tests that committing change to a standard value still allows retrieval of the moncli value and that this
        value is the same as the test input"""
        test_value = 'test_staged_changes_are_correct VALUE'  # Arbitrary Test value to assert
        eric_system_item.text.value = test_value
        eric_system_item.commit()
        new_moncli_item = clients_object.monday.system.get_items(ids=[eric_system_item.mon_id])[0]
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
        assert eric_system_item.staged_changes[eric_system_item.numbers.id] == str(new_value)

    def test_committed_changes_match_new_eric_value(self, eric_system_item, test_value):
        """Tests that committing change to a standard value still allows retrieval of the eric value and that this
        value is the same as the test input"""
        test_value = test_value  # Arbitrary Test value to assert
        eric_system_item.numbers.value = test_value
        eric_system_item.commit()
        new_eric = BaseItem(eric_system_item.mon_id)
        new_eric_value = new_eric.numbers.value
        assert new_eric_value == str(test_value)

    def test_committed_changes_match_new_moncli_value(self, test_value, eric_system_item, clients_object):
        """Tests that committing change to a standard value still allows retrieval of the moncli value and that this
        value is the same as the test input"""
        test_value = test_value  # Arbitrary Test value to assert
        eric_system_item.numbers.value = test_value
        eric_system_item.commit()
        new_moncli_item = clients_object.monday.system.get_items(ids=[eric_system_item.mon_id])[0]
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
        return moncli_read_only_item.get_column_value('status4')

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
        assert eric_system_item.staged_changes[eric_system_item.status.id]['index'] == test_index

    def test_staged_changes_are_correct_when_an_index_is_used_to_effect_change(
            self,
            eric_system_item,
            test_index
    ):
        """Tests that staging a change for a status value using an index will generate the correct
        _staged_changes dictionary"""
        eric_system_item.status.index = test_index
        assert eric_system_item.staged_changes[eric_system_item.status.id]['index'] == test_index

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
        new_eric = BaseItem(eric_system_item.mon_id)
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
        new_eric = BaseItem(eric_system_item.mon_id)
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
        new_moncli_item = clients_object.monday.system.get_items(ids=[eric_system_item.mon_id])[0]
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


class TestDropDownValue:

    @pytest.fixture(scope='class')
    def read_only_dropdown_column_value(self, moncli_read_only_item):
        return moncli_read_only_item.get_column_value('dropdown3')

    @pytest.fixture(scope='class')
    def test_id(self):
        return 1

    @pytest.fixture(scope='class')
    def test_label(self):
        return 'dropdownlabel1'

    def test_moncli_label_and_eric_label_match(
            self,
            eric_read_only_item,
            read_only_dropdown_column_value
    ):
        """Tests whether the label value of the read only test item is the same for the moncli object and
        the eric object"""
        moncli_labels = [item['name'] for item in read_only_dropdown_column_value.labels]
        assert moncli_labels == eric_read_only_item.dropdown.labels

    def test_moncli_ids_and_eric_ids_match(
            self,
            eric_read_only_item,
            read_only_dropdown_column_value
    ):
        """Tests whether the index value of the read only test item is the same for the moncli object and
        the eric object"""
        moncli_ids = [item['id'] for item in read_only_dropdown_column_value.labels]
        assert moncli_ids == eric_read_only_item.dropdown.ids

    def test_labels_convert_to_ids_correctly(
            self,
            eric_system_item
    ):
        """Tests that conversion from labels to ids is correct"""
        labels = ['dropdownlabel1', 'dropdownlabel2']
        ids = [1, 2]
        eric_ids = eric_system_item.dropdown._id_and_label_conversion(labels)

        assert ids == [int(item) for item in eric_ids]

    def test_list_input_is_processed_correctly(
            self,
            eric_read_only_item
    ):
        """Tests that the column can be supplied with a list in order to effect change"""
        eric_read_only_item.dropdown.add([3, 4])
        assert sorted(eric_read_only_item.dropdown.ids) == [1, 2, 3, 4]

    def test_string_input_is_processed_correctly(
            self,
            eric_read_only_item
    ):
        """Tests that the column can be supplied with a string in order to effect change"""
        eric_read_only_item.dropdown.add('dropdownlabel3')
        assert sorted(eric_read_only_item.dropdown.ids) == [1, 2, 3]

    def test_integer_input_is_processed_correctly(
            self,
            eric_read_only_item
    ):
        """Tests that the column can be supplied with a string in order to effect change"""
        eric_read_only_item.dropdown.add(3)
        assert sorted(eric_read_only_item.dropdown.ids) == [1, 2, 3]

    def test_add_method_adds_the_required_ids(
            self,
            eric_read_only_item
    ):
        """Tests the dropdown.add effects the correct change"""
        new_ids = [3, 4]  # IDs for 'dropdownlabel3' and 'dropdownlabel4'
        expected_ids = new_ids + eric_read_only_item.dropdown.ids
        new_labels = ['dropdownlabel3', 'dropdownlabel4']
        eric_read_only_item.dropdown.add(new_labels)
        assert sorted(eric_read_only_item.dropdown.ids) == sorted(expected_ids)

    def test_remove_method_removes_the_required_ids(
            self,
            eric_read_only_item
    ):
        """Tests the dropdown.remove effects the correct change"""
        to_remove = [2]
        expected = [1]
        eric_read_only_item.dropdown.remove(to_remove)
        assert eric_read_only_item.dropdown.ids == expected

    def test_replace_method_replaces_the_required_ids(
            self,
            eric_read_only_item
    ):
        """Tests the dropdown.remove effects the correct change"""
        to_replace = [3, 4]
        expected = [3, 4]
        eric_read_only_item.dropdown.replace(to_replace)
        assert eric_read_only_item.dropdown.ids == expected

    def test_committed_changes_through_label_match_new_eric_value(
            self,
            eric_system_item
    ):
        """Tests that committing change to a standard value still allows retrieval of the eric value and that this
        value is the same as the test input"""
        eric_system_item.dropdown.replace(['dropdownlabel1', 'dropdownlabel2'])  # Label corresponding to ID: 3
        eric_system_item.commit()
        new_eric = BaseItem(eric_system_item.mon_id)
        assert new_eric.dropdown.ids == [1, 2]

    def test_committed_changes_through_ids_match_new_eric_value(
            self,
            eric_system_item
    ):
        """Tests that committing change to a standard value still allows retrieval of the eric value and that this
        value is the same as the test input"""
        eric_system_item.dropdown.add(3)  # Label corresponding to ID: 3
        eric_system_item.commit()
        new_eric = BaseItem(eric_system_item.mon_id)
        assert new_eric.dropdown.ids == [1, 2, 3]


class TestLongTextValue:

    @pytest.fixture(scope='class')
    def read_only_long_text_column_value(self, moncli_read_only_item):
        return moncli_read_only_item.get_column_value('long_text')

    @pytest.fixture(scope='class')
    def test_value(self):
        return 'A VERY LONG TEXT VALUE, HELLO WORLD'  # Arbitrary test value

    def test_moncli_string_and_eric_string_match(self, eric_read_only_item, read_only_long_text_column_value):
        """Tests whether the text values of the read only test item are the same for the moncli object and
        the eric object"""
        moncli = read_only_long_text_column_value.text
        eric = eric_read_only_item.longtext.value
        assert moncli == eric

    def test_staged_changes_are_correct(self, eric_system_item, test_value):
        """Tests that staging a change for a text value will generate the correct staged_changes dictionary"""
        eric_system_item.longtext.value = test_value
        assert eric_system_item.staged_changes[eric_system_item.longtext.id] == test_value

    def test_committed_changes_match_new_eric_value(self, eric_system_item, test_value):
        """Tests that committing change to a standard value still allows retrieval of the eric value and that this
        value is the same as the test input"""
        eric_system_item.longtext.value = test_value
        eric_system_item.commit()
        new_eric = BaseItem(eric_system_item.mon_id)
        new_eric_value = new_eric.longtext.value
        assert new_eric_value == test_value

    def test_committed_changes_match_new_moncli_value(self, eric_system_item, clients_object, test_value):
        """Tests that committing change to a standard value still allows retrieval of the moncli value and that this
        value is the same as the test input"""
        eric_system_item.longtext.value = test_value
        eric_system_item.commit()
        new_moncli_item = clients_object.monday.system.get_items(ids=[eric_system_item.mon_id])[0]
        new_moncli_value = new_moncli_item.get_column_value(id=eric_system_item.longtext.id).text
        assert new_moncli_value == test_value

    @pytest.mark.parametrize('input_type', [
        ['random', 'list', 'entries'],  # Arbitrary test value
        {'dict': 'value'},  # Arbitrary test value
        object  # Arbitrary test value
    ])
    def test_incorrect_input_raises_type_error(self, input_type, eric_system_item):
        """Tests that supplying the text column with a non int or str argument raises a type error"""
        with pytest.raises(ValueError) as e_info:
            eric_system_item.longtext.value = input_type


class TestLinkValue:

    @pytest.fixture(scope='class')
    def read_only_link_column_value(self, moncli_read_only_item):
        return moncli_read_only_item.get_column_value('link7')

    def test_moncli_strings_and_eric_strings_match(self, eric_read_only_item, read_only_link_column_value):
        """Tests whether the text values of the read only test item are the same for the moncli object and
        the eric object"""
        moncli_text = read_only_link_column_value.url_text
        moncli_url = read_only_link_column_value.url
        assert moncli_text == eric_read_only_item.link.text
        assert moncli_url == eric_read_only_item.link.url

    def test_staged_changes_are_correct(self, eric_read_only_item):
        """Tests that staging a change for a text value will generate the correct _staged_changes dictionary"""
        url = 'www.random.com'
        text = 'random display text'
        eric_read_only_item.link.value = [url, text]
        assert eric_read_only_item.staged_changes[eric_read_only_item.link.id] == {'url': url, 'url_text': text}

    def test_committed_changes_match_new_eric_value(self, eric_system_item):
        """Tests that committing change to a standard value still allows retrieval of the eric value and that this
        value is the same as the test input"""
        # TODO Write this test (TestLinkValue.test_committed_changes_match_new_eric_value)
        pass

    def test_committed_changes_match_new_moncli_value(self, eric_system_item, clients_object):
        # TODO Write this test (TestLinkValue.test_committed_changes_match_new_moncli_value)
        pass

    @pytest.mark.parametrize('input_type', [
        ['random', 'list', 'entries'],  # Arbitrary test value
        {'dict': 'value'},  # Arbitrary test value
        object  # Arbitrary test value
    ])
    def test_incorrect_input_raises_type_error(self, input_type, eric_system_item):
        """Tests that supplying the text column with a non int or str argument raises a type error"""
        with pytest.raises(ValueError) as e_info:
            eric_system_item.link.value = input_type


class TestCheckBoxValue:

    @pytest.fixture()
    def read_only_checkbox_column_value(self, moncli_read_only_item):
        return moncli_read_only_item.get_column_value('checkbox')

    def test_moncli_value_and_eric_value_match(self, eric_read_only_item, read_only_checkbox_column_value):
        """Tests whether the text values of the read only test item are the same for the moncli object and
        the eric object"""
        eric = eric_read_only_item.checkbox.value
        monc = read_only_checkbox_column_value.checked
        if not monc:
            monc = False
        else:
            monc = True
        assert eric == monc


class TestHourValue:

    @pytest.fixture(scope='class')
    def read_only_hour_column_value(self, moncli_read_only_item):
        return moncli_read_only_item.get_column_value('hour')

    @pytest.fixture(scope='class')
    def dummy_hour(self):
        return 19

    @pytest.fixture(scope='class')
    def dummy_minute(self):
        return 55

    def test_moncli_strings_and_eric_strings_match(self, eric_read_only_item, read_only_hour_column_value):
        """Tests whether the text values of the read only test item are the same for the moncli object and
        the eric object"""
        moncli_hour = read_only_hour_column_value.hour
        eric_hour = eric_read_only_item.hour.hour
        assert moncli_hour == eric_hour

        moncli_min = read_only_hour_column_value.minute
        eric_min = eric_read_only_item.hour.minute
        assert moncli_min == eric_min

    def test_staged_changes_are_correct_after_hour_change(self, eric_system_item, dummy_hour):
        """Tests that staging a change for an hour value will generate the correct _staged_changes dictionary"""
        eric_system_item.hour.hour = dummy_hour
        assert eric_system_item.staged_changes[eric_system_item.hour.id]['hour'] == dummy_hour

    def test_staged_changes_are_correct_after_minute_change(self, eric_system_item, dummy_minute):
        """Tests that staging a change for an hour value will generate the correct _staged_changes dictionary"""
        eric_system_item.hour.minute = dummy_minute
        assert eric_system_item.staged_changes[eric_system_item.hour.id]['minute'] == dummy_minute

    def test_staged_changes_are_correct_after_value_change(self, eric_system_item, dummy_hour, dummy_minute):
        """Tests that staging a change for an hour value will generate the correct _staged_changes dictionary"""
        eric_system_item.hour.value = f'{dummy_hour}{dummy_minute}'
        assert eric_system_item.staged_changes[eric_system_item.hour.id] == {'hour': dummy_hour, 'minute': dummy_minute}

    def test_committed_changes_match_new_eric_value(self, eric_system_item, dummy_hour, dummy_minute):
        """Tests that committing change to a standard value still allows retrieval of the eric value and that this
        value is the same as the test input"""
        test_value = f'{dummy_hour}{dummy_minute}'  # Arbitrary Test value to assert (7:55 PM)
        eric_system_item.hour.value = test_value
        eric_system_item.commit()
        new_eric = BaseItem(eric_system_item.mon_id)
        new_eric_value = new_eric.hour.value
        assert new_eric_value.replace(':', '') == test_value  # eric value needs to have colon removed

    @pytest.mark.parametrize('input_type', [
        ['random', 'list', 'entries'],  # Arbitrary test value
        {'dict': 'value'},  # Arbitrary test value
        object  # Arbitrary test value
    ])
    def test_incorrect_input_raises_type_error(self, input_type, eric_system_item):
        """Tests that supplying the text column with a non int or str argument raises a type error"""
        with pytest.raises(ValueError) as e_info:
            eric_system_item.text.value = input_type
