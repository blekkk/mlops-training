# Join as worker node

## On Master Node

Create token for worker

```bash
kubeadm token create --print-join-command
```

Make a note of the kubeadm join command to be used in worker node

## On Worker Node

Use this command on the worker node to join the Kubernetes cluster. Please adjust the ip address or hostname, token and discovery token given by the `kubeadm join command`.

```bash
kubeadm join x.x.x.x:6443 --token xxxxx --discovery-token-ca-cet-hash sha256:xxxxx
```
