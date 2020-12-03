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
:class:`apper.Fusion360CommandBase` and
:class:`apper.PaletteCommandBase` classes.
Each instance of these classes will be a new command in your add-in.


.. py:currentmodule:: apper
.. autoclass:: apper.FusionApp
   :members:


.. py:currentmodule:: apper
.. autoclass:: apper.Fusion360CommandBase
   :members:


.. py:currentmodule:: apper
.. autoclass:: apper.PaletteCommandBase
   :members:


Other Modules
==============

.. automodule:: apper.Fusion360AppEvents
   :members:


.. automodule:: apper.Fusion360Utilities
   :members:


.. automodule:: apper.Fusion360DebugUtilities
   :members:
