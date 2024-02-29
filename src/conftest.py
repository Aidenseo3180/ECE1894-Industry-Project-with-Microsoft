from Constants import NAMESPACE_NAME, CUSTOM_IMAGE_NAME
from k8_client import generate_k8_pods
import logging


# Find the location of test files, put into configmap
def pytest_collection_modifyitems(session, config, items):
    logging.info("Items listed below:")
    LIST_OF_TEST_FILES = []

    for item in items:
        LIST_OF_TEST_FILES.append(item.location[0])

    custom_image = config.option.custom_image
    name = config.option.namespace
    num_pods = config.getoption("--num_pods")
  
    generate_k8_pods(given_custom_image=custom_image, given_namespace_name=name, num_pods=num_pods, list_filename=LIST_OF_TEST_FILES) 

def pytest_addoption(parser):
    parser.addoption(
        "--namespace", action="store", default=NAMESPACE_NAME, help="Define the namespace of pods"
    )
    parser.addoption(
        "--custom_image", action="store", default=CUSTOM_IMAGE_NAME, help="Define the name of the custom image"
    )
    parser.addoption(
        "--num_pods", action="store", default=4, help="Define the number of pods"
    )
