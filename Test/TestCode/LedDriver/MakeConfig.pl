# Compiler options
Options    => [
    '-Wall',
    '-O2',
],

# The source files to be compiled
SourceFiles => [
    '../ProductCode/LedDriver/LedDriver.c',
    './TestCode/LedDriver/LedDriverTest.c',
    './TestCode/LedDriver/LedDriverTestRunner.c',
],

IncludePaths => [
    '../ProductCode/LedDriver/',
],


