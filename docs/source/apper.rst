===================
Developer Interface
===================

This part of the documentation covers all the interfaces of Requests. For
parts where Requests depends on external libraries, we document the most
important right here and provide links to the canonical documentation.

.. module:: apper

Main Interface
==============

All of Requests' functionality can be accessed by these 7 methods.
They all return an instance of the :class:`FusionApp <FusionApp>` object.


Core Apper Modules
==================

apper.FusionApp module
----------------------

.. autoclass:: FusionApp
   :members:

apper.Fusion360CommandBase module
---------------------------------


.. autoclass:: Fusion360CommandBase
   :members:
   :undoc-members:
   :show-inheritance:

apper.PaletteCommandBase module
-------------------------------

.. autoclass:: PaletteCommandBase
   :members:
   :undoc-members:
   :show-inheritance:


Other Modules
==============

apper.Fusion360DebugUtilities module
------------------------------------

.. automodule:: Fusion360DebugUtilities
   :members:
   :undoc-members:
   :show-inheritance:

apper.Fusion360Utilities module
-------------------------------

.. automodule:: Fusion360Utilities
   :members:
   :undoc-members:
   :show-inheritance:
