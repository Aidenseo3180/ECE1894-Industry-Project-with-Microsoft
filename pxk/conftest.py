# NOTE: Worker_contest.py. Provided to pods but do not do anything. Just to make pods to understand the received pytest command
def pytest_addoption(parser):
    parser.addoption(
        "--namespace", action="store", default=None, help="Defines the namespace of pods"
    )
    parser.addoption(
        "--custom_image", action="store", default=None, help="Defines the name of the custom image"
    )
