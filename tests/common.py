import unittest
import webserver
import mock


class MockDB(object):
    def __init__(self):
        self._data = {}

    def save_state(self, gs, slug):
        assert gs.data.get('password') is not None
        self._data[slug] = webserver.GameState(dict(gs.data))

    def load_state(self, slug, _):
        return self._data.get(slug)


class GardenSimTest(unittest.TestCase):

    def setUp(self):
        self._db = MockDB()

        patcher = mock.patch('webserver.GameState.load', self._db.load_state)
        self.addCleanup(patcher.stop)
        patcher.start()

        patcher = mock.patch.object(webserver.GameState, 'save',
                                    lambda a, b: self._db.save_state(a, b))
        self.addCleanup(patcher.stop)
        patcher.start()
