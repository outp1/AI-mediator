import unittest
import bot

class TestBot(unittest.TestCase):
    def test_bot_token(self):
        self.assertIsNotNone(bot.BOT_TOKEN)

if __name__ == '__main__':
    unittest.main()
