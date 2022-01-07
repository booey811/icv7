import pytest

from zenpy.lib.api_objects import User

from application import HardLog
from application.zendesk import helper


class TestUserSearch:

    def test_supply_with_incorrect_eric_object_raises_hard_log(self, logger, temp_devtest_item):
        with pytest.raises(HardLog):
            helper.user_search(temp_devtest_item, logger)

    def test_user_search_returns_one_correct_user_when_searching_via_email(self, temp_main_item_for_zen):
        user = helper.user_search(temp_main_item_for_zen, temp_main_item_for_zen.logger)
        assert type(user) is User
        assert user.id == 1904191859233
