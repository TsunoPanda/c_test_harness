import unittest
import sys
import os
from py_module.make import MakeFile
from py_module.make import ExecutableStatus
import py_module.TimeStampComp

class BasicTest(unittest.TestCase):
    __BASE_DIR = './py_test/make_test'
    __EXT_TARGET = f'{__BASE_DIR}/test.exe'
    __EXT_COMPILER = 'gcc'
    __EXT_INCLUDE_PATH = [f'{__BASE_DIR}/math']
    __EXT_LINKER_OPTION = ['-MMD', '-Wall', '-O2']
    __EXT_COMPILE_OPTION = ['-MMD', '-Wall', '-O2']
    __EXT_OBJ_PATH = f'{__BASE_DIR}/Obj'
    __EXT_SOURCE_1 = f'{__BASE_DIR}/main.c'
    __EXT_SOURCE_2 = f'{__BASE_DIR}/math/math.c'

    @classmethod
    def setUpClass(cls):
        print('*****************************************')
        print('*********** Start Basic Test ************')
        print('*****************************************')
        cls.ext_instance = MakeFile(cls.__EXT_TARGET, cls.__EXT_COMPILER, cls.__EXT_INCLUDE_PATH, cls.__EXT_LINKER_OPTION)
        cls.ext_instance.add_src(cls.__EXT_SOURCE_1, cls.__EXT_COMPILE_OPTION, cls.__EXT_OBJ_PATH)
        cls.ext_instance.add_src(cls.__EXT_SOURCE_2, cls.__EXT_COMPILE_OPTION, cls.__EXT_OBJ_PATH)

    def test_basic_000_clear(self):
        print('\n\n*********** Start Clear Test ************\n')
        result = self.ext_instance.clear()

    def test_basic_001_make(self):
        print('\n\n*********** Start make Test ************\n')
        result = self.ext_instance.make()
        self.assertEqual(result, ExecutableStatus.EXECUTABLE_VALID)

    def test_basic_002_build(self):
        print('\n\n*********** Start build Test ************\n')
        result = self.ext_instance.build()
        self.assertEqual(result, ExecutableStatus.EXECUTABLE_VALID)

    def test_basic_003_make(self):
        print('\n\n*********** Start make after build Test ************\n')
        result = self.ext_instance.make()
        self.assertEqual(result, ExecutableStatus.EXECUTABLE_VALID)

class JsonReadTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('\n\n')
        print('*****************************************')
        print('*********** Start Json Test ************')
        print('*****************************************')
        cls.ext_instance = MakeFile()
        cls.ext_instance.load_json_makefile('./py_test/make_test/makefile.jsonc')

    def test_json_000_clear(self):
        print('\n\n*********** Start Clear Test ************\n')
        result = self.ext_instance.clear()

    def test_json_001_make(self):
        print('\n\n*********** Start Make Test ************\n')
        result = self.ext_instance.make()
        self.assertEqual(result, ExecutableStatus.EXECUTABLE_VALID)

    def test_json_002_build(self):
        print('\n\n*********** Start Build Test ************\n')
        result = self.ext_instance.build()
        self.assertEqual(result, ExecutableStatus.EXECUTABLE_VALID)

    def test_json_003_onefile_modified_make(self):
        print('\n\n****Start only make updated files test.****\n')
        py_module.TimeStampComp.ClearTimeStampDict()
        os.utime(path='./py_test/make_test/math/math.h', times=None)
        result = self.ext_instance.make()
        self.assertEqual(result, ExecutableStatus.EXECUTABLE_VALID)

if __name__ == '__main__':
    unittest.main()
