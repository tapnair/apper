
Adding apper to an existing project
=====================================

The best way to leverage apper in your addin project is to use `Git Submodules <https://git-scm.com/book/en/v2/Git-Tools-Submodules>`_

This way you can easily update to the latest version of apper
if it is enhanced

This assumes you already have your project in a `Git Repository <https://git-scm.com/docs/gittutorial>`_

Open a terminal and navigate to your addin's root directory:

You should be someplace like this:

>>> pwd
/Users/rainsbp/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/FusionApperSample

Now add the submodule to your project:

>>> git submodule add https://github.com/tapnair/apper

To check the status of apper from the project root directory:

>>> git submodule status

To update apper from the project root directory:

>>> git submodule update --remote
remote: Enumerating objects: 6, done.
remote: Counting objects: 100% (6/6), done.
remote: Compressing objects: 100% (3/3), done.
remote: Total 4 (delta 1), reused 4 (delta 1), pack-reused 0
Unpacking objects: 100% (4/4), done.
From https://github.com/tapnair/apper
   5035ffb..e951ad1  master     -> origin/master
Submodule path 'apper': checked out 'e951ad1030b6ed8fb60db3bac7e1098d64289833'


