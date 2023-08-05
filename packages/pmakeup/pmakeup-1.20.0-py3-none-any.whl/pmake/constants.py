import datetime
import itertools
import math
import os

import typing

from pmake import version

STANDARD_MODULES = [
    ("math", math),
    ("datetime", datetime),
    ("itertools", itertools),
    ("os", os),
    ("typing", typing)
]

STANDARD_VARIABLES = [
    ("VERSION", version.VERSION, "Version of the program"),
    ("UTCDATE", datetime.datetime.utcnow(), "time when the program started (in UTC)"),
    ("DATE", datetime.datetime.now(), "time when the program started (in user timezone)"),
]