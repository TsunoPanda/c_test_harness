import unittest
from py_module.timestamp_comp import TimestampComp, CompResult

class BasicTest(unittest.TestCase):

    __EXT_FILE1 = './py_test/timestamp_comp_test/text1.txt'
    __EXT_FILE2 = './py_test/timestamp_comp_test/text2.txt'

    def test_basic_000_output_time_stamp_value(self):
        mtime = TimestampComp.get_timestamp_value(self.__EXT_FILE1)
        mtime2 = TimestampComp.get_timestamp_value(self.__EXT_FILE2)
        print(mtime)
        print(mtime2)

    def test_basic_001_file1_is_newer_than_file2(self):
        self.assertEqual(TimestampComp.compare_timestamps(self.__EXT_FILE1, self.__EXT_FILE2),
                            CompResult.FILE1_IS_NEWER)

    def test_basic_002_file1_is_the_newest(self):
        file_list = [self.__EXT_FILE1, self.__EXT_FILE2]
        self.assertTrue(TimestampComp.is_the_file_latest(self.__EXT_FILE1, file_list))

    def test_basic_003_file2_is_the_oldest(self):
        file_list = [self.__EXT_FILE1, self.__EXT_FILE2]
        self.assertTrue(TimestampComp.is_the_file_oldest(self.__EXT_FILE2, file_list))
