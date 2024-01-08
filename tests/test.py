import unittest
from unittest import TestCase
import app


class FilesCase(TestCase):
    def setUp(self) -> None:
        app.create_app.testing = True

    def test_home(self):
        result = self.app.get("/")


if __name__ == "__main__":
    unittest.main()
