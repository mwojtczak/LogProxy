# LogProxy
LogProxy is a tool for extracting logs and forwarding them to [QRadar](https://www.ibm.com/security/security-intelligence/qradar). 

LogProxy provides REST API enabling wide usage across all types of platforms.

LogProxy is a dockerised service that can be deployed in a cloud using provided configuration.

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
curl -i -X POST -H "Content-Type: application/json"  -d '{"src_ip": "1.1.1.1", "dst_ip": "2.2.2.2", "url": "testurl", "timestamp": "1.12.2019"}' http://0.0.0.0:8080/add_log/
```
to get 200, OK http response.

Check your QRadar console to see the message logged.