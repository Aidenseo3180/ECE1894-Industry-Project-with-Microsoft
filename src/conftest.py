from Constants import NAMESPACE_NAME, CUSTOM_IMAGE_NAME, DEFAULT_NUM_PODS
from k8_client import generate_k8_pods, delete_k8_deployment
import logging
import pytest
import xdist
import execnet.gateway
import execnet.multi
import io
import xdist.workermanage
from kubernetes import watch, client
from kubernetes import config as kubectl_config
from kubernetes.stream import stream
from kubernetes.stream.ws_client import WSClient
import uuid
from queue import Queue
from xdist.workermanage import NodeManager
from xdist.dsession import DSession
from socket import SocketIO

import socket

# FIXME: This is for running multiple streams at the same time for all the pods. Don't worry about this and focus on getting 1 to work.
# @pytest.hookimpl(wrapper=True)
# def pytest_sessionstart(session):
#     # Skip original pytest_sessionstart operations, so that we can recreate active nodes after it's done

#     # CREATE KUBERNETES DEPLOYMENT ENVIRONMENT
#     logging.info("Items listed below:")
#     list_of_test_files = []

#     for item in session.config.option.file_or_dir:
#         list_of_test_files.append(item)

#     # Read in all the options
#     custom_image = session.config.option.custom_image
#     namespace_name = session.config.option.namespace
#     num_pods = session.config.getoption("--num_pods")

#     # If no namespace is given, give unique namespace
#     if namespace_name == NAMESPACE_NAME:
#         namespace_name = namespace_name + '-' + str(uuid.uuid4())
  
#     # TODO: check if not worker --> if not we run this generate k8 pods function
#     generate_k8_pods(given_custom_image=custom_image, given_namespace_name=namespace_name, num_pods=num_pods, list_filename=list_of_test_files) 

#     yield

#     # Since Dsession is the one that's responsible of 
#     plugin = session.config.pluginmanager.getplugin("dsession")

#     # stream object of kubernetes pods using namespace
#     w = watch.Watch()
#     apps_v1 = client.CoreV1Api()

#     # TODO: test this stream and see what's in there
#     stream = w.stream(
#         apps_v1.list_namespaced_pod(namespace_name),
#         namespace=namespace_name
#     )

#     delete_k8_deployment()

#     # We want eventlet (concurrent IO) with threads
#     # execnet.set_execmodel("eventlet", "thread")
#     # gw = execnet.Group()

#     # plugin._active_nodes = [
#     #     xdist.workermanage.WorkerController(gateway=Gateway(io..))
#     # ]

def pytest_collection_modifyitems(session, config, items):
    ##########
    # Set up #
    ##########
    logging.info("Items listed below:")
    list_of_test_files = []

    # Find the location of test files, put into configmap
    for item in items:
        list_of_test_files.append(item.location[0])

    custom_image = config.option.custom_image
    namespace_name = config.option.namespace
    num_pods = config.getoption("--num_pods")

    if namespace_name == NAMESPACE_NAME:
        namespace_name = namespace_name + '-' + str(uuid.uuid4())
  
    # NOTE: Run this only once in the very beginning, then comment it out
    # generate_k8_pods(given_custom_image=custom_image, given_namespace_name=namespace_name, num_pods=num_pods, list_filename=list_of_test_files) 
    
    # You can manually move socketserver.py by: Kubectl cp <location of the file> <name of the pod>:<save location> --namespace=<namespace>
    # Ex. kubectl cp src/test_hello_world.py mypod:/code/ --namespace=<my namespace>

    ##########
    # Stream #
    ##########

    kubectl_config.load_kube_config()
    api_instance = client.CoreV1Api()

    # NOTE: Comment these out when running generate_k8_pods(). After running it, manually give pod name & namespace here to create a stream
    temp_name = "ms-deployment-74497558b6-fh5mw"
    temp_ns = "pytest-namespace-b488f657-3799-46f4-84f6-d9edb45a5ecb"

    # Create a stream
    exec_command = ['/bin/sh']
    ws = stream(
        api_instance.connect_get_namespaced_pod_exec,
        temp_name, temp_ns,
        command=exec_command,
        stderr=True, stdin=True,
        stdout=True, tty=False,
        _preload_content=False
    )

    # NOTE: Method 1

    # Remote address
    # peer_pair = ws.sock.sock.getpeername()   # getsockname() if you want local address
    # available_port = peer_pair[1]
    # logging.info(peer_pair)

    # XXX: This is to run commands automatically (can't end port connection once connected though). You can do this manually from terminal
    # XXX: Can simply do: kubectl exec <name of pod> --namespace=<namespace> -it sh

    # commands = [
    #     "python /code/ms_socketserver.py :{}".format(available_port)
    #     # "pytest test/test_hello_world.py",
    #     # "echo Hello World"
    # ]
    # while ws.is_open():
    #     ws.update(timeout=1)
    #     if ws.peek_stdout():
    #         logging.info("STDOUT: %s" % ws.read_stdout())
    #     if ws.peek_stderr():
    #         logging.info("STDERR: %s" % ws.read_stderr())
    #     if commands:
    #         temp = commands.pop(0)
    #         logging.info("Running command... {}\n".format(temp))
    #         ws.write_stdin(temp + "\n")
    #     else:
    #         break

    # spec = "socket={0}:{1}".format(peer_pair[0], available_port)
    # try:
    #     gw = execnet.makegateway(spec)  # There's a problem with bootstrap not being able to read from io
    #     ws.close()
    #     logging.info("worked!!")

    # except Exception as e:
    #     logging.info(e)
    #     logging.info("failed!!")
    #     ws.close()


    # NOTE: Method 2
    try:
        ws.write_stdin('''python -c "print('Hello World')" \n'''.encode('ascii'))
        
        # XXX: Just testing here
        # data = b'python -c "print(\'Hello World\')" \n'
        # data = "python print('Hello World')\n"
        # if isinstance(data, str):
        #     data = data.encode("utf-8")
        
        ws.update(timeout=3)
        if ws.peek_stdout():
            logging.info("STDOUT: %s" % ws.read_stdout())
        if ws.peek_stderr():
            logging.info("STDERR: %s" % ws.read_stderr())

        logging.info("Passed")
        ws.close()

    except Exception as e:
        logging.info("failed!!")
        logging.info(e)
        ws.close()
    
    # NOTE: You can manully delete namespace from terminal without calling this
    # delete_k8_deployment(namespace_name)


def useless_comments_here():

    # exec = execnet.set_execmodel("thread")
    # modified_session = DSession(config)  # Can only implement 1 DSession
    # config.pluginmanager.register(modified_session, "dsession")
    # plugin = config.pluginmanager.getplugin("dsession")


    # spec = XSpec(spec)
    # gw = gateway_bootstrap.bootstrap(ws.sock.sock, spec)

    # ws.write_stdin('''python -c "print('Hello World')" \n'''.encode('ascii'))
    # ws.update(timeout=1)
    # if ws.peek_stdout():
    #     logging.info("STDOUT: %s" % ws.read_stdout())
    # if ws.peek_stderr():
    #     logging.info("STDERR: %s" % ws.read_stderr())

    # breakpoint()

    # ws.update(timeout=1)
    # if ws.peek_stdout():
    #     logging.info("STDOUT: %s" % ws.read_stdout())
    # if ws.peek_stderr():
    #     logging.info("STDERR: %s" % ws.read_stderr())
    # breakpoint()
    
    # spec = XSpec(spec)
    # gw = gateway_bootstrap.bootstrap(ws.sock.sock, spec)

    # breakpoint()

    # NOTE: ws.read_XXX() thinks you're giving commands as sh --> so, you can't give inputs such as ws.write_stdin("Hello World\n")
    # It has to be something like ws.write_stdin("echo Hello World\n") <-- NOTE: you have to have \n at the end of the command (for some reason)
    # Ex. ws.write_stdin('''python -c "print('Hello World')" \n''')

    # '''
    # ws.write_stdin("echo Hello World\n")
    # ws.update(timeout=1)
    # if ws.peek_stdout():
    #     logging.info("STDOUT: %s" % ws.read_stdout())
    # if ws.peek_stderr():
    #     logging.info("STDERR: %s" % ws.read_stderr())

    # breakpoint()
    
    # '''

    # Make gateway for the spec
    # gw = execnet.Group().makegateway(spec) # FIXME: this spec will later be changed to spec_socket??
    # config.hook.pytest_xdist_newgateway(gateway=gw)

    # breakpoint()

    #stream.write_channel()

    # w = watch.Watch()
    # apps_v1 = client.CoreV1Api()
    
    # stream = w.stream(
    #     apps_v1.list_namespaced_pod,
    #     namespace_name
    # )

    # spec = None
    # try:
    #     for event in stream:
    #         logging.info('-----')
    #         # event_type = event["type"]
    #         # logging.info(event_type)
    #         obj = event["object"]
    #         temp_list = obj.to_dict()
    #         # logging.info(obj)
    #         # metadata = obj.get('metadata')
    #         # logging.info(metadata)
    #         spec = temp_list.get('spec')
    #         # code = obj.get('code')
    #         # logging.info(code)
    #         break   # NOTE: break out of generator right away since it will run forever

    # except Exception:
    #     logging.info('Failed')

    # NOTE: This is for Gateway (creating our own IO wrapper) way:
    
    # We want eventlet (concurrent IO) with threads
    # execnet.set_execmodel("eventlet", "thread")
    # spec = "popen"  # Becomes XSpec(spec) from makegateway(spec) function
    # gw = execnet.gateway.Gateway(io=io, spec=spec)
    # plugin = session.config.pluginmanager.getplugin("dsession")

    # plugin._active_nodes = [
    #     xdist.workermanage.WorkerController(gateway=gw)
    # ]
            
    # NOTE: This is for group.makegateway function way:

    # execnet.set_execmodel("eventlet", "thread")
    # modified_session = DSession(config)  # Can only implement 1 DSession
    # config.pluginmanager.register(modified_session, "dsession")
    # plugin = config.pluginmanager.getplugin("dsession")

    # # Make gateway for the spec
    # gw = execnet.Group().makegateway(spec) # has to be socket io
    # config.hook.pytest_xdist_newgateway(gateway=gw)

    # # Give temporary numprocesses for now
    # config.option.numprocesses = 1
    # if config.option.numprocesses:
    #     if config.option.dist == "no":
    #         config.option.dist = "load"
    #     numprocesses = config.option.numprocesses
    #     if config.option.maxprocesses:
    #         numprocesses = min(numprocesses, config.option.maxprocesses)
    #     config.option.tx = ["popen"] * numprocesses
    # if config.option.distload:
    #     config.option.dist = "load"

    # # Set up rest of stuffs for WorkerController constructor
    # queue = Queue()
    # nodemanager = NodeManager(config)
    # plugin._active_nodes = [
    #     xdist.workermanage.WorkerController(nodemanager=nodemanager, gateway=gw, config=config, putevent=queue.put)
    # ]
    # plugin._active_nodes[0].setup()   # Call setup() to handle rest of stuffs
    
    # NOTE: Kill the WorkerController at the end (but how?)
    # plugin._active_nodes[0].ensure_teardown()
    # plugin._active_nodes[0].shutdown()
    pass

def pytest_addoption(parser):
    parser.addoption(
        "--namespace", action="store", default=NAMESPACE_NAME, help="Define the namespace of pods"
    )
    parser.addoption(
        "--custom_image", action="store", default=CUSTOM_IMAGE_NAME, help="Define the name of the custom image"
    )
    parser.addoption(
        "--num_pods", action="store", default=DEFAULT_NUM_PODS, help="Define the number of pods"
    )
