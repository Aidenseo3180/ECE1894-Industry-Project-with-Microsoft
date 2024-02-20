from Constants import NAMESPACE_NAME, CUSTOM_IMAGE_NAME
import logging

def pytest_collection_modifyitems(session, config, items):
    logging.info("Items listed below:")
    for item in items:
        logging.info(item.path)

def pytest_addoption(parser):
    parser.addoption(
        "--namespace", action="store", default=NAMESPACE_NAME, help="Define the namespace of pods"
    )
    parser.addoption(
        "--custom_image", action="store", default=CUSTOM_IMAGE_NAME, help="Define the name of the custom image"
    )
    parser.addoption(
        "--num_pods", action="store", default=4, help="Define the name of the custom image"
    )