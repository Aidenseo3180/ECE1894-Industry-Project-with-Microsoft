from kubernetes import client, config

def generate_k8_pods(custom_image, namespace):

    return custom_image, namespace

    # TODO deal with k8 later

    # # load cluster configuration
    # config.load_kube_config()  # for local environment

    # # same as kubectl get nodes
    # v1 = client.CoreV1Api()
    # v1.list_node()  

