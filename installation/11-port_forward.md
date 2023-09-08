# Systemd services port forwarding
To forward some application ports, instead of using `nohup`, you can create systemd services. This way, the services will restart automatically upon exit.

Config:

Create a file `/etc/systemd/system/<YOUR_SERVICE>.service` at type

```bash
[Unit]
Description=<DESCRIPTION>
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=1
User=root
ExecStart=<COMMANDS>

[Install]
WantedBy=multi-user.target
```

Then start the service and enable at startup.

```bash
systemctl start <service>
systemctl enable <service>
```

**List of services**

| Service Name | Commands | Description |
| --- | --- | --- |
| rabbitmq-api-port | kubectl port-forward service/rabbitmq-basic 5672:5672 --address=0.0.0.0 | Rabbitmq port forward service for API |
| rabbitmq-ui-port | kubectl port-forward service/rabbitmq-basic 15672:15672 --address=0.0.0.0 | Rabbitmq port forward service for UI |
| kubeflow-port | kubectl port-forward svc/istio-ingressgateway -n istio-system 8087:80 --address=0.0.0.0 | Kubeflow port-forwarding service |
| label-studio-port | kubectl port-forward service/label-studio-ls-app 8080:80 --address=0.0.0.0 | Label-studio port-forwarding service |

Use these command if you want to stop a service.

```bash
systemctl stop <service>
systemctl disable <service>
```