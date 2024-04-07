from src.Constants import NAMESPACE_NAME, CUSTOM_IMAGE_NAME

def pytest_addoption(parser):
    parser.addoption(
        "--namespace", action="store", default=NAMESPACE_NAME, help="Defines the namespace of pods"
    )
    parser.addoption(
        "--custom_image", action="store", default=CUSTOM_IMAGE_NAME, help="Defines the name of the custom image"
    )
    parser.addoption(
        "--ktx", action="store", default=None, help="Triggers the pytest-xdist-kubernetes plugin"
    )
