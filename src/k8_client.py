from kubernetes import client, config
import logging
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_fixed

def generate_k8_pods(given_custom_image, given_namespace_name, num_pods, list_filename):
    # NOTE: Assuming image and cluster already exist

    config.load_kube_config()
    apps_v1 = client.CoreV1Api()

    # *************
    # * Namespace *
    # *************
    # --- Creation of namespace
    logging.info('---- Namespace Creation Started ----')

    try:
        namespace_metadata = client.V1ObjectMeta(name=given_namespace_name)
        apps_v1.create_namespace(
            client.V1Namespace(metadata=namespace_metadata)
        )
    except Exception:
        # return immediately if given namespace already exists OR environment setup is incorrect (ex. doesn't have running cluster with image)
        logging.info('---- Creation Failed.... Terminating ----')
        return False

    # --- Namespace creation
    logging.info('---- Namespace Successfully Added ----')

    # **************
    # * Config Map *
    # **************
    logging.info('---- Config Map Creation Started ----')
    
    # --- Config Map Meta Data
    config_map_meta_data = client.V1ObjectMeta(
        name='ms-config',
        namespace=given_namespace_name
    )

    # --- Put the content of the test files as key-value pair to Config Map
    config_map_data = {}  # dictionary to store data of configMap
    for test_file_path in list_filename:
        # Relative Path
        file = open(test_file_path, 'r')
        file_content = file.read()
        
        file_name = Path(test_file_path).name
        
        config_map_data.update({file_name:file_content})
        file.close()

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

    logging.info("---- Config Map Successfully Created ----")

    # ***********************
    # * Adding a Deployment *
    # ***********************
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
        mount_path='/code/src'
    )
    volume_mount_list.append(volume_mount1)

    # Container inside the inner spec of template
    containers = []
    container1 = client.V1Container(
        name='ms-container', 
        image=given_custom_image, 
        image_pull_policy='IfNotPresent',
        volume_mounts=volume_mount_list
    )
    containers.append(container1)

    # Volume Config Map Info
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

    # NOTE: wait until all the pods are in ready state    
    try:
        retry_check_pod_status(apps_v1, given_namespace_name)
    except:
        logging.info('---- Environment Failed to Initialize. Deleting Allocated Resources... ----')
        delete_k8_deployment(given_namespace_name)
        raise Exception

    logging.info('---- Deployment Successfully Created ----')

def delete_k8_deployment(given_namespace_name):
    # --- Deleting namespace at the end deletes all the related pods
    apps_v1 = client.CoreV1Api()
    apps_v1.delete_namespace(name=given_namespace_name)
    logging.info('---- Namespace Successfully Deleted ----')

@retry(
    wait=wait_fixed(2),
    stop=stop_after_attempt(10)
)
def retry_check_pod_status(apps_v1, given_namespace_name):
    # NOTE: Check if pods are in ready state
    logging.info('---- Waiting For Pods to be Prepared... ----')
    cnt = 0
    list_namespace_pod = apps_v1.list_namespaced_pod(given_namespace_name)
    if list_namespace_pod.items:
        for element in list_namespace_pod.items:
            pod_status = element.status.container_statuses[0]
            if pod_status.ready is True and pod_status.started is True:
                cnt += 1

        if cnt == len(list_namespace_pod.items):
            return

    raise Exception