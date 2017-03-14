import webserver
import mock
import json
import uuid
import game_config
from tests.common import GardenSimTest


class TestWebserver(GardenSimTest):

    def setUp(self):
        super(TestWebserver, self).setUp()
        webserver.app.config['TESTING'] = True
        self.app = webserver.app.test_client()
        self.game_config = game_config.get_config(True)
        self.password = 'testpassword'

    def get(self, path):
        return self.app.get(path)

    def post(self, path, data=None):
        if data is None:
            data = {}
        rv = self.app.post(path,
                           data=json.dumps(data),
                           headers={'Content-Type': 'application/json'})
        return json.loads(rv.data)

    def new_state(self):
        slug = 'TEST' + uuid.uuid4().hex
        return self.post('/game-state/' + slug,
                         {'password': self.password, 'newOrLoad': 'new'})['state']

    @mock.patch('db.get_leaderboard_data')
    def test_homepage(self, get_leaderboard_data):
        get_leaderboard_data.side_effect = [
            [('Player1', 1000, 10)],
        ]
        rv = self.app.get('/')
        self.assertIn('New Game', rv.data, "Can't see 'New Game' button on home screen")
        self.assertIn('Player1', rv.data, "Can't see leaderboard table on home screen")

    def test_buy_first_seed(self):
        state = self.new_state()
        slug = state['slug']
        first_seed = self.game_config['firstSeed']
        rv = self.post('/action/buy', {'slug': slug,
                                       'password': self.password,
                                       'recipe_id': first_seed})
        new_state = rv['state']
        self.assertEquals(new_state['seedCounts'][first_seed], 1, "Could not buy initial seed")

    def test_buy_until_broken(self):
        """ Buy a seed over and over until you can't buy any more. """
        state = self.new_state()
        slug = state['slug']
        first_seed = self.game_config['firstSeed']

        purchases = 100  # we should run out of money before buying 100 seeds
        while purchases > 0:
            response = self.post('/action/buy', {'slug': slug,
                                                 'password': self.password,
                                                 'recipe_id': first_seed})
            message = response['message']
            if not message.startswith('Bought a'):
                return
            purchases -= 1
        self.fail("Bought a lot of seeds without running out of money.")
