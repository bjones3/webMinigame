import unittest, webserver


class TestWebserver(unittest.TestCase):

    def test_webserver(self):
        webserver.save_state('testSlug', webserver.GAME_CONFIG)
        load_test = webserver.load_state('testSlug')
        self.assertEqual(webserver.GAME_CONFIG, load_test)
