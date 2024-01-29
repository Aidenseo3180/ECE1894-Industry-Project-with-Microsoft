from main.k8_client import generate_k8_pods
from test.pytest_fixtures import pass_k8_info
from Constants import DEFAULT_NAMESPACE, CUSTOM_IMAGE

def test_k8(pass_k8_info):
    """
    Test function to test k8 client correctly generating pods.

    :param pass_k8_info: Fixture to accept the name of the namespace and the number of pods.

    :return: None
    """

    custom_image, name = pass_k8_info

    # generate k8 pods
    a, b = generate_k8_pods(custom_image=custom_image, namespace=name)

    assert(custom_image == a and name == b)

