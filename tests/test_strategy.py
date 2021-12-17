import string
import random

from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import contextmanager

from pab.strategy import load_strategies

STRATEGY_TEMPLATE="""
from pab.strategy import BaseStrategy

class {name}(BaseStrategy):
    def run(self):
        pass
"""

def randname(size: int = 15):
    return ''.join(random.choice(string.ascii_letters) for i in range(size))

@contextmanager
def template_strat_in_temp_dir(name: str) -> Path:
    with TemporaryDirectory() as tmp:
        startsfile = Path(tmp) / "strategies.py"
        startsfile.write_text(STRATEGY_TEMPLATE.format(name=name))
        yield Path(tmp)

def test_import_strategies_from_outside_cwd():
    NAME = randname()
    with template_strat_in_temp_dir(NAME) as tmpdir:
        strats = load_strategies(tmpdir)
        assert NAME in Path(tmpdir / "strategies.py").read_text()
        assert NAME in [s.__name__ for s in strats]
