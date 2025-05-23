import os
import threading
import unittest
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

import requests


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Многопоточный HTTP-сервер"""


class ServerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.makedirs("static", exist_ok=True)
        with open("static/aboba.txt", "w") as f:
            f.write("test content")
        cls.server = ThreadedHTTPServer(("localhost", 8080), SimpleHTTPRequestHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()
        if os.path.exists("static/aboba.txt"):
            os.remove("static/aboba.txt")
        if os.path.exists("static/aboba2.txt"):
            os.remove("static/aboba2.txt")

    def test_keepalive(self):
        """тест для keep-alive соединения"""
        session = requests.Session()
        client1 = session.get("http://localhost:8080")
        client2 = session.get("http://localhost:8080")
        self.assertEqual(client1.status_code, 200)
        self.assertEqual(client2.status_code, 200)

    def test_static_files(self):
        """тест доступа к статическим файлам"""
        with open("static/aboba.txt") as f:
            content = f.read()
        self.assertEqual(content, "test content")

    def test_static_file_processing(self):
        """тест обслуживания статических запросов"""
        response = requests.get("http://localhost:8080/static/aboba.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "test content")

    def test_error404(self):
        """тест обработки ошибки 404"""
        response = requests.get("http://localhost:8080/hernya")
        self.assertEqual(response.status_code, 404)

    def test_cache_invalidation(self):
        """тест кэша дескрипторов открытых файлов"""
        test_file = "static/aboba2.txt"
        with open(test_file, "w") as f:
            f.write("First version")
        response1 = requests.get(f"http://localhost:8080/static/aboba2.txt")
        with open(test_file, "w") as f:
            f.write("Second version")
        response2 = requests.get(f"http://localhost:8080/static/aboba2.txt")
        self.assertEqual(response2.text, "Second version")


if __name__ == "__main__":
    unittest.main()
