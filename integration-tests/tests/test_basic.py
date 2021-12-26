
def test_basic(setup_project):
    with setup_project("BasicProject") as pab:
        pab.process_tasks()