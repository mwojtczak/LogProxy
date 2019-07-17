# LogProxy
LogProxy is a tool that analyses incoming requests of web applications and logs selected data to [QRadar](https://www.ibm.com/security/security-intelligence/qradar). 

LogProxy provides REST API enabling wide usage across all types of platforms.

LogProxy is a dockerized service that can be deployed in a cloud using a provided configuration.

## Architecture
LogProxy consists of two main components: LogCollector and LogProxy.

LogCollector is a Flask library that provides a decorator for extracting source IP address of incoming connections. Each IP address is then formatted as a log entry and passed to LogProxy using HTTP protocol.

LogProxy is a dockerized application that connects to a private network of corresponding QRadar instance and forwards received logs to its TCP server.
![Architecture overview](LogProxyArchitecture.jpg?raw=true "Architecture overview")

## Test it locally
To run LogProxy locally you need to install docker.

Enter LogProxy directory and update *vpn.conf* file with vpn credentials.

Build docker image:
```bash
docker build -t logproxy:latest .
```
and then run docker with your QRadar IP addess as QRADAR_IP parameter:
```bash
docker run -p 8080:8080 -p 514:514 -i -e PYTHONUNBUFFERED=0  -e QRADAR_IP=<ip_address> --cap-add NET_ADMIN  logproxy
```
You should see message:
```
* Running on http://0.0.0.0:8080/
```
ensuring HTTP server started running. Test the server using REST API e.g. with *curl* command:
```bash
curl -i -X POST -H "Content-Type: application/json"  -d '{"log": "LOGPROXY:: src_ip=10.10.10.10 url=http://20.20.20.20/home/ timestamp=1560189227"}' http://0.0.0.0:8080/add_log/
```
to get 201, Created http response.

Add log source in QRadar panel for your LogProxy instance.
Check your QRadar console to see the message logged.


## Deploy it in the cloud
LogProxy is an application running in a docker, making it easy to deploy in the cloud with provided configuration files.

We assume you already have a container named logproxy deployed.

Login to your IBM account:
```bash
ibmcloud login -a cloud.ibm.com
```
Create namespace for your app:
```bash
ibmcloud cr namespace-add logproxy
```
Login to region of your cluster:
```bash
ibmcloud cs region-set <region_url>
```
Create docker image of logproxy and push to remote repository in cloud:
```bash
docker build -t <image_name> .
docker tag <image_name> <region_url>/<namespace>/<image_name>:<tag>
docker push <region_url>/<namespace>/<image_name>:<tag>
```

Set the context for your cluster by copying output of command:
```bash
 ibmcloud cs cluster-config logproxy
```

Update QRADAR_IP environment variable in deployment/deployment.yaml file.
Create the deployment resource:
```bash
kubectl create -f deployment/deployment.yaml
```
Create the service resource:
```bash
kubectl create -f deployment/service.yaml
```

Ensure that service is running by visiting http://container_public_ip:service_port_no/.

Now you need to configure QRadar by adding LogSource in Admin tab. To get IP address of vpn interface in docker,
run command:
```bash
kubectl exec -it <pod_name>  -- ifconfig
```

After QRadar LogSource is configured, see Log Activity tab and observe the logs incoming.

## Test LogCollector

To see how to use LogCollector in Flask application, run examples/flask_example.py with LogProxy IP address and port number:
```bash
python3.6 examples/flask_example.py LOG_PROXY_IP  LOG_PROXY_PORT
```
and visit 0.0.0.0:5000/ or 0.0.0.0:5000/test.
See QRadar LogActivity tab to ensure there are logs providing information of your activity.

You can use LogCollector the same way in your Flask application. 
