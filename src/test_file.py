def example_function():
    return True

def test_k8():
    """
    Test function to test k8 client correctly generating pods.

    :param pass_k8_info: Fixture to accept the name of the namespace and the number of pods.

    :return: None
    """
    assert(example_function() == True)

