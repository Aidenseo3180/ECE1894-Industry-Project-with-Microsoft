from Constants import NAMESPACE_NAME
from k8_client import generate_k8_pods, delete_k8_deployment
import logging
import pytest
import xdist
import xdist.workermanage
from kubernetes import client
from kubernetes import config as kubectl_config
from kubernetes.stream import stream
import uuid
import subprocess
import os
import signal
from execnet import XSpec
from pathlib import Path
import socket
from time import sleep

process_list = []  # list of subprocesses responsible for port-forwarding
ws_list = []  # list of streams for each pod

def pytest_xdist_setupnodes(config: pytest.Config, specs: list[XSpec]):

    if config.option.ktx != "pod":
        return

    # **********
    # * Set up *
    # **********
    global selected_namespace
    list_of_test_files = config.option.file_or_dir   # List of pytest files to run provided through the terminal
    list_of_test_files.append("src/Constants.py")    # Move Constants.py file because it's used by conftest.py in docker image
    custom_image = config.option.custom_image
    selected_namespace = config.option.namespace

    if selected_namespace == NAMESPACE_NAME:
        selected_namespace = selected_namespace + '-' + str(uuid.uuid4())
  
    num_pods = len(specs)
    generate_k8_pods(given_custom_image=custom_image, given_namespace_name=selected_namespace, num_pods=num_pods, list_filename=list_of_test_files) 

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
        ws = stream(
            api_instance.connect_get_namespaced_pod_exec,
            k8_pod_name, selected_namespace,
            command=exec_command,
            stderr=True, stdin=True,
            stdout=True, tty=False,
            _preload_content=False
        )
        ws_list.append(ws)

        # Remote address - localhost : TCP port pair
        peer_pair = ws.sock.sock.getpeername()
        assigned_port = peer_pair[1]

        # NOTE: select the "available TCP port" using temporary sockets
        s = socket.socket()
        s.bind(('', 0))
        available_port = s.getsockname()[1]
        s.close()

        # NOTE: Running port-forward in background, give os.setsid to fully delete the thread at the end
        process = subprocess.Popen(
            ["kubectl", "port-forward", "{}".format(k8_pod_name), "--namespace", "{}".format(selected_namespace), "{}:{}".format(available_port, assigned_port)],
            start_new_session=True
        )
        process_list.append(process)

        logging.info("Subprocess running for port-forwarding")

        # NOTE: Run the server.py from each pod to listen to localhost
        commands = [
            "python /code/ms_socketserver.py :{}".format(assigned_port)
        ]
        while ws.is_open():
            ws.update(timeout=1)
            if commands:
                cm = commands.pop(0)
                ws.write_stdin(cm + "\n")
            else:
                break

        logging.info("Server file listening to port")

        specs[idx].socket = '127.0.0.1:{}'.format(available_port)
        specs[idx].popen = False

        # NOTE: Bypass xdist checking whether the directory exists inside the k8 pod
        root = Path('src')   # TODO: Change this to sync with k8_client's configmap
        config.pluginmanager.get_plugin('dsession').nodemanager.roots.append(root)
        config.pluginmanager.get_plugin('dsession').nodemanager._rsynced_specs.add((specs[idx], root))

    # NOTE: Give extra time for threads to port-forward and run server.py from each pod
    sleep(2)


def pytest_sessionfinish(session):

    # NOTE: If controller, clean the allocated resources
    if xdist.is_xdist_controller(session):

        if session.config.option.ktx != "pod":
            return

        # Kill process and child processes
        for process in process_list:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)

        # Close the stream
        for ws in ws_list:
            ws.close()

        delete_k8_deployment(selected_namespace)
