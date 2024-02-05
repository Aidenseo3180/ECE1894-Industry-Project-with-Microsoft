from kubernetes import client, config

def generate_k8_pods(given_custom_image, given_namespace_name):
    #NOTE Assuming image and cluster already exist

    # bring in k8 configuration to code so that it can handle k8
    config.load_kube_config()
    v1 = client.CoreV1Api()

    ######################################
    # same as pod.YAML file in k8 folder #
    ######################################
    containers = []
    container1 = client.V1Container(name='private-reg-container', image=given_custom_image, image_pull_policy='Never')
    containers.append(container1)

    # specify the pod spec
    pod_spec = client.V1PodSpec(containers=containers)
    # specify the pod metadata
    pod_metadata = client.V1ObjectMeta(name='private-reg', namespace=given_namespace_name)

    #############
    # Namespace #
    #############
    # create the namespace if doesn't exist
    namespaces = v1.list_namespace()
    all_namespaces = []
    for ns in namespaces.items:
        all_namespaces.append(ns.metadata.name)

    # add namespace if doesn't exist
    # Like pod.yaml, there's namespace.yaml too. Below is for the yaml specifically designed to create namespace
    if given_namespace_name not in all_namespaces:
        print("---- Namespace doesn't exist, so one is created ----")
        # NOTE namespace and pod are different. YAML can be created for either the namespace or the pod. This is like creating YAML of namespace
        # create metadata of namespace
        namespace_metadata = client.V1ObjectMeta(name=given_namespace_name)
        v1.create_namespace(
            client.V1Namespace(metadata=namespace_metadata)
        )

    # Checking if namespace is successfully added
    # Equivalent to: kubectl get namespace
    namespaces = v1.list_namespace()
    print("---- Checking existing namespaces ----")
    for ns in namespaces.items:
        print(ns.metadata.name)

    ###############################
    # Adding a pod with namespace #
    ###############################
    # First, check if pod with namespace already exists
    # Grab names of pods with namespace, save it
    pod_with_namespace = v1.list_namespaced_pod(namespace=given_namespace_name)
    all_pod_with_namespace = []
    for pod_ns in pod_with_namespace.items:
        all_pod_with_namespace.append(pod_ns.metadata.name)

    # TODO: In the future, you'll have to give number of pods by -n. Since pods can't hav same name, come out with random name generator
    # Check to make sure that we do not create pod with same name
    if 'private-reg' not in all_pod_with_namespace:
        # create a pod body by combinding metadata with spec
        pod_body = client.V1Pod(api_version='v1', kind='Pod', metadata=pod_metadata, spec=pod_spec)
        print("---- Pod created ----")
        v1.create_namespaced_pod(namespace=given_namespace_name, body=pod_body)

    # Print pods running
    # Equivalent to: kubectl get pods --namespace <Namespace>
    print("---- Running Pods with namespace ----")
    pod_with_namespace = v1.list_namespaced_pod(namespace=given_namespace_name)
    for pod_ns in pod_with_namespace.items:
        print(pod_ns.metadata.name)

    # Delete pod at the end
    v1.delete_namespaced_pod(namespace=given_namespace_name, name='private-reg')

    return given_custom_image, given_namespace_name

