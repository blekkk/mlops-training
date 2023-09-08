# K8S Storage Class and Volumes

## Dynamic Provisioning with Network File System (NFS)

1. Clone nfs-ganesha repository

    ```bash
    git clone https://github.com/kubernetes-sigs/nfs-ganesha-server-and-external-provisioner.git
    cd nfs-ganesha-server-and-external-provisioner
    ```

2. Verify Dockerfile, need some adjustment on current version (08/2023)

    ```bash
    nano Dockerfile
    ## modify 
    # ARG binary=nfs-provisioner
    ## to
    # ARG binary=bin/nfs-provisioner
    ```

3. Build nfs-provisioner

    ```bash
    make build
    make container
    ```

4. Go to deploy/kubernetes directory

    ```bash
    cd deploy/kubernetes
    ```

5. Create the Deployment

    ```bash
    # modify NFS provisioner name
    nano deployment.yaml
    # find args section and change provisioner to nfs-provisioner
    ...
    args:
      - "-provisioner=nfs-provisioner"
    ...
    
    # Create deployment
    kubectl create -f deployment.yaml
    ```

6. Create the ClusterRole, ClusterRoleBinding, Role, and RoleBinding

    ```bash
    kubectl create -f rbac.yaml
    ```

7. Create the StorageClass

    ```bash
    # modify the storage class name to nfs-storageclass
    nano class.yaml
    # also change provisioner name to nfs-provisioner
    ...
    metadata:
      name: nfs-storageclass
    provisioner: nfs-provisioner
    ...
    
    # Create StorageClass
    kubectl create -f class.yaml
    ```

8. Test and verify

    ```bash
    # Modify claim.yaml if you change the storage class name
    nano claim.yaml
    ...
    metadata:
      name: nfs-pvc
    spec:
      storageClassName: nfs-storageclass
    ...
    
    # Create Persistent Volume Claim
    kubectl create claim.yaml
    
    # Ensure that you have a new persistent volume created automatically
    kubectl get pv
    ```

9. Set default storage class

    ```bash
    # Check existing storage class
    kubectl get sc
    
    ## If you have a default storage class
    # set false current default sc first
    kubectl patch sc old-default-sc-local -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'
    
    ## Can go here immediately if you don't have any
    # set new default sc
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

0. Create folder

    ```bash
    mkdir -p /mnt/disks/pv-mlops
    ```

1. Create persistent volume yaml

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

2. After you create both PV yaml, run it with these commands

    ```bash
    # Execute for each yaml
    kubectl create -f pv-mlops.yaml
    ```

3. Verify the PV

    ```bash
    kubectl get pv -A
    ```
