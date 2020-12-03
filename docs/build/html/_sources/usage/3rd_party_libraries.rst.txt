===================
3rd Party Libraries
===================

There is an included helper class to use 3rd party libraries in a reasonably "safe" way.

Using 3rd Party Libraries with Fusion 360 Add-ins
-------------------------------------------------
Because Fusion 360 uses its own internal python runtime for the execution of add-ins there
are some unique challenges to using 3rd party libraries.

Especially when those libraries have dependancies on other additional libraries.  For example,
`Requests <https://requests.readthedocs.io/en/master/>`_ actually requires a number of other libraries.
These libraries are expecting each other to also be in the sys.path of the currently running python interpreter.
So it is not sufficient to simply install Requests to a project subdirectory and use a relative import,
since even though you have imported requests,
modules within requests will attempt to directly import other modules that requests installed as dependencies.

Here is one method that can be used to deal with these issues:
    1. Install the library to a subdirectory of your project such as 'lib'
    2. Temporarily add the location of that directory to your system path
    3. Import the required package
    4. Use the package
    5. Remove the location from the system path

The lib_import class
--------------------

There is a decorator class in :mod:`.Fusion360Utilities` called: :class:`.lib_import`
that will simplify this process for you.

.. py:currentmodule:: apper
.. autoclass:: lib_import
   :noindex:
   :members:
