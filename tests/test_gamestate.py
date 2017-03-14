import uuid

from werkzeug.exceptions import HTTPException
from game import GameState
from webserver import GAME_CONFIG
from tests.common import GardenSimTest


class TestGameState(GardenSimTest):
    def new_game_state(self):
        slug = "TEST" + uuid.uuid4().hex
        return GameState.new(slug, 'pwd')

    def test_check_cash(self):
        gs = self.new_game_state()
        gs.data['resources']['cash'] = 0
        gs.check_cash()
        self.assertGreater(gs.data['resources']['cash'], 0)

    def test_overharvest(self):
        slug = "TEST" + uuid.uuid4().hex
        gs = GameState.new(slug, 'pwd')
        seed_id = GAME_CONFIG['firstSeed']
        seed_data = GAME_CONFIG['seeds'][seed_id]
        gs.buy(seed_id)
        gs.sow(seed_id, 0, 0)
        plot = gs.get_plot(0, 0)
        plot['sowTime'] -= seed_data['harvestTimeSeconds'] * 1000 + 3000  # set plant time to long enough ago that we can harvest
        cash_before = gs.data['resources']['cash']
        gs.data['seedCounts'][seed_id] = GAME_CONFIG['max_seed_count']
        msg = gs.harvest(0, 0)
        # hacky way to extract number of seeds harvested
        seeds_generated = seed_data['yield']['seed']
        if 'Got ' in msg:
            seeds_generated += int(msg.split('Got ')[1].split()[0])
        cash_after = gs.data['resources']['cash']
        expected_cash_after = cash_before + seed_data['yield']['cash'] + seeds_generated * seed_data['sellCost']
        self.assertEqual(
            cash_after, expected_cash_after,
            "Did not get the correct amount of money when breaking seed limit.  Got $%s, expected $%s" % (cash_after, expected_cash_after)
        )

    def test_initial_crop_state(self):
        gs = self.new_game_state()
        for x in range(GAME_CONFIG['field_width']):
            for y in range(GAME_CONFIG['field_height']):
                self.assertFalse(gs.has_planted_crop(x, y))
                is_starting_plot = x < GAME_CONFIG['starting_field_width'] and y < GAME_CONFIG['starting_field_height']
                plot = gs.get_plot(x, y)
                self.assertEqual(is_starting_plot, plot is not None)

    def test_doing_illegal_things(self):
        """ This test doesn't ensure we do the right thing in these cases,
        just that the bad data causes some kind of exception
        """
        gs = self.new_game_state()
        # harvesting an empty plot
        self.assertRaises(HTTPException, gs.harvest, 0, 0)
        # harvesting a locked plot
        self.assertRaises(HTTPException, gs.harvest, 0, GAME_CONFIG['field_height'])
        # buy something that doesn't exist
        self.assertRaises(Exception, gs.buy, 'nonexistentrecipe')
        # sell something that doesn't exist
        self.assertRaises(Exception, gs.sell, 'nonexistentseed')
        # sell something we don't have
        self.assertRaises(HTTPException, gs.sell, GAME_CONFIG['firstSeed'])
        # sow something that doesn't exist
        self.assertRaises(Exception, gs.sow, 'nonexistentseed', 0, 0)
        # sow something we don't have
        self.assertRaises(HTTPException, gs.sow, GAME_CONFIG['firstSeed'], 0, 0)
        # sow something on a locked plot
        gs.buy(GAME_CONFIG['firstSeed'])
        self.assertRaises(HTTPException, gs.sow, GAME_CONFIG['firstSeed'], 0, GAME_CONFIG['field_height'])
