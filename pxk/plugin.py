from .Constants import NAMESPACE_NAME, CUSTOM_IMAGE_NAME
from .k8_client import generate_k8_pods, delete_k8_deployment
import logging
import pytest
import xdist
from kubernetes import client
from kubernetes import config as kubectl_config
from kubernetes.stream import stream
import uuid
import subprocess
from execnet import XSpec
from pathlib import Path
import socket
from time import sleep


def pytest_addoption(parser):
    parser.addoption(
        "--namespace", action="store", default=NAMESPACE_NAME, help="Defines the namespace of pods"
    )
    parser.addoption(
        "--custom_image", action="store", default=CUSTOM_IMAGE_NAME, help="Defines the name of the custom image"
    )


def pytest_xdist_setupnodes(config: pytest.Config, specs: list[XSpec]):

    if config.known_args_namespace.tx[0] != 'pod':
        return
    
    global process_list     # list of subprocesses responsible for port-forwarding
    process_list = []
    global ws_list          # list of streams for each pod' 
    ws_list = []
    
    # **********
    # * Set up *
    # **********
    global selected_namespace
    selected_namespace = config.option.namespace

    custom_image_list = config.option.custom_image.split(',')
    list_of_test_files = config.option.file_or_dir      # List of pytest files to run provided through the terminal

    # Find the path of packages and test files
    pkg_dir = Path(__file__).parent
    test_dir = Path(list_of_test_files[0]).parent

    # Move in all the necessary files from the package
    list_of_test_files.append(f"{pkg_dir}/ms_socketserver.py") # Move server.py that will run from the pod
    list_of_test_files.append(f"{pkg_dir}/conftest.py")

    if selected_namespace == NAMESPACE_NAME:
        selected_namespace = selected_namespace + '-' + str(uuid.uuid4())
  
    num_pods = len(specs)
    generate_k8_pods(
        given_custom_images=custom_image_list, 
        given_namespace_name=selected_namespace, 
        num_pods=num_pods, 
        list_filename=list_of_test_files, 
        file_dir=test_dir
    ) 

    # ***************************
    # * Communication with Pods *
    # ***************************

    kubectl_config.load_kube_config()
    api_instance = client.CoreV1Api()
    
    # NOTE: Go through all existing pods with the same namespace
    list_namespace_pod = api_instance.list_namespaced_pod(selected_namespace)
    for idx, np in enumerate(list_namespace_pod.items):
        k8_pod_name = np.metadata.name

        # Create a stream
        exec_command = ['/bin/sh']
        try:
            ws = stream(
                api_instance.connect_get_namespaced_pod_exec,
                k8_pod_name, selected_namespace,
                command=exec_command,
                stderr=True, stdin=True,
                stdout=True, tty=False,
                _preload_content=False
            )
            ws_list.append(ws)
        except:
            logging.info('---- Stream cannot be generated. Make sure that the pod is running ----')
            delete_k8_deployment(selected_namespace)
            raise Exception

        # Remote address - localhost : TCP port pair
        peer_pair = ws.sock.sock.getpeername()
        assigned_port = peer_pair[1]

        # NOTE: select the "available TCP port" using temporary sockets
        s = socket.socket()
        s.bind(('', 0))
        available_port = s.getsockname()[1]
        s.close()

        # NOTE: Running port-forward in background, give os.setsid to fully delete the thread at the end
        try:
            process = subprocess.Popen(
                ["kubectl", "port-forward", f"{k8_pod_name}", "--namespace", f"{selected_namespace}", f"{available_port}:{assigned_port}"],
                start_new_session=True
            )
            process_list.append(process)
        except:
            logging.info('---- Subprocess cannot be created. Check if the port is already occupied ----')
            delete_k8_deployment(selected_namespace)
            raise Exception

        logging.info("Subprocess running for port-forwarding")

        # NOTE: Run the server.py from each pod to listen to localhost
        commands = [
            f"python /code/{test_dir}/ms_socketserver.py :{assigned_port}"
        ]
        try:
            while ws.is_open():
                ws.update(timeout=1)
                if commands:
                    cm = commands.pop(0)
                    ws.write_stdin(cm + "\n")
                else:
                    break
        except:
            logging.info("Issue related to stream happened.. Terminating")
            delete_k8_deployment(selected_namespace)
            raise Exception

        logging.info("Server file listening to port")

        specs[idx].socket = f'127.0.0.1:{available_port}'
        specs[idx].popen = False

        # NOTE: Bypass xdist checking whether the directory exists inside the k8 pod
        config.pluginmanager.get_plugin('dsession').nodemanager.roots.append(test_dir)
        config.pluginmanager.get_plugin('dsession').nodemanager._rsynced_specs.add((specs[idx], test_dir))

    # NOTE: Give extra time for threads to port-forward and run server.py from each pod
    logging.info('---- Give Extra Time for Threads to Run Tasks... ----')
    sleep(2)


def pytest_sessionfinish(session):

    # NOTE: If controller, clean the allocated resources
    if xdist.is_xdist_controller(session):

        if session.config.known_args_namespace.tx[0] != 'pod':
            return

        # Kill process and child processes
        for process in process_list:
            process.kill()

        # Close the stream
        for ws in ws_list:
            ws.close()

        delete_k8_deployment(selected_namespace)
