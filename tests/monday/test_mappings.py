import pytest

"""
Need to write tests for the following (for each column value):
    result from _stage_change is correct result
    result from _stage_change can be submitted successfully, regardless of input (int, str, etc)
        [these tests should run so that incorrect inputs are handled within eric, before submission]
    following change commit, getting the moncli value is similar to the value submitted
    following change commit, getting the eric values are the same as the value submitted
    
"""



@pytest.fixture(scope='class')
def text_column_value(moncli_read_only_item):
    return moncli_read_only_item.get_column_value('text')


@pytest.fixture()
def eric_text_value(eric_system_item):
    return eric_system_item.text


@pytest.mark.usefixtures('text_column_value')
@pytest.mark.usefixtures('eric_text_value')
class TestTextValue:

    def test_moncli_string_converts_correctly(self, eric_read_only_item, text_column_value):
        moncli = text_column_value.text
        eric = eric_read_only_item.text.value
        assert moncli == eric



