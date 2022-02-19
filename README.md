# Deployment of DingoDB
[DingoDB](https://github.com/dingodb/dingo) is a real-time Hybrid Serving & Analytical Processing (HSAP) Database. It can execute high-frequency queries and upsert, interactive analysis, multi-dimensional analysis in extremely low latency. To achieve high concurrency and high throughput, DingoDB uses an elastic distributed deployment mode.
In order to simplify the deployment, this project introduces the deployment of DingoDB using [ansible](https://www.ansible.com/).

## 1. Typical Physical Topology

![Physical Topology about DingoDB](./refer/cluster_topology.png)

The roles in the cluster are mainly divided into:

- Coordinator

Coordinator act as the master of the cluster. It is responsible for the management and scheduler of data replications of DingoDB cluster.

- Executor

Executor act as the worker of the cluster. It is responsible for executing the physical execution plan of  SQL to scan and compute the data.

- Driver Proxy

DingoDB uses JDBC driver to perform table-level data operations, such as create, insert, update, delete, etc. Driver Proxy act as the proxy of JDBC Connection.


## 2. Installation prerequisites

- Version of OS

CentOS 7 or higher.

- Repository of Yum works fine

The repository will be used to install basic tools needed by the cluster, such as `python3`.

- Ansible Host

A host installed with `ansible` is required to  distribute cluster configuration and related software modules about DingoDB. This machine can also be replaced by one node in DingoDB cluster such as `Node-1`.

## 3. Deployment Guidelines

In the cluster mode, `ansible` is selected as the deployment tools. You can use this guide to install a DingoDB cluster.

### 3.1 Define the configuration about the Cluster

Edit the configuration `inventory/hosts`, use the real host, user, password to replace the item.

```cfg
[all:vars]
ansible_connection=ssh
ansible_ssh_user=root
ansible_ssh_pass=123456
ansible_python_interpreter=/usr/bin/python3

[coordinator]
172.20.3.13 
172.20.3.14
172.20.3.15

[executor]
172.20.3.15
172.20.3.16
172.20.3.17

[driver]
172.20.3.17

[all_nodes:children]
coordinator
executor
driver
```

### 3.2 Check Python3 is installed or not on DingoDB cluster

Check Python3 is installed or not on DingoDB cluster, if `Python3` is not installed, We can use ansible to install `Python3` using such command.

```shell
ansible all_nodes --become -m raw -a "yum install -y python3" -i ansible_hosts
```

### 3.3 Install the DingoDB cluster

- Copy artifacts 

```
1. artifacts/jdk-8u171-linux-x64.tar.gz
2. artifacts/dingo.zip
```

- Executor ansible script

```shell
 ansible-playbook playbook.yml
```

### 3.4 Install Steps about DingoDB

You can follow this guide to install a dingo cluster:

[![asciicast](https://asciinema.org/a/4INSgMgv1q7gW5NZrpIGVJWVt.svg)](https://asciinema.org/a/4INSgMgv1q7gW5NZrpIGVJWVt)