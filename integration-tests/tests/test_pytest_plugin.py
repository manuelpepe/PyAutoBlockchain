from pab.init import Tree, TREE, File, Directory

from _pytest.config import ExitCode


pytest_plugins = ("pytester",)

STRATEGY_CODE = """from pab.strategy import BaseStrategy

class ChangeValue(BaseStrategy):
    def __init__(self, *args, contract: str = "", value: str = ""):
        super().__init__(*args)
        self.contract = self.contracts.get(contract)
        self.value = value

    def run(self):
        self.transact(
            self.accounts[1],
            self.contract.functions.setString,
            (self.value, )
        )
"""


CONTRACT_CODE = """
contract PABTest {
    string myString;
    constructor() {
        myString = "OLD";
    }
    function setString(string memory newString) public {
        myString = newString;
    }
    function getString() public view returns(string memory) {
        return myString;
    }
}
"""

MIGRATION_CODE = """
var PABTest = artifacts.require("PABTest");
module.exports = function(deployer) {
    deployer.deploy(PABTest);
};
"""

TRUFFLE_CONFIG = """
module.exports = {
    networks: {
        development: {
            host: "127.0.0.1",
            port: 8545,
            network_id: "*",
        },
    },
    compilers: {
        solc: {
            version: "0.8.9",
        }
    },
};
"""


def init_tree(path):
    """Create a modified version of the default tree."""
    extra = Directory(
        "tests",
        [
            Directory(
                "truffle",
                [
                    Directory("contracts", [File("PABTest.sol", CONTRACT_CODE)]),
                    Directory("migrations", [File("1_deploy.js", MIGRATION_CODE)]),
                    File("truffle-config.js", TRUFFLE_CONFIG),
                ],
            )
        ],
    )
    tree = TREE.copy()
    # Replace strategies
    tree[1] = File("strategies.py", STRATEGY_CODE)
    tree[5].content = "[]"  # Clear tasks.json
    tree[6].content = "{}"  # Clear contracts.json
    del tree[2]  # Remove basic tests directory
    tree.append(extra)
    Tree(tree).create(path)


def test_plugin_loads_fixtures(pytester):
    init_tree(pytester.path)
    pytester.makeconftest(
        """
    import pytest
    pytest_plugins = ("pab.test", )
    """
    )
    pytester.makepyfile(
        """
    def test_starts(setup_project, get_strat, pytestconfig):
        with setup_project() as pab:
            params = {
                "contract": "PABTest",
                "value": "NEW"
            }
            strat = get_strat(pab, 'ChangeValue', params)
            assert strat
            assert strat.contract.functions.getString().call() == "OLD"
            strat.run()
            assert strat.contract.functions.getString().call() == "NEW"
    """
    )
    result = pytester.runpytest()
    assert result.ret == ExitCode.OK
