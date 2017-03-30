import unittest
import webserver


class TestConfig(unittest.TestCase):

    def test_config_data(self):
        return
        seed_data = ['name', 'imageSmall', 'imageMedium', 'imageLarge',
                     'sellCost', 'yield', 'harvestTimeSeconds']
        self.assertTrue('seeds' in webserver.GAME_CONFIG)
        for seed in webserver.GAME_CONFIG['seeds']:
            for data in seed_data:
                self.assertTrue(data in webserver.GAME_CONFIG['seeds'][seed], "%s not in %s" % (data, webserver.GAME_CONFIG['seeds'][seed]))
        self.assertIn('starting_resources', webserver.GAME_CONFIG)
        self.assertIn('cash', webserver.GAME_CONFIG['starting_resources'])
        self.assertIn(webserver.GAME_CONFIG['firstSeed'], webserver.GAME_CONFIG['seeds'])

    def test_associative_table_load(self):
        for recipe in webserver.CONFIG.recipes.values():
            for resource_id in recipe['cost']:
                self.assertIn(resource_id, webserver.CONFIG.resources,
                              "Recipe %s uses unknown resource %s" % (recipe['id'], resource_id))
        for seed in webserver.CONFIG.seeds.values():
            for resource_id in seed['yield']:
                self.assertIn(resource_id, webserver.CONFIG.resources,
                              "Seed %s uses unknown resource %s" % (seed['id'], resource_id))
