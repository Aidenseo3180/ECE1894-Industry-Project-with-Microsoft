from kubernetes import client, config
from Constants import NAMESPACE_NAME
import logging
import uuid
from pathlib import Path



def generate_k8_pods(given_custom_image, given_namespace_name, num_pods, list_filename):
    #NOTE Assuming image and cluster already exist

    # bring in k8 configuration to code so that it can handle k8
    config.load_kube_config()
    apps_v1 = client.CoreV1Api()

    #############
    # Namespace #
    #############
    # --- Creation of namespace
    logging.info('---- Namespace Creation Started ----')

    # If no namespace is given, give unique namespace
    if given_namespace_name == NAMESPACE_NAME:
        given_namespace_name = given_namespace_name + '-' + str(uuid.uuid4())

    try:
        namespace_metadata = client.V1ObjectMeta(name=given_namespace_name)
        apps_v1.create_namespace(
            client.V1Namespace(metadata=namespace_metadata)
        )
    except Exception:
        # return immediately if given namespace already exists
        return False

    # --- Check namespace
    namespaces = apps_v1.list_namespace()
    logging.info('---- Namespace Successfully Added. List of Namespaces Below ----')
    for ns in namespaces.items:
        logging.info(ns.metadata.name)

    ##############
    # Config Map #
    ##############
    logging.info('---- Config Map Creation Started ----')
    
    # --- Config Map Meta Data
    config_map_meta_data = client.V1ObjectMeta(
        name='ms-config',
        namespace=given_namespace_name
    )

    # --- Put test files as key-value pair to Config Map
    # dict that stores data of configMap
    config_map_data = {}
    for test_file_path in list_filename:
        # Relative Path
        file = open(test_file_path, 'r')
        file_content = file.read()
        # split file_path by slash, read the last occurence
        
        file_name = Path(test_file_path).name
        
        config_map_data.update({file_name:file_content})
        file.close()

    logging.info("---- List of test files that will be added to config map in key-value pair ----")
    logging.info(config_map_data)

    config_map_body = client.V1ConfigMap(
        api_version='v1',
        kind='ConfigMap',
        metadata=config_map_meta_data,
        data=config_map_data
    )

    apps_v1.create_namespaced_config_map(
        namespace=given_namespace_name,
        body=config_map_body
    )

    logging.info("---- Config Map Successfully Created. Below is the created CM ----")

    # Check existence of config map
    current_cm = apps_v1.list_namespaced_config_map(given_namespace_name)
    for cm in current_cm.items:
        logging.info(cm.metadata.name)
    
    #######################
    # Adding a Deployment #
    #######################
    logging.info('---- Deployment Creation Started ----')
    
    # --- METADATA
    delpoyment_body_metadata = client.V1ObjectMeta(
        name='ms-deployment', 
        namespace=given_namespace_name, 
        labels={'app':'ms'}
    )

    # --- INNER SPEC-CONTAINER

    # Volume Mount List
    volume_mount_list = []
    volume_mount1 = client.V1VolumeMount(
        name='config-volume',
        mount_path='/code/test'
    )
    volume_mount_list.append(volume_mount1)

    # Container inside the inner spec of template
    containers = []
    container1 = client.V1Container(
        name='ms-container', 
        image=given_custom_image, 
        image_pull_policy='Never',
        volume_mounts=volume_mount_list
    )
    containers.append(container1)

    # Volume Config Map Info
    ##
    items_list = []
    for test_file_path in list_filename:
        # Get name of file, give to item as key-path pair (to include files in configMap)
        file_name = Path(test_file_path).name
        item = client.V1KeyToPath(
            key=file_name,
            path=file_name
        )
        items_list.append(item)

    volumes_config_map_info = client.V1ConfigMapVolumeSource(
        name='ms-config',
        items=items_list
    )

    # Volume that goes into inner spec
    volume_list = []
    volume1 = client.V1Volume(
        name='config-volume',
        config_map=volumes_config_map_info
    )
    volume_list.append(volume1)

    spec_template_spec = client.V1PodSpec(
        containers=containers,
        volumes=volume_list
    )

    # --- SPEC-SELECTOR-MATCH LABEL
    spec_selector = client.V1LabelSelector(
        match_labels={'app':'ms'}
    )

    # --- TEMPLATE
    template_metadata = client.V1ObjectMeta(
        labels={'app':'ms'}
    )
    spec_template = client.V1PodTemplateSpec(
        metadata=template_metadata, 
        spec=spec_template_spec
    )

    # --- SPEC
    deployment_body_spec = client.V1DeploymentSpec(
        replicas=num_pods, 
        selector=spec_selector, 
        template=spec_template
    )

    # --- CONFIG & CLIENT
    core_v1 = client.AppsV1Api()

    # --- ENTIRE YAML
    body = client.V1Deployment(
        api_version='apps/v1', 
        kind='Deployment', 
        metadata=delpoyment_body_metadata, 
        spec=deployment_body_spec
    )

    # --- CREATE DEPLOYMENT
    core_v1.create_namespaced_deployment(
        namespace=given_namespace_name, 
        body=body
    )
    logging.info('---- Deployment Successfully Created. Pods listed below. ----')

    # Print pods with namespace in deployment to confirm that they exist
    # FIXME: It seems like code runs faster than the genenration of deployment, leading below codes to not print anything
    # list_namespace_pod = apps_v1.list_namespaced_pod(given_namespace_name)
    # for np in list_namespace_pod.items:
    #     logging.info(np.metadata.name)

    # --- Deleting namespace at the end deletes all the related pods
    apps_v1.delete_namespace(name=given_namespace_name)
    logging.info('---- Namespace Successfully Deleted ----')

    return True

