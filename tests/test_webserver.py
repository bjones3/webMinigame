import unittest
import webserver
import mock
import json
import uuid
import game_config


class TestWebserver(unittest.TestCase):

    def setUp(self):
        webserver.app.config['TESTING'] = True
        self.app = webserver.app.test_client()
        self.game_config = game_config.get_config(True)

    def get(self, path):
        return self.app.get(path)

    def post(self, path, data=None):
        if data is None:
            data = {}
        rv = self.app.post(path,
                           data=json.dumps(data),
                           headers={'Content-Type': 'application/json'})
        return json.loads(rv.data)

    @mock.patch('webserver.load_state')
    @mock.patch('webserver.save_state')
    def new_state(self, save_state, load_state):
        load_state.side_effect = [None]
        slug = 'TEST' + uuid.uuid4().hex
        return self.post('/game-state/' + slug, {'password': 'pwd'})['state']

    @mock.patch('webserver.get_leaderboard_data')
    def test_homepage(self, get_leaderboard_data):
        get_leaderboard_data.side_effect = [
            [('Player1', 1000, 10)],
        ]
        rv = self.app.get('/')
        self.assertIn('New Game', rv.data, "Can't see 'New Game' button on home screen")
        self.assertIn('Player1', rv.data, "Can't see leaderboard table on home screen")

    @mock.patch('webserver.load_state')
    @mock.patch('webserver.save_state')
    def test_buy_first_seed(self, save_state, load_state):
        state = self.new_state()
        slug = state['slug']
        load_state.side_effect = [state]
        first_seed = self.game_config['firstSeed']
        rv = self.post('/action/buy', {'slug': slug,
                                       'password': state['password'],
                                       'seed': first_seed})
        new_state = rv['state']
        self.assertEquals(new_state['seedCounts'][first_seed], 1, "Could not buy initial seed")
