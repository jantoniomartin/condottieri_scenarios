from django.test import TestCase
from unittest import mock

from condottieri_scenarios.graphics import *

class GraphicsTestCase(TestCase):

    @mock.patch('os.makedirs')
    def test_ensure_dir(self, mock_makedirs):
        mock_makedirs.return_value = None
        self.assertIsNone(ensure_dir(''))
