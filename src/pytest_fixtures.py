import pytest

@pytest.fixture
def pass_k8_info(request)->list:
    """
    Fixture to accept the name of the namespace from the command line.
    :param request: pytest request object

    :return: num of pods to use and their namespace
    """

    custom_image = str(request.config.getoption("--custom_image"))
    name = str(request.config.getoption("--namespace"))
    num_pods = int(request.config.getoption("--num_pods"))
    
    return [custom_image, name, num_pods]
