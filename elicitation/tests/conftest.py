import sys
from pathlib import Path

_ELICIT = Path(__file__).resolve().parents[1]
if str(_ELICIT) not in sys.path:
    sys.path.insert(0, str(_ELICIT))
