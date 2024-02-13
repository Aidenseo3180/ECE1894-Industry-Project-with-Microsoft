from kubernetes import client, config
import logging

def generate_k8_pods(given_custom_image, given_namespace_name):
    #NOTE Assuming image and cluster already exist

    # bring in k8 configuration to code so that it can handle k8
    config.load_kube_config()
    apps_v1 = client.CoreV1Api()

    ######################################
    # same as pod.YAML file in k8 folder #
    ######################################
    containers = []
    container1 = client.V1Container(name='ms-container', image=given_custom_image, image_pull_policy='Never')
    containers.append(container1)

    #############
    # Namespace #
    #############
    # create the namespace
    # Like pod.yaml, there's namespace.yaml too. Below is for the yaml specifically designed to create namespace
    try:
        namespace_metadata = client.V1ObjectMeta(name=given_namespace_name)
        apps_v1.create_namespace(
            client.V1Namespace(metadata=namespace_metadata)
        )
    except Exception:
        # return immediately if given namespace already exists
        return False

    # Checking if namespace is successfully added (kubectl get namespace)
    namespaces = apps_v1.list_namespace()
    logging.info('---- Namespace Successfully Added. List of Namespaces Below ----')
    for ns in namespaces.items:
        logging.info(ns.metadata.name)

    #######################
    # Adding a Deployment #
    #######################
    
    # METADATA
    delpoyment_body_metadata = client.V1ObjectMeta(
        name='ms-deployment', 
        namespace=given_namespace_name, 
        labels={"app":"ms"}
    )

    # INNER SPEC-CONTAINER
    spec_template_spec = client.V1PodSpec(containers=containers)

    # SPEC-SELECTOR-MATCH LABEL
    spec_selector = client.V1LabelSelector(
        match_labels={"app":"ms"}
    )

    # TEMPLATE
    template_metadata = client.V1ObjectMeta(
        labels={"app":"ms"}
    )
    spec_template = client.V1PodTemplateSpec(
        metadata=template_metadata, 
        spec=spec_template_spec
    )

    # SPEC
    deployment_body_spec = client.V1DeploymentSpec(
        replicas=4, 
        selector=spec_selector, 
        template=spec_template
    )

    # CONFIG & CLIENT
    core_v1 = client.AppsV1Api()

    # ENTIRE YAML
    body = client.V1Deployment(
        api_version='apps/v1', 
        kind='Deployment', 
        metadata=delpoyment_body_metadata, 
        spec=deployment_body_spec
    )

    # CREATE DEPLOYMENT
    core_v1.create_namespaced_deployment(
        namespace=given_namespace_name, 
        body=body
    )
    logging.info('---- Deployment Successfully Created ----')

    # TODO: Print pods with namespace in deployment to confirm that they exist

    # Deleting namespace at the end deletes all the related pods
    apps_v1.delete_namespace(name=given_namespace_name)
    logging.info('---- Namespace Successfully Deleted ----')

    return True

