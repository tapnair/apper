===================
Developer Interface
===================

This part of the documentation covers all the interfaces of Requests. For
parts where Requests depends on external libraries, we document the most
important right here and provide links to the canonical documentation.

.. module:: apper

Core Apper Modules
==================

The core Apper functionality can be accessed by sub-classing these 3 classes.
Step one is to create an instance of the :class:`FusionApp <FusionApp>` object.
Step two is to add instances of
:class:`Fusion360CommandBase <Fusion360CommandBase>` and
:class:`PaletteCommandBase <PaletteCommandBase>` classes.
Each instance of these classes will be a new command in your add-in.


.. automodule:: FusionApp
   :members:


.. automodule:: Fusion360CommandBase
   :members:


.. automodule:: PaletteCommandBase
   :members:


Other Modules
==============


.. automodule:: Fusion360AppEvents
   :members:


.. automodule:: Fusion360Utilities
   :members:


.. automodule:: Fusion360DebugUtilities
   :members:
