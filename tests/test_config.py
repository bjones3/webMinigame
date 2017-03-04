import unittest
import webserver


class TestConfig(unittest.TestCase):

    def test_config_data(self):
        seed_data = ['name', 'imageSmall', 'imageMedium', 'imageLarge',
                     'buyCost', 'sellCost', 'seedYield', 'cashYield', 'harvestTimeSeconds']
        self.assertTrue('seeds' in webserver.GAME_CONFIG)
        for seed in webserver.GAME_CONFIG['seeds']:
            for data in seed_data:
                self.assertTrue(data in webserver.GAME_CONFIG['seeds'][seed], "%s not in %s" % (data, webserver.GAME_CONFIG['seeds'][seed]))
        self.assertIn('starting_resources', webserver.GAME_CONFIG)
        self.assertIn('cash', webserver.GAME_CONFIG['starting_resources'])
        self.assertIn(webserver.GAME_CONFIG['firstSeed'], webserver.GAME_CONFIG['seeds'])
