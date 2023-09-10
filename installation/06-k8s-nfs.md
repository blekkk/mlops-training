## Dynamic Provisioning with Network File System (NFS)

1. Clone nfs-ganesha repository

    ```bash
    cd ~
    git clone https://github.com/ssalman172/nfs-ganesha-server-and-external-provisioner.git
    cd nfs-ganesha-server-and-external-provisioner
    ```

2. Build nfs-provisioner

    ```bash
    make build
    make container
    ```

3. Go to deploy/kubernetes directory

    ```bash
    cd deploy/kubernetes
    ```

4. Create the Deployment

    ```bash
    kubectl create -f deployment.yaml
    ```

5. Create the ClusterRole, ClusterRoleBinding, Role, and RoleBinding

    ```bash
    kubectl create -f rbac.yaml
    ```

6. Create the StorageClass

    ```bash
    kubectl create -f class.yaml
    ```

7. Set default storage class

    ```bash
    kubectl patch sc nfs-storageclass -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
    ```

## Static Provisioning (Local)

### Prepare Storage Class

1. We will be using local storage, create yaml file

    ```bash
    nano sc-local.yaml

    # Local storage class yaml template
    kind: StorageClass
    apiVersion: storage.k8s.io/v1
    metadata:
      name: sc-local
    provisioner: kubernetes.io/no-provisioner
    volumeBindingMode: WaitForFirstConsumer
    ############################################
    ```

2. After you create the yaml file

    ```bash
    kubectl create -f sc-local.yaml
    ```

3. Verify the storage class

    ```bash
    kubectl get sc -A
    ```

4. If your storage class is not a default storage class, then make it default

    ```bash
    # Please adjust "sc-local" to your storage class name
    kubectl patch sc sc-local -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
    ```

### Prepare Persistent Volumes

1. Create folder

    ```bash
    mkdir -p /mnt/disks/pv-mlops
    ```

2. Create persistent volume yaml

    ```bash
    nano pv-mlops.yaml
    # yaml file example, please adjust as you need
    apiVersion: v1
    kind: PersistentVolume
    metadata:
      name: pv-mlops
    spec:
      capacity:
        storage: 10Gi # PV Size, please adjust
      accessModes:
      - ReadWriteOnce
      persistentVolumeReclaimPolicy: Retain
      storageClassName: sc-local
      local:
        path: /mnt/disks/pv-mlops # Ensure this is exist or mkdir first, each PV use different folder
      nodeAffinity:
        required:
          nodeSelectorTerms:
          - matchExpressions:
            - key: kubernetes.io/hostname
              operator: In
              values:
              - worker-jtk-x # Kubernetes node name
    ```

3. After you create both PV yaml, run it with these commands

    ```bash
    # Execute for each yaml
    kubectl create -f pv-mlops.yaml
    ```

4. Verify the PV

    ```bash
    kubectl get pv -A
    ```
