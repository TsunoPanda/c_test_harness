# Generic Compiler options
Compiler => 'g++',

HarnessOptions    => [
    '-MMD',  # Make dependency file
    '-Wformat=0',
],

# The source files to be compiled
HarnessSourceFiles => [
    './TestHarness/src/CppUTest/CommandLineArguments.cpp',
    './TestHarness/src/CppUTest/CommandLineTestRunner.cpp',
    './TestHarness/src/CppUTest/JUnitTestOutput.cpp',
    './TestHarness/src/CppUTest/MemoryLeakDetector.cpp',
    './TestHarness/src/CppUTest/MemoryLeakWarningPlugin.cpp',
    './TestHarness/src/CppUTest/SimpleMutex.cpp',
    './TestHarness/src/CppUTest/SimpleString.cpp',
    './TestHarness/src/CppUTest/TeamCityTestOutput.cpp',
    './TestHarness/src/CppUTest/TestFailure.cpp',
    './TestHarness/src/CppUTest/TestFilter.cpp',
    './TestHarness/src/CppUTest/TestHarness_c.cpp',
    './TestHarness/src/CppUTest/TestMemoryAllocator.cpp',
    './TestHarness/src/CppUTest/TestOutput.cpp',
    './TestHarness/src/CppUTest/TestPlugin.cpp',
    './TestHarness/src/CppUTest/TestRegistry.cpp',
    './TestHarness/src/CppUTest/TestResult.cpp',
    './TestHarness/src/CppUTest/TestTestingFixture.cpp',
    './TestHarness/src/CppUTest/Utest.cpp',
    './TestHarness/src/Platforms/gcc/UtestPlatform.cpp',
],

IncludePaths => [
    './TestHarness/include/CppUTest/',
    './TestHarness/include/',
],


