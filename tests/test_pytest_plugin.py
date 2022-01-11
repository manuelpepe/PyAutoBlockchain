from pab.init import Tree, TREE, File

from _pytest.config import ExitCode


pytest_plugins = ("pytester",)

STRATEGY_CODE = """from pab.strategy import BaseStrategy

class SampleStrategy(BaseStrategy):
    def run(self):
        print("OK")
"""


def init_tree(path, pycontent=STRATEGY_CODE):
    """Copy default tree but replace `strategies/` with `strategies.py`."""
    TEST_TREE = TREE.copy()
    TEST_TREE[1] = File("strategies.py", pycontent)
    Tree(TEST_TREE).create(path)


def test_plugin_loads_fixtures(testdir):
    init_tree(testdir.tmpdir)
    testdir.makepyfile(
        """
    pytest_plugins = ("pab.test", )
    def test_starts(setup_project, get_strat, pytestconfig):
        assert setup_project
        assert get_strat
        assert pytestconfig._pab
    """
    )
    result = testdir.runpytest()
    assert result.ret == ExitCode.OK
