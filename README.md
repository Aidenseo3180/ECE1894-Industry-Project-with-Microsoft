# Pytest-xdist-kubernetes

The pytest-xdist-plugin extends pytest-xdist with new kubernetes pod communication.
```bash
pytest {testfiles to run} -n {number of pods per deployment} --ktx='pod'
```
On top of the existing pytest-xdist library, various options have been added to support running pytest from kubernetes pods.
```bash
pytest --namespace='custom namspace' --custom_image='testfiles to run' -n {number of pods per deployment} --ktx='pod'
```
Logger is included as part of the functions added by the plugin. You can check the progress of the plugin by specifying:
```bash
--log-cli-level INFO
```

## How to install
In order to use the plugin, >= Python 3.9 is required. Can be installed with the following command:  
```bash
pip install pytest-xdist-kubernetes
```

## Reference
The plugin uses Kubernetes API to create/delete kubernetes pods.
https://github.com/kubernetes-client/python/blob/master/kubernetes/README.md