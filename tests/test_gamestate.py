import uuid
from webserver import GameState
from tests.common import GardenSimTest


class TestGameState(GardenSimTest):
    def test_check_cash(self):
        slug = "TEST" + uuid.uuid4().hex
        gs = GameState.new(slug, 'pwd')
        gs.data['resources']['cash'] = 0
        gs.check_cash()
        self.assertGreater(gs.data['resources']['cash'], 0)
