# Compiler options for product codes
ProductCodeOptions    => [
    '-MMD', # Make dependency file
    '-Wall',
    '-O2',
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

IncludePaths => [
    '../ProductCode/LedDriver/',
],


