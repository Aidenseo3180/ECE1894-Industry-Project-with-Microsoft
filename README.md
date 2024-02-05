# ECE1894-Industry-Project-with-Microsoft

Microsoft project on PyPi for ECE1894 Industry project course in Spring 2024 at University of Pittsburgh.  

### Usage  
To build the docker image :  
```
docker build -t <name of image>:<tag> <location of dockerfile>
```
To download all the dependencies :  
```
poetry install
```
Passing namespace and custon image through pytest command :  
```
pytest --namespace=<namespace> --custom_image=<name of custom image>
```
Copying a file from a local storage to a pod :  
```
kubectl cp <location of the file> <Where in the pod you want it to be>
```
To execute the pytest from a pod :  
```
kubectl exec <name of a pod> -- pytest <location of the pytest file in pod>
```
### Reference
https://github.com/kubernetes-client/python/  