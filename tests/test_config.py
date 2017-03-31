<<<<<<< HEAD
import unittest

=======
>>>>>>> master
import webserver
from tests.common import GardenSimTest


class TestConfig(GardenSimTest):

    def test_config_data(self):
        seed_data = ['name', 'imageSmall', 'imageMedium', 'imageLarge',
                     'sellCost', 'yield', 'harvestTimeSeconds']
        self.assertIsNotNone(webserver.CONFIG.seeds)
        for seed in webserver.CONFIG.seeds:
            for data in seed_data:
                self.assertTrue(data in webserver.CONFIG.seeds[seed], "%s not in %s" % (data, webserver.CONFIG.seeds[seed]))
        self.assertIn('starting_resources', webserver.CONFIG.general)
        self.assertIn(webserver.CONFIG.CASH_RESOURCE, webserver.CONFIG.general['starting_resources'])
        self.assertIn(webserver.CONFIG.general['firstRecipe'], webserver.CONFIG.recipes)

    def test_associative_table_load(self):
        for recipe in webserver.CONFIG.recipes.values():
            for resource_id in recipe['cost']:
                self.assertIn(resource_id, webserver.CONFIG.resources,
                              "Recipe %s uses unknown resource %s" % (recipe['id'], resource_id))
        for seed in webserver.CONFIG.seeds.values():
            for resource_id in seed['yield']:
                self.assertIn(resource_id, webserver.CONFIG.resources,
                              "Seed %s generates unknown resource %s" % (seed['id'], resource_id))

    def test_duplicate_names(self):
        def check_dupes(collection, col_name):
            all_names = [item['name'] for item in collection.values()]
            for name in set(all_names):
                all_names.remove(name)
            self.assertFalse(all_names,
                             "Duplicate %s names: %s" % (col_name, ', '.join(all_names)))

        check_dupes(webserver.CONFIG.resources, 'resource')
        check_dupes(webserver.CONFIG.seeds, 'seed')
        check_dupes(webserver.CONFIG.recipes, 'recipe')

    def test_all_recipes_have_cost(self):
        for recipe in webserver.CONFIG.recipes.values():
            self.assertIsNotNone(recipe.get('cost'),
                                 "Recipe %s has no resource cost" % recipe['id'])
            self.assertTrue(sum(recipe['cost'].values()))

    def test_all_seeds_have_yield(self):
        for seed in webserver.CONFIG.seeds.values():
            self.assertIsNotNone(seed.get('yield'),
                                 "Seed %s produces no resources" % seed['id'])
        self.assertTrue(sum(seed['yield'].values()))

    def test_all_resources_used_somewhere(self):
        all_resource_ids = set(webserver.CONFIG.resources)
        for recipe in webserver.CONFIG.recipes.values():
            all_resource_ids -= set(r for r in recipe['cost'] if recipe['cost'][r])
        self.assertFalse(all_resource_ids,
                         "Found resources that are never used: %s" % ','.join(all_resource_ids))

    def test_all_resources_generated(self):
        all_resource_ids = set(webserver.CONFIG.resources)
        for seed in webserver.CONFIG.seeds.values():
            all_resource_ids -= set(r for r in seed['yield'] if seed['yield'][r])
        self.assertFalse(all_resource_ids,
                         "Found resources that can't be created: %s" % ','.join(all_resource_ids))

    def test_every_seed_has_a_recipe(self):
        all_seed_ids = set(webserver.CONFIG.seeds)
        for recipe in webserver.CONFIG.recipes.values():
            all_seed_ids -= set([recipe['seedId']])
        self.assertFalse(all_seed_ids,
                         "Found seeds that have no recipes: %s" % ','.join(all_seed_ids))

    def test_all_recipes_completable(self):
        all_recipe_ids = set(webserver.CONFIG.recipes)
        gs = self.new_game_state()
        owned_resources = set(r for r in gs.data['resources'] if gs.get_resource_count(r))

        def add_seed(seed_id):
            for res in webserver.CONFIG.seeds[seed_id]['yield']:
                if webserver.CONFIG.seeds[seed_id]['yield'][res]:
                    owned_resources.add(res)

        for seed_id in gs.data['seedCounts']:
            if gs.get_seed_count(seed_id):
                add_seed(seed_id)

        unlocked_recipe = True
        while unlocked_recipe and all_recipe_ids:
            unlocked_recipe = False
            for recipe_id in all_recipe_ids:
                recipe = webserver.CONFIG.recipes[recipe_id]
                if not set(recipe['cost']).difference(owned_resources):
                    add_seed(recipe['seedId'])
                    unlocked_recipe = True
                    all_recipe_ids.remove(recipe_id)
                    break

        self.assertFalse(all_recipe_ids,
                         "Found recipes that can't be reached: %s" % ','.join(all_recipe_ids))
