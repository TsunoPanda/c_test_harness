# c_test_harness
Test environment for c language. This environment uses Perl script. Users have to install strawberry perl.

## CodeDependency module

### Abstruction
#### Make All File Lists
At first this module will make all file lists from the input code files and include folder path.
The example folder struct is shown in below.
![Example Folder Structure](Images/ExampleFolderStruct.svg)

If this module was input an array of source codes containing

    ./src/code1.c,

    ./src/folder2/code2.c

and was input an array of include paths containing

    ./src/folder1,

    ./src/folder2

then it will make an array shown in below

    ./src/code1.c

    ./src/folder1/header1.h,

    ./src/folder1/header2.h,

    ./src/folder2/header3.h,

    ./src/folder2/code2.c,

    
#### Make Direct Relation Map Of The Files
Once the all file list was generated, this module would make the direct relation map. The direct relation map is a hash which has file paths as keys and has array of  file pathes included by the key file. For example, assume the codes has relation shown in below.
![Example Folder Structure](Images/IncludeRelation.svg)

After this process, we will have the hash structure like below

    './src/code1.c' -> [./src/folder1/header1.h, ./src/folder1/header2.h],

    './src/folder1/header1.h' -> [./folder2/header3.h],

    './src/folder1/header2.h' -> [],

    './src/folder2/code2.c' -> [./header3.h],

    './src/folder2/header3.h' -> [./folder1/header1.h]

#### Make Deep Relation Map Of the Files
