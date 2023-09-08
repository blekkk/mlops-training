# Kubernetes

1. Disable swap

    ```bash
    swapoff -a
    sudo sed -i '/ swap / s/^/#/' /etc/fstab
    ```

2. Set up Forwarding IPv4 and letting iptables see bridged traffic

    ```bash
    cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
    overlay
    br_netfilter
    EOF
    
    sudo modprobe overlay
    sudo modprobe br_netfilter
    
    # sysctl params required by setup, params persist across reboot
    
    cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
    net.bridge.bridge-nf-call-iptables  = 1
    net.bridge.bridge-nf-call-ip6tables = 1
    net.ipv4.ip_forward                 = 1
    EOF
    
    # Apply sysctl params without reboot
    
    sudo sysctl --system
    ```

3. Update system and install basic utilities for further installation

    ```bash
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl
    ```

4. Add the Kubernetes apt repository

    ```bash
    sudo mkdir -p /etc/apt/keyrings
    echo "deb [signed-by=/etc/apt/keyrings/kubernetes.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
    curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes.gpg
    ```

5. *Update* apt package index, *install* kubelet, kubeadm, kubectl and docker.io, and *pin* their version

    ```bash
    sudo apt-get update
    sudo apt-get install -y kubelet=1.25.11-00 kubeadm=1.25.11-00 kubectl=1.25.11-00 docker.io
    sudo apt-mark hold kubelet kubeadm kubectl docker.io
    ```

6. Set the cgroup driver for runc to systemd required for the kubelet

    ```bash
    sudo mkdir /etc/containerd
    sudo containerd config default > /etc/containerd/config.toml
    sed -i 's/ SystemdCgroup = false/ SystemdCgroup = true/'
    /etc/containerd/config.toml
    sudo systemctl restart containerd
    sudo systemctl restart kubelet
    ```

7. Initialize Cluster

    ```bash
    kubeadm config images pull
    kubeadm init --pod-network-cidr=192.168.0.0/16
    
    mkdir -p $HOME/.kube
    sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config
    ```

8. Setup Calico

    ```bash
    kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.1/manifests/tigera-operator.yaml
    kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.1/manifests/custom-resources.yaml
    ```

9. Taint nodes

    ```bash
    kubectl taint nodes --all node-role.kubernetes.io/control-plane-
    ```

## Reference(s)

[Kubernetes Cluster setup on Ubuntu 22.04 using kubeadm with Calico, By Sir Babar Zahoor](https://www.linkedin.com/pulse/kubernetes-cluster-setup-ubuntu-2204-using-kubeadm-calico-md-sajjad/)
