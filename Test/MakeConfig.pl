# Generic Compiler options
Compiler => 'gcc',

Options    => [
    '-MMD',
],

# The source files to be compiled
SourceFiles => [
    './TestHarness/unity.c',
    './TestHarness/unity_fixture.c',
    './TestHarness/unity_memory.c',
],

IncludePaths => [
    './TestHarness/',
],


