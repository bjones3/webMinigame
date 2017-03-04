import unittest, webserver


class TestConfig(unittest.TestCase):

    def test_config_data(self):
        seed_data = ['name', 'imageSmall', 'imageMedium', 'imageLarge',
                     'buyCost', 'sellCost', 'seedYield', 'cashYield', 'harvestTimeSeconds']
        self.assertTrue('seeds' in webserver.GAME_CONFIG)
        for seed in webserver.GAME_CONFIG['seeds']:
            for data in seed_data:
                self.assertTrue(data in webserver.GAME_CONFIG['seeds'][seed], "%s not in %s" % (data, webserver.GAME_CONFIG['seeds'][seed]))
        self.assertTrue('starting_resources' in webserver.GAME_CONFIG)
        self.assertTrue('cash' in webserver.GAME_CONFIG['starting_resources'])
