import unittest
from py_module.jsonc import load

class BasicTest(unittest.TestCase):

    __EXT_JSONC_FILE = './py_test/jsonc_test/test.jsonc'

    def test_basic_000_read_jsonc(self):
        with open(self.__EXT_JSONC_FILE, 'r', encoding = 'UTF-8') as json_file:
            read_dict = load(json_file)
            self.assertEqual(read_dict['string'], 'This is a test')
            self.assertEqual(read_dict['number'], 3)
            self.assertEqual(read_dict['array'][0], 'Hello,')
            self.assertEqual(read_dict['array'][1], ' ')
            self.assertEqual(read_dict['array'][2], 'World')
            self.assertEqual(read_dict['array_of_dict'][0]['string'], 'hello')
            self.assertEqual(read_dict['array_of_dict'][0]['number'], 1)
            self.assertEqual(read_dict['array_of_dict'][1]['string'], 'Hello')
            self.assertEqual(read_dict['array_of_dict'][1]['number'], 2)
