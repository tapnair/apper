===================
Developer Interface
===================

This part of the documentation covers all the interfaces of Apper.

.. py:module:: apper

Core Apper Modules
==================

The core Apper functionality can be accessed by sub-classing these 3 classes.
Step one is to create an instance of the :class:`.FusionApp` object.
Step two is to add instances of
:class:`.Fusion360CommandBase` and
:class:`.PaletteCommandBase` classes.
Each instance of these classes will be a new command in your add-in.


.. automodule:: FusionApp
.. py:currentmodule:: apper
.. autoclass:: FusionApp
   :members:


.. automodule:: Fusion360CommandBase
.. py:currentmodule:: apper
.. autoclass:: Fusion360CommandBase
   :members:


.. automodule:: PaletteCommandBase
.. py:currentmodule:: apper
.. autoclass:: PaletteCommandBase
   :members:


Other Modules
==============

.. automodule:: Fusion360AppEvents
   :members:


.. automodule:: Fusion360Utilities
   :members:


.. automodule:: Fusion360DebugUtilities
   :members:
