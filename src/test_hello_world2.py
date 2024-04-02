import logging

def hello_world_function():
    return "Hello World"

def test_hello_world():
    logging.info("This is pod 2")
    assert hello_world_function() == "Hello World"
