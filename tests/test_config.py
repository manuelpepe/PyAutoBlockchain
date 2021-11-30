import os

from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from pab.config import Config, ConfigDef, ConfigSchema, LCDict
from pab.init import chdir


@contextmanager
def temp_environ():
    prev_environ = {**os.environ}
    with TemporaryDirectory() as tmpdir:
        with chdir(tmpdir):
            yield tmpdir
    os.environ = prev_environ


class CustomSchema(ConfigSchema):
    def _load(self):
        return LCDict({
            "my.config": ConfigDef("my.config", "", "int", 0),
            "my.second.config": ConfigDef("my.second.config", "", "string", "DEFAULT"),
            "my.second.other": ConfigDef("my.second.other", "", "string", "DEFAULT")
        })


def test_load_from_env():
    with temp_environ() as tmpdir:
        conf = Config(Path(tmpdir))
        conf.schema = CustomSchema()
        conf.load()
        assert conf.get("my.config") == 0  # Defaults to 0 by schema

        os.environ["PAB_CONF_MY_CONFIG"] = "123"
        conf.load()  # Now loads from environ
        assert conf.get("my.config") == 123  



def test_load_from_envfile():
    with temp_environ() as tmpdir:
        conf = Config(Path(tmpdir))
        conf.schema = CustomSchema()
        conf.load()
        assert conf.get("my.config") == 0  # Defaults to 0 by schema

        Path(".env").write_text("PAB_CONF_MY_CONFIG=321")
        conf.load()  # Now loads from .env file
        assert conf.get("my.config") == 321  


def test_load_from_custom_envfile():
    with temp_environ() as tmpdir:
        Path(".env.sandbox").write_text('')
        conf = Config(Path(tmpdir), ["sandbox"])
        conf.schema = CustomSchema()
        conf.load()
        assert conf.get("my.config") == 0  # Defaults to 0 by schema

        Path(".env.sandbox").write_text("PAB_CONF_MY_CONFIG=456")
        conf.load()  # Now loads from .env file
        assert conf.get("my.config") == 456  


def test_load_from_jsonfile():
    with temp_environ() as tmpdir:
        conf = Config(Path(tmpdir))
        conf.schema = CustomSchema()
        conf.load()
        assert conf.get("my.config") == 0  # Defaults to 0 by schema

        (Path(tmpdir) / Path("config.json")).write_text("""{
            "my": {
                "config": 654
            }
        }""")
        conf.load()  # Now loads from .env file
        assert conf.get("my.config") == 654  


def test_get_tree():
    with temp_environ() as tmpdir:
        conf = Config(Path(tmpdir))
        conf.schema = CustomSchema()
        conf.load()
        assert conf.get("my") == {
            "config": 0,
            "second": {
                "config": "DEFAULT",
                "other": "DEFAULT"
            }
        }


def test_get_tree_with_data_and_defaults():
    with temp_environ() as tmpdir:
        os.environ["PAB_CONF_MY_SECOND_CONFIG"] = "NEW STRING"
        conf = Config(Path(tmpdir))
        conf.schema = CustomSchema()
        conf.load()
        assert conf.get("my") == {
            "config": 0,
            "second": {
                "config": "NEW STRING",
                "other": "DEFAULT"
            }
        }


