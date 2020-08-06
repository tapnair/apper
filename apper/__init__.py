"""
Apper Fusion 360 API Wrapper
=========================================================
Apper a simple wrapper for the Fusion 360 API,
written in Python, for human beings.

Full documentation is at <https://apper.readthedocs.io>.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 by Patrick Rainsberry.
:license: Apache 2.0, see LICENSE for more details.

"""
import sys

submodule_names = [
    'FusionApp',
    'Fusion360AppEvents',
    'Fusion360CommandBase',
    'PaletteCommandBase',
    'Fusion360Utilities',
    'Fusion360DebugUtilities',
    ]
for submodule_name in submodule_names:
    if sys.modules.get(''.join(['apper.', submodule_name]), False):
        del sys.modules['apper.' + submodule_name]

try:
    from .FusionApp import FusionApp
    from .Fusion360AppEvents import Fusion360CustomEvent
    from .Fusion360AppEvents import Fusion360CustomThread
    from .Fusion360AppEvents import Fusion360NewThread
    from .Fusion360AppEvents import Fusion360DocumentEvent
    from .Fusion360AppEvents import Fusion360WorkspaceEvent
    from .Fusion360AppEvents import Fusion360WebRequestEvent
    from .Fusion360AppEvents import Fusion360CommandEvent
    from .Fusion360AppEvents import Fusion360ActiveSelectionEvent
    from .Fusion360CommandBase import Fusion360CommandBase
    from .PaletteCommandBase import PaletteCommandBase
    from .Fusion360Utilities import AppObjects
    from .Fusion360Utilities import *
    from .Fusion360DebugUtilities import *

except:
    pass
