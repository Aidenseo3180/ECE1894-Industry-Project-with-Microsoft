from k8_client import generate_k8_pods
from pytest_fixtures import pass_k8_info

def test_k8(pass_k8_info):
    """
    Test function to test k8 client correctly generating pods.

    :param pass_k8_info: Fixture to accept the name of the namespace and the number of pods.

    :return: None
    """

    custom_image, name, num_pods = pass_k8_info

    # generate k8 pods
    state = generate_k8_pods(given_custom_image=custom_image, given_namespace_name=name, num_pods=num_pods)

    assert(state == True)

