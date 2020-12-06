import sys
import os
from pathlib import Path
path = str(Path(os.getcwd()).parent)+'qTools'
sys.path.insert(0, path)