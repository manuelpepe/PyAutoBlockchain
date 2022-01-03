from unittest.mock import Mock
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import contextmanager
from pab.init import chdir, File, Directory, Tree


@contextmanager
def chdir_into_temp():
    with TemporaryDirectory() as tmpdir:
        with chdir(tmpdir):
            yield tmpdir


def test_create_empty_directory():
    with chdir_into_temp() as tmpdir:
        Tree([Directory("MyDir")]).create(tmpdir)
        assert Path("MyDir").is_dir()


def test_create_file():
    with chdir_into_temp() as tmpdir:
        Tree([File("MyFile.txt", "My data")]).create(tmpdir)
        assert Path("MyFile.txt").is_file()
        assert Path("MyFile.txt").read_text() == "My data"


def test_create_complex_tree():
    with chdir_into_temp() as tmpdir:
        Tree(
            [
                Directory(
                    "MyDir",
                    [
                        Directory(
                            "MySubDir",
                            [File("FileInSubdir.py", "print('Hello world!')")],
                        ),
                        File("MyFile.txt", "My sample data"),
                    ],
                ),
                File("README.md", "Read me first"),
            ]
        ).create(tmpdir)

        assert Path("MyDir").is_dir()
        assert Path("MyDir/MySubDir").is_dir()
        assert Path("README.md").read_text() == "Read me first"
        assert Path("MyDir/MyFile.txt").read_text() == "My sample data"
        assert (
            Path("MyDir/MySubDir/FileInSubdir.py").read_text()
            == "print('Hello world!')"
        )


def test_create_optional_file():
    """Create optional file twice. Second time should not raise exception, but warn the user."""
    OLD_DATA = "some data"
    NEW_DATA = "some different data"
    WARNING = "File already exists. Do this and that."
    FILENAME = "OptionalFile.rst"

    def mocked_file(*args, **kwargs):
        file = File(*args, **kwargs)
        file.warn = Mock()
        return file

    should_be_created = mocked_file(FILENAME, OLD_DATA, optional=True, warning=WARNING)
    should_not_be_created = mocked_file(
        FILENAME, NEW_DATA, optional=True, warning=WARNING
    )
    with chdir_into_temp() as tmpdir:
        Tree([should_be_created]).create(tmpdir)
        assert Path(FILENAME).read_text() == OLD_DATA
        should_be_created.warn.assert_not_called()

        Tree([should_not_be_created]).create(tmpdir)
        # assert data was not overwritten and user was warned
        assert Path(FILENAME).read_text() == OLD_DATA
        should_not_be_created.warn.assert_called_once()
