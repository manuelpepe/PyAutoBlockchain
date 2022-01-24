from pab.core import TasksRunner


def test_basic(setup_project):
    with setup_project("BasicProject") as pab:
        runner = TasksRunner(pab)
        runner.process_tasks()
