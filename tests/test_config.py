import unittest, webserver


class TestConfig(unittest.TestCase):

    def test_config_data(self):
        seed_data = ['name', 'imageSmall', 'imageMedium', 'imageLarge',
                     'buyCost', 'sellCost', 'harvestYield', 'harvestTimeSeconds']
        for seed in webserver.GAME_CONFIG['seeds']:
            for data in seed_data:
                self.assertTrue(data in webserver.GAME_CONFIG['seeds'][seed])
        self.assertTrue('startingCash' in webserver.GAME_CONFIG)
        self.assertTrue('seeds' in webserver.GAME_CONFIG)
