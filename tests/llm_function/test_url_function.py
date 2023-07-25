import unittest

from genia.llm_function.url_function import URLFunction


class TestLLMFunctionFactory(unittest.TestCase):
    def setUp(self):
        self._url = URLFunction()

    def test_plain_url(self):
        GOOGLE = "https://google.com"
        config = {"template": GOOGLE}
        formatted = self._url.format_url(config)
        self.assertEqual(GOOGLE, formatted)

    def test_url(self):
        url = "https://google.com/q={query}"
        config = {"template": url}
        params = {"query": "my_query_goes_here"}
        formatted = self._url.format_url(config, params)
        self.assertEqual("https://google.com/q=my_query_goes_here", formatted)


# https://api.github.com/repos/{owner}/{repo}/commits?since={since}
if __name__ == "__main__":
    unittest.main()
