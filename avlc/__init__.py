from .version import __version__, __major__, __minor__, __micro__, __stage__
from .equalizer import *
from .player import *
from .enums import *
from .media import *
from .event import *
from .util import *
from .tcm import *


def version(version_type=None):
    if version_type is None:
        return __version__
    elif version_type == "major":
        return __major__
    elif version_type == "minor":
        return __minor__
    elif version_type == "micro":
        return __micro__
    elif version_type == "stage":
        return __stage__
    else:
        raise ValueError(f'Invalid Version: "{version_type}"')
