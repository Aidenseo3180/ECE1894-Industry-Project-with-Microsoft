from Constants import DEFAULT_NAMESPACE, CUSTOM_IMAGE

def pytest_addoption(parser):
    parser.addoption(
        "--namespace", action="store", default=DEFAULT_NAMESPACE, help="Define the namespace of pods"
    )
    parser.addoption(
        "--custom_image", action="store", default=CUSTOM_IMAGE, help="Define the name of the custom image"
    )
