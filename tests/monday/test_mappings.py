import pytest


@pytest.fixture(scope='class')
def text_column_value(moncli_read_only_item):
    return moncli_read_only_item.get_column_value('text')


@pytest.mark.usefixtures('text_column_value')
class TestTextValue:

    def test_moncli_string_converts_correctly(self, eric_read_only_item, text_column_value):
        moncli = text_column_value.text
        eric = eric_read_only_item.text.value
        assert moncli == eric
