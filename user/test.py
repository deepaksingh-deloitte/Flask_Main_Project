import unittest
import requests

class TestAPI(unittest.TestCase):
    URL = 'http://127.0.0.1:5000/'
    TOKEN = ''

    

    expected_response_200 = {
        "id": 1,
        "public_id": "47756c8a-0dcc-4a21-a654-67275a43d7d1",
        "username": "deepak123"
    }

    expected_response_404 = {
    "message": "User not found"
    }

    def test_current_user_200(self):
        res = requests.post('http://127.0.0.1:5000/login', json={
            "username":"deepak123",
            "password": "123"
        })
        if res.ok:
            self.TOKEN = res.json()['tok']
        resp = requests.get(self.URL + 'currentuser', headers={"x-access-token":self.TOKEN})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 3)
        self.assertDictEqual(resp.json(), self.expected_response_200)
        print('test_get_one_card_200 completed!')

    def test_current_user_404(self):
        res = requests.post('http://127.0.0.1:5000/login', json={
            "username":"deepak12",
            "password": "123"
        })
        if res.ok:
            self.TOKEN = res.json()['tok']
        self.assertEqual(res.status_code, 404)
        self.assertDictEqual(res.json(), self.expected_response_404)
        print('test_current_user_404 completed!')

if __name__ == "__main__":
    tester = TestAPI()
    tester.test_current_user_200()
    tester.test_current_user_404()