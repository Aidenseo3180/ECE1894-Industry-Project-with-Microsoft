# ECE1894-Industry-Project-with-Microsoft  
Microsoft project on PyPi for ECE1894 Industry project course in Spring 2024 at University of Pittsburgh.  
  
### Usage  
How to set up the k3d cluster environment for pytest :  
First, build the docker image  
```
docker build -t {name of image}:{tag} {location of dockerfile}
```
Then, import the docker image from the docker registry to the k3d cluster  
```
k3d image import {name of image} -c {name of existing cluster}
```
Finally, give namespace and custon image to run the pytest  
```
pytest --log-cli-level {info level} --namespace={namespace} --custom_image={name of custom image} {location of the test file}
```
  
Copying a file from a local storage to a pod :  
```
kubectl cp {location of the file>} {Where in the pod you want it to be}
```
To execute the pytest that pod contains :  
```
kubectl exec {name of a pod} -- pytest {location of the pytest file in pod}
```
### Reference
https://github.com/kubernetes-client/python/blob/master/kubernetes/README.md