# Compiler options for product codes
ProductCodeOptions    => [
    '-MMD', # Make dependency file
    '-Wall',
    '-O0',  # No optimization for coverage measurement
    '-fprofile-arcs',
    '-ftest-coverage',
],

# The product source files to be compiled
ProductSourceFiles => [
    '../ProductCode/LedDriver/LedDriver.c',
],

# Compiler options for test codes
TestCodeOptions    => [
    '-MMD',  # Make dependency file
    '-Wall',
    '-O2',
],

# The test source files to be compiled
TestSourceFiles => [
    './TestCode/LedDriver/LedDriverTest.cpp',
    './TestCode/LedDriver/LedDriverTestRunner.cpp',
],

LinkerOption => [
    '-MMD', # Make dependency file
    '-Wall',
    '-O2',
    '-fprofile-arcs',
    '-ftest-coverage',
    '-pthread',
],

IncludePaths => [
    '../ProductCode/LedDriver/',
],


