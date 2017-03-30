import unittest
import db
import game
import mock
import uuid


class MockDB(object):
    def __init__(self):
        self._data = {}

    def save_state(self, slug, gs_data):
        assert gs_data.get('password') is not None
        self._data[slug] = game.GameState(dict(gs_data))

    def load_state(self, slug, _):
        return self._data.get(slug)


class GardenSimTest(unittest.TestCase):

    def setUp(self):
        self._db = MockDB()

        patcher = mock.patch('game.GameState.load', self._db.load_state)
        self.addCleanup(patcher.stop)
        patcher.start()

        patcher = mock.patch.object(db, 'save',
                                    lambda a, b: self._db.save_state(a, b))
        self.addCleanup(patcher.stop)
        patcher.start()

    def new_game_state(self):
        return game.GameState.new(uuid.uuid4().hex, 'pwd')
