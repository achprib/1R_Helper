![image-20240521160729800](.\images\dev_cover.png)

<div align="right"><span style="color:red; font-style:Italic;font-weight:bold;font-size:25px;">ONE Record Project</span></div>
<div align="right" style="font-weight:bold;">ONE Record部署指南</div>

<div align="right">Version 1.0.1</div>

<div align="right">2024-07-08</div>







<div align="right" style="font-size:8pt">IATA 1RLL项目组编制</div>

<div align="center" style="font-size:8pt">@International Aviation Transport Association</div>

<div style="page-break-after: always;"></div>

## 目录

[TOC]

<div style="page-break-after: always;"></div>

## 1 简介

ONE Record 是航空货物数据分享的标准，旨在创建一个单一的货物记录。为了能通过标准且安全的 Web API 分享数据，ONE Record 确定了一个通用模型。通过 ONE Record，航空公司、托运人、货运代理、地面服务代理和供应链中的所有其他实体可进行自由的实时交互，传输内容丰富的数据，并获得即时通知和确认。ONE Record 的目标是推进航空物流业务转型，而这种转型可能给那些主要建立在既有老旧系统之上且依赖纸质流程的航空物流业务带来翻天覆地的变化。

本文档用于指导基于ONE Record标准的NE:ONE项目的快速部署，主要面向项目开发人员、测试人员，以及对本项目感兴趣的其他人员。

本文档主要包含以下部分内容：

- 服务器准备
- ONE Record 部署

<div style="page-break-after: always;"></div>

## 2 开始之前

开始之前，请准备好以下开发环境。

###  2.1 环境依赖
#### 2.1.1 软件环境

本手册基于Windows 10 环境进行编写，具体软件环境清单如下：

<div style="text-align: center">表1 软件清单</div>

| 名称 | 版本 | 说明                                                     |
| ---- | ---- |----------------------------------------------------------------------------|
| ONE Record服务器    | NE:ONE latest version | 采用NE:ONE最新的链接。 |
|    docker desktop  |   4.22.0  | 必需。<br/> |
|Postman      | 11.3.2 | 必需。<br/>下载链接为:[Download Get Started for Free](https://www.postman.com/downloads/) |
| AWS CLI |      | 用于链接AWSS3服务（非必需）。<br/>参考文档为：[配置AWS CLI - AWS Command Line Interface](https://docs.aws.amazon.com/zh_cn/cli/latest/userguide/cli-chap-configure.html) |
| GragphDB（docker） | 10.4.0 | 用于数据持久化（非必需）。<br/>采用项目src/main/docker-compose目录下的docker-compose.graphdb-server.yml及<br/>docker-compose.graphdb.yml创建 |
| keycloak （docker） | 22.0.5 | 必需.用于鉴权<br/>采用项目 src/main/docker-compose目录下的docker-compose.keycloak.yml文件创建 |

<div STYLE="page-break-after: always;"></div>

#### 2.1.2 硬件环境
硬件环境清单如下：


<div style="text-align: center">表2 硬件清单</div>

| 名称 | 参数 | 说明     |
| ------------------------ | ------------------------ | ---------------------------- |
| CPU                      | 2.6G Hz或更高            |            |
| 内存                     | 8G及以上                 |            |
| 硬盘                     | 50G以上                  |            |

#### 2.1.3 网络环境

确保能正常访问 Internet

<div style="page-break-after: always;"></div>

###  2.2 获取配置文件
#### 2.2.1 Docker Compose 文件

[NE:ONE项目的源代码](https://git.openlogisticsfoundation.org/wg-digitalaircargo/ne-one) 提供了Docker Compose文件，以及配置信息。

<img src="images/deploy_download.png" style="zoom: 53%;" />

<div style="text-align: center">图1 NE:ONE项目源码</div>

在下载的源码目录 \src\main\docker-compose\下，如图：

<img src="images/deploy_comps.png" style="zoom: 63%;" />

<div style="text-align: center">图2 Docker Compose文件</div>


具体清单如下：
<div style="text-align: center">表3 Docker Compose文件清单</div>

| Compose文件                       | 用途                                                         | 环境文件                |
| --------------------------------- | ------------------------------------------------------------ | ----------------------- |
| docker-compose.graphdb.yml        | 启用GraphDB持久化，可以与 docker-compose.graphdb-server.yml 一起使<br/>用 | graph-db.env            |
| docker-compose.graphdb-server.yml | 启动 GraphDB 实例                                            | 无                      |
| docker-compose.mtls.yml           | 启动服务器并在端口 8443上启用 TLS                            | tls.env                 |
| docker-compose.tls.yml            | 在端口 8443 上启用 mTLS（和 TLS）的情况下启动服务器。不得与 docker-compose.tls.yml 一起使用。 | tls.env ，<br/>mtls.env |


#### 2.2.2 环境变量配置文件

Docker Compose文件要配合环境变量配置文件一起使用，在项目目录 \src\main\docker-compose\ 下。

<div style="text-align: center">表4 Docker Compose环境配置文件</div>

| 环境配置文件                 | 目的                                         |
| ----------------------------------- | --------------------------------- |
| lo-id.env       | 1R服务器环境配置，含对外主机名、对外访问模式、对外端口、访问路径   |
| minio.env       | 配置minio作为S3兼容服务器，支持Blob存储                         |
| mtls.env        | 配置mtls安全策略   |
| tls.env         | 配置tls安全策略 |
| in-memory.env   | 配置内存存储模式   |
| graph-db.env    | 配置GraphDB持久存储   |

<div style="page-break-after: always;"></div>

## 3 Docker 部署安装

​    这里提供两种基于Docker的部署方式，

- 基于Docker compose文件启动
- 基于Docker直接启动 


### 3.1 基于 Docker Compose 文件部署
NE:ONE项目提供了Docker Compose文件，以支持个性化的部署需求。

#### 3.1.1 下载源代码
通过链接：[WG-DigitalAirCargo / NE-ONE · GitLab](https://git.openlogisticsfoundation.org/wg-digitalaircargo/ne-one) 下载源代码。

#### 3.1.2 启动Keycloak

启动keycloak进行身份验证

```shell script
docker compose -f docker-compose.keycloak.yml up -d
```

#### 3.1.3 配置参数

##### 3.1.3.1 配置环境参数

根据具体需求配置 .env中的相应参数，请查阅 附录A。

##### 3.1.3.2 配置compose.yml参数

在docker-compose.yml文件中添加如下环境变量。

```shell
environment:
  - QUARKUS_REDIS_HOSTS=redis://localhost:6379
  - AUTH_VALID_ISSUERS_LOCAL=http://<1r_server_ip>:8989/realms/neone
  - AUTH_ISSUERS_LOCAL_PUBLICKEY_LOCATION=http://<1r_server_ip>:8989/realms/neone/protocol/openid-connect/certs
  - QUARKUS_OIDC_CLIENT_AUTH_SERVER_URL=http://<1r_server_ip>:8989/realms/neone
```

如需要与其他利益相关方服务器进行订阅通知，需要添加相关方的neone realm端点和公钥位置端点，以此来信任彼此的token。

```shell
  - AUTH_VALID_ISSUERS_LOCAL2=http://<1r_server_ip2>:8989/realms/neone
  - AUTH_ISSUERS_LOCAL2_PUBLICKEY_LOCATION=http://<1r_server_ip2>:8989/realms/neone/protocol/openid-connect/certs
  - AUTH_VALID_ISSUERS_LOCAL3=http://<1r_server_ip3>:8989/realms/neone
  - AUTH_ISSUERS_LOCAL3_PUBLICKEY_LOCATION=http://<1r_server_ip3>:8989/realms/neone/protocol/openid-connect/certs
```

#### 3.1.4 快速启动ONE Record服务器

根据业务需求，参考以下命令，拉取镜像并在docker中启动相应的服务:

**方案1： 以最小方式启动NE:ONE** 

```shell script
docker compose -f docker-compose.yml up -d
```

**方案2： 启用GraphDB和NE:ONE服务器**

```shell script
docker compose -f docker-compose.yml -f docker-compose.graphdb.yml -f docker-compose.graphdb-server.yml up -d
```

**方案3： 启用TLS和NE:ONE服务器**

```shell script
docker compose -f docker-compose.yml -f docker-compose.tls.yml -f docker-compose.mockserver.yml up -d
```

> **NOTE:**
>
> 1. 使用的证书包含在存储库中，但证书主题为 localhost。
> 2. tls.env 文件更改物流对象 ID 的配置以指向服务器的 TLS 端口和方案。
> 3. 使用您自己的证书时，必须调整 tls.env 文件和 docker-compose.tls.yml 文件以指向正确的证书文件并包含正确的密码。

**方案4： 启用GraphDB, TLS 和 NE:ONE服务器**

```shell script
docker compose -f docker-compose.yml -f docker-compose.tls.yml -f docker-compose.graphdb.yml  -f docker-compose.graphdb-server.yml -f docker-compose.mockserver.yml up -d
```

**方案5：启用mTLS 和 NE:ONE服务器**

```shell script
docker compose -f docker-compose.yml -f docker-compose.mtls.yml up -d
```

> **NOTE:**
>
> 1. mTLS 配置包括 TLS 配置，因为 mTLS 是 TLS 的补充。
> 2. 至于 mTLS，包含的配置使用位于此存储库中的证书。 《NE:ONE开发者手册》配置部分描述了如何使用您自己的证书。
> 3. 使用您自己的证书时，必须调整 tls.env 、 mtls.env 文件和 docker-compose.tls.yml 文件以指向正确的证书文件并包含正确的密码。


#### 3.1.5 访问服务器

打开Postman，发起GET http://<1r_server_ip>:8080 以访问服务器信息。如下图：

<img src="images/deploy_pm_serverinfo.png" style="zoom: 83%;" />

<div style="text-align: center">图3 NE:ONE 服务器信息</div>

部署成功！

> **Note**:
>
> <1r_server_ip>替换见附录B

<div style="page-break-after: always;"></div>

### 3.2 基于Docker直接部署

#### 3.2.1 配置参数

NE:ONE服务器信息端使用 application.properties 中配置的值填充,默认值是：

```shell script
neone-server.supported-content-types[0]=application/ld+json
neone-server.supported-content-types[1]=application/turtle
neone-server.supported-content-types[2]=text/turtle
neone-server.supported-languages[0]=${default-language}
neone-server.data-holder.name=ACME Corporation
neone-server.data-holder.id=_data-holder
```

> **NOTE:** 
>
> 1. neone-server.data-holder.id 定义数据所有者 LogisticsObject 的 URI，默认为 _data-holder。因此根据默认配置，可以使用 URI
>    http://localhost:8080/logistics-objects/_data_holder
> 2. NE:ONE 服务器的配置遵循默认的 Quarkus 配置，请参阅 Quarkus 配置指南。相关配置和默认值位于
>    src/main/resources/application.conf 文件中。 


<div style="page-break-after: always;"></div>

#### 3.2.2 启动NEONE服务器

使用以下命令启动Docker 容器：

```shell script
docker run -d --network docker-compose_default --name neone -p 8080:8080 
-e QUARKUS_REDIS_HOSTS=redis://localhost:6379 
-e AUTH_VALID_ISSUERS_LOCAL=http://<1r_server_ip>:8989/realms/neone  
-e AUTH_ISSUERS_LOCAL_PUBLICKEY_LOCATION=http://<1r_server_ip>:8989/realms/neone/protocol/openid-connect/certs 
-e QUARKUS_OIDC_CLIENT_AUTH_SERVER_URL=http://<1r_server_ip>:8989/realms/neone git.openlogisticsfoundation.org:5050/wg-digitalaircargo/ne-one:latest
```

> **NOTE:** 
>
> 1. latest 标记始终指向最新的发行版本。
>
> 2. 默认采用in-memory存储方式。 
>
> 3. 如需要与其他利益相关方服务器进行订阅通知，需要添加相关方的neone realm端点和公钥位置端点，以此来信任彼此的token。
>
>    ```shell
>    -e AUTH_VALID_ISSUERS_LOCAL2=http://<1r_server_ip2>:8989/realms/neone  
>    -e AUTH_ISSUERS_LOCAL2_PUBLICKEY_LOCATION=http://<1r_server_ip2>:8989/realms/neone/protocol/openid-connect/certs 
>    -e AUTH_VALID_ISSUERS_LOCAL3=http://<1r_server_ip3>:8989/realms/neone  
>    -e AUTH_ISSUERS_LOCAL3_PUBLICKEY_LOCATION=http://<1r_server_ip3>:8989/realms/neone/protocol/openid-connect/certs 
>    ```

<div style="page-break-after: always;"></div>

#### 3.2.3 访问服务器

打开Postman，发起GET http://<1r_server_ip>:8080 以访问服务器信息。如下图：

<img src="images/deploy_pm_serverinfo.png" style="zoom: 83%;" />

<div style="text-align: center">图4 NE:ONE 服务器信息</div>

部署成功！

> **Note**:
>
> <1r_server_ip>替换见附录B

<div style="page-break-after: always;"></div>

## 附录

### 附录A 配置 .env 文件

默认配置在 .env 文件中提供，并设置为本地部署配置服务器。为了配置服务器以进行外部访问，至少必须将 lo-id.env 文件调整为外部访问可用的主机和端口配置

<div style="text-align: center">表5 环境变量配置描述</div>

| 环境变量               | 描述                                                         |
| ---------------------- | ------------------------------------------------------------ |
| LO_ID_CONFIG_HOST      | 服务器的外部主机名                                           |
| LO_ID_CONFIG_SCHEME    | 主机的协议，http 或 https                                    |
| LO_ID_CONFIG_PORT      | 服务器外部接口                                               |
| LO_ID_CONFIG_ROOT_PATH | 如果存在反向代理，则使用与NE：ONE服务器（可选）不同的根路径为端点提供服务 |

这些配置属性用于构建NE:ONE服务器中所有外部可解析实体的基础，因此基础URL的格式为：<LO_ID_CONFIG_SCHEME>://<LO_ID_CONFIG_HOST>[:<LO_ID_CONFIG_PORT>]/[<LO_ID_CONFIG_ROOT_PATH>/]

### 附录B 配置1R服务器地址

<div style="text-align: center">表6 配置1R服务器地址</div>

| Name          | Example                                                      |
| ------------- | :----------------------------------------------------------- |
| 1r_server_ip  | - localhost(本地部署)<br />- 服务器的 IP 地址，如：192.168.1.123 |
| 1r_server_ip2 | - 相关方服务器的IP地址                                       |
| 1r_server_ip3 | - 相关方服务器的IP地址                                       |





<div style="page-break-after: always;"></div>