import unittest
from genia.llm_function.open_api_function import OpenApiFunction


class TestOpenAIFunction(unittest.TestCase):
    def setUp(self):
        self._swagger_client = OpenApiFunction()

    @unittest.skip("this test is integration, not unit. it fails if the pet doesnt exist in a public db")
    def test_pet_url(self):
        swagger_url = "https://petstore.swagger.io/v2/swagger.json"
        tag = "pet"
        function_name = "getPetById"
        parameters = {"petId": 1}
        response = self._swagger_client.invoke_api(swagger_url, tag, function_name, parameters)
        self.assertEqual(1, 1)


# https://api.github.com/repos/{owner}/{repo}/commits?since={since}
if __name__ == "__main__":
    unittest.main()
