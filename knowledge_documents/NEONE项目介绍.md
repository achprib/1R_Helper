# NE:ONE - opeN sourcE： ONE Record服务器软件

NE:ONE是由德国联邦数字和运输部资助的研究项目Digital Testbed Air Cargo（DTAC）发起的一项倡议。https://www.linkedin.com/company/digitales-testfeld-air-cargo-dtac/

它的目标是提供开源和免费使用的ONE Record服务器软件包，帮助您实施IATA ONE Record标准，这是航空货运及其他领域的新数据共享标准。NE:ONE完全符合IATA ONE Record的API描述（v2.0）和数据模型（v3.0.0），以帮助您开始使用ONE Record。

要了解有关 ONE Record 的更多信息，请查看 IATA GitHub：

- 当前 API 描述，包括如何查询（例如 POST、GET、PATCH）任何 ONE Record服务器，包括 NE:ONE：
      https://iata-cargo.github.io/ONE-Record
- 当前数据模型：
      https://github.com/IATA-Cargo/ONE-Record/tree/api_2.0.0-dev/working_draft/API

虽然NE:ONE目前正在通过DTAC内部的公共资金进行开发，但它应该由航空货运界及其他领域的参与者共同使用和维护。让我们一起将数字航空货运推向一个新的水平！

有关NE:ONE、DTAC和OLF工作组工作的更多信息，您可以联系 oliver.ditz@iml.fraunhofer.de

现在NE:ONE软件包是基于[CARGO ontology Version 3.0.0](https://github.com/IATA-Cargo/ONE-Record/blob/master/2023-12-standard/Data-Model/IATA-1R-DM-Ontology.ttl) 和 [API ontology 2.0.0-dev](https://github.com/IATA-Cargo/ONE-Record/blob/master/working_draft/API/ONE-Record-API-Ontology.ttl)

[TOC]

## 开始
- 从安装开始，请参阅章节 [安装]（#installation）。
- 基于NE:ONE开发，可以查看[NE:ONE开发 - 入门]（#neone-development-getting-started）一章。
- 如果想开始配置自己的NE:ONE服务器，例如设置通知，您可以查看[配置]（#configuration）。

## 安装

### 使用Docker

NE:ONE项目发布包含NE:ONE服务器的docker容器。
从 [Gitlab 容器注册表](https://git.openlogisticsfoundation.org/wg-digitalaircargo/ne-one/container_registry) 可访问已发布的容器。
名为“ne-one-mtls”的映像配置了强制 mTLS 访问。

可以使用以下命令作为普通Docker容器启动NE:ONE服务器：

```shell script
docker run -d --name neone \
    -p 8080:8080 \
    git.openlogisticsfoundation.org:5050/wg-digitalaircargo/ne-one:latest
```

“latest”标记始终指向最新版本。使用标签“dev”表示最新开发版本。

这将使用**内存存储库**启动NE:ONE服务器的最小实例。

在“application.properties”中配置服务器端的信息，默认值为：

```properties
neone-server.supported-content-types[0]=application/ld+json
neone-server.supported-content-types[1]=application/turtle
neone-server.supported-content-types[2]=text/turtle
neone-server.supported-languages[0]=${default-language}
neone-server.supported-logistics-object-types[0]=https://onerecord.iata.org/ns/cargo#Piece
neone-server.supported-logistics-object-types[1]=https://onerecord.iata.org/ns/cargo#Waybill
neone-server.supported-logistics-object-types[2]=https://onerecord.iata.org/ns/cargo#Shipment
neone-server.data-holder.name=ACME Corporation
neone-server.data-holder.id=_data-holder
```

“neone-server.data-holder.id”定义“LogisticsObject”数据持有者的URI，默认为“_data-holder”，因此根据默认配置，可以使用 URI 检索对象
“http://localhost:8080/logistics-objects/_data_holder”。

NE:ONE服务器的配置遵循默认的Quarkus配置可能性。请参考
[Quarkus配置指南](https://quarkus.io/guides/config-reference) 。可能的配置和默认值包括
位于“src/main/resources/application.conf”文件中。

还有一个启用了 mTLS 的 docker 映像，名为
“git.openlogisticsfoundation.org:5050/wg-digitalaircargo/ne-one/ne-one-mtls”，具有与非 mTLS 版本相同的标记。
若要使用此版本，建议使用 docker compose 方法启动服务器。

若要访问NE:ONE服务器提供的服务，需要JWT令牌。另请参阅有关
[keycloak设置](#starting-keycloak-for-authentication)。
默认情况下，一个有效的令牌发行者配置的URL为http://localhost:8989/realms/neone， 
且对应的JWKS端点为 http://localhost:8989/realms/neone/protocol/openid-connect/certs 

添加其他有效发行者要依据下面的格式：
```properties
auth.valid-issuers.<ISSUER_KEY>=<ISSUER_URL>
auth.issuers.<ISSUER_KEY>.publickey.location=<PUBLIC_KEY_LOCATION>
```

必须通过不同的 Quarkus 配置机制（属性文件、Java 系统属性、环境变量等）。

'<PUBLIC_KEY_LOCATION>' 可以是 JWKS URL、字符串形式的公钥，也可以指向包含PEM 格式的公钥文件。

> **_NOTE：_** 要禁用从提供的 JWT 中检索“one-record-ìd”，请设置“disable.access.subject”
> 属性设置为“true”。执行此操作时，将使用访问主体的固定值，并将该值设置为数据持有者服务器的。这不会禁用 ACL 授权，无论如何都需要创建 ACL。
> 详情请查阅 [授权 API](#authorization-api)。

### Docker Compose

NE:ONE项目包含几个Docker Compose文件，可用于在不同的环境中启动服务器配置。
Docker Compose 文件位于源存储库的“src/main/docker-compose”文件夹中。

以最小配置启动NE:ONE服务器（不含持久存储）如下：

```shell script
docker compose up -d
```

这将启动NE:ONE服务器，并将内部端口“8080”映射到主机端口“8080”。

默认配置在“.env”文件中提供，并设置为为本地部署配置服务器。
若要从外部也能访问服务器，至少要配置“lo-id.env”文件中的主机和端口配置。

| 环境变量               | 描述                                                         |
| ---------------------- | ------------------------------------------------------------ |
| LO_ID_CONFIG_HOST      | 服务器的外部主机名                                           |
| LO_ID_CONFIG_SCHEME    | 主机的方案，'http' 或 'https'                                |
| LO_ID_CONFIG_PORT      | 服务器的外部端口                                             |
| LO_ID_CONFIG_ROOT_PATH | 如果存在反向代理，则使用与 NE:ONE 服务器不同的根路径（可选）为端点提供服务，则默认 '/' |

这些配置属性用于构建NE:ONE服务器最基本的外部实体，因此基本 URL 的格式为：
<LO_ID_CONFIG_SCHEME>://<LO_ID_CONFIG_HOST>[:<LO_ID_CONFIG_PORT>/[<LO_ID_CONFIG_ROOT_PATH>/]

当NE:ONE服务器调用外部服务进行通知和订阅时，请在“client.env”配置。
若使用默认配置，NE:ONE服务器需要一个模拟服务器，并与NE:ONE运行在同一网络中，以处理订阅请求和通知。

以下清单列举出了启用GraphDB持久存储、TLS 和 mTLS 的Docker compose文件。

| Docker Compose 文件                 | 目的                                                         | 环境文件               |
| ----------------------------------- | ------------------------------------------------------------ | ---------------------- |
| docker-compose.graphdb.yml       | 启用 GraphDB 持久化，可与 'docker-compose.graphdb-server.yml' 一起使用 | graph-db.env          |
| docker-compose.graphdb-server.yml | 启动 GraphDB 实例                                            | 无                     |
| docker-compose.tls.yml            | 在端口 8443 上启用 TLS 的情况下启动服务器                    | tls.env   |
| docker-compose.mtls.yml           | 在端口 8443 上启用 mTLS（和 TLS）的情况下启动服务器。**不得与“docker-compose.tls.yml”一起使用**。 | tls.env， mtls.env |

#### 启用 GraphDB 持久化

使用以下 Docker Compose 命令，以启用含有 GraphDB 持久性存储的服务器。

```shell script
docker compose -f docker-compose.yml -f docker-compose.graphdb.yml -f docker-compose.graphdb-server.yml up -d
```

#### 启用 TLS

启用 TLS 时，使用的证书包含在存储库中，但证书使用者为“localhost”。
请参阅 [mTLS 配置部分](accessing-the-server-using-mtls) 以逐步创建证书。

“tls.env”文件更改了物流对象 ID 的配置以指向服务器的TLS端口和模式。

> **_NOTE：_** 使用您自己的证书时，“tls.env”文件和“docker-compose.tls.yml”文件必须
> 调整为指向正确的证书文件并包含正确的密码。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    

```shell script
docker compose -f docker-compose.yml -f docker-compose.tls.yml up -d
```

#### 启用 mTLS

mTLS 配置包括 TLS 配置，因为 mTLS 是 TLS 的补充。至于mTLS，其包含的配置
是位于此存储库中的证书。这[mTLS配置部分](accessing-the-server-using-mtls) 介绍如何使用自己的证书。

> **_NOTE：_** 使用自己的证书时，“tls.env”、“mtls.env”文件和“docker-compose.tls.yml”文件
> 必须进行调整，以指向正确的证书文件并包含正确的密码。

```shell script
docker compose -f docker-compose.yml -f docker-compose.mtls.yml up -d
```

#### 启动用于订阅和通知的模拟服务器

```shell script
docker compose -f docker-compose.mockserver.yml up -d
```

这也可以与其他 Docker Compose 文件结合使用，参见 [组合配置](combining-configurations)。
启动的模拟服务器还公开了一个仪表板，可以在其中查看期望和请求。
访问仪表板，链接为：[http://localhost:1080/mockserver/dashboard](http://localhost:1080/mockserver/dashboard)

#### 启动Keycloak进行身份验证

NE:ONE服务器使用JWT令牌保护其资源。采用Docker Compose文件来启动Keycloak。由于NE:ONE服务器实现了ONE Record规范，因此它支持
不同的标识提供者提供的JWT。因此，该项目提供了两个 Docker compose文件，用于启动两个独立的 Keycloak实例。可以使用以下命令启动：

*Keycloak实例1*：

|              |                                                              |
| ------------ | ------------------------------------------------------------ |
| **网址**     | http://localhost:8989                                        |
| **用户名**   | admin                                                    |
| **密码**     | admin                                                     |
| **令牌 URL** | http://localhost:8989/realms/neone/protocol/openid-connect/token |


此外，该实例有一个预置的用户通过Blob API来下载文件。

|              |                                                              |
| ------------ | ------------------------------------------------------------ |
| **User Name**     | neone-viewer                                        |
| **Password**   | viewer                                                    |

```shell script
docker compose -f docker-compose.keycloak.yml up -d
```

*Keycloak实例2*：

|              |                                                              |
| ------------ | ------------------------------------------------------------ |
| **网址**     | http://localhost:8990                                        |
| **用户名**   | admin                                                     |
| **密码**     | admin                                                     |
| **令牌 URL** | http://localhost:8990/realms/neone/protocol/openid-connect/token |

```shell script
docker compose -f docker-compose.keycloak-2.yml up -d
```

这两个实例都配置了一个名为“neone”的realm。此外，还为预配置 ID 为“neone-client”和密码“lx7ThS5aYggdsMm42BP3wMrVqKm9WpNY”的客户端。

这两个实例都配置为颁发令牌，包括 ONE Record 自定义声明“logistics_agent_uri”。
实例1的值是“http://localhost:8080/logistics-objects/_data-holder”，
实例2的值是“http://external/logistics-objects/_data-holder”。

#### 启动 Minio 作为 S3 兼容服务

NE:ONE 服务器将 blob 存储在任何 Amazon S3 兼容的存储提供程序中。
为了简单起见，提供了Docker Compose 文件来启动 [Minio 服务器](https://minio.io)。
看[组合配置](#combinig-configurations)介绍如何使用 Docker Compose将Minio服务器与NE:ONE服务器一起启动


当 NE:ONE 服务器作为独立的 docker 容器运行时，请配置网络以包含 Minio 服务器。
最简单的方法是设置“QUARKUS_S3_ENDPOINT_OVERRIDE”环境变量为“http://host.docker.internal:9000”，
而且，在Linux上运行docker时，在启动NE:ONE服务器的docker 命令中加入 --add-host=host.docker.internal:host-gateway。
例如：
```shell
docker run -d --name neone \
  -p 8080:8080 \
  --add-host=host.docker.internal:host-gateway \
  -e "QUARKUS_S3_ENDPOINT_OVERRIDE=http://host.docker.internal:9000" \
  git.openlogisticsfoundation.org:5050/digital-air-cargo/ne-one:dev`
```

另外，启动 Minio 服务器，可以使用 Docker Compose 文件

```shell script
docker compose -f docker-compose.minio.yml up -d
```

或者使用 docker 命令启动 Minio 服务器

```shell
docker run -d \
  -p 9000:9000  -p 9090:9090 \
  --name minio \
  -e "MINIO_ROOT_USER=admin" \
  -e "MINIO_ROOT_PASSWORD=admin123" \
  quay.io/minio/minio server /data --console-address ":9090"
```

NE:ONE 服务器默认使用由提供的 Docker Compose 文件来启动本地 Minio 服务器以用于 Blob 存储。
要配置其他 S3 对象存储，请参阅[Quarkus S3 扩展文档](ttps://docs.quarkiverse.io/quarkus-amazon-services/dev/amazon-s3.html)。

默认配置在启动期间创建名为“neone”的存储桶。以下属性用于控制此行为：

| 属性                                             | 描述                             | 默认值 |
| ------------------------------------------------ | -------------------------------- | ---- |
| “blobstore.bucket-name”（blobstore.bucket-name） | 用于存储 blob 的存储桶名称       |      |
| “blobstore.create-bucket”                        | 如果存储桶不存在，是否创建存储桶 | 假   |

#### 启动 Grafana 和 Prometheus 进行监控

NE:ONE 服务器在 '/q/metrics' 端点公开 Prometheus 的指标。
本项目提供了 Docker Compose 文件来启用数据监控。
安装程序将启动 Prometheus 和一个Grafana实例。这两个默认配置为直接查看衡量指标值。

Prometheus连接主机的8080端口，所以其前提是NE:ONE服务器已启动，且对外开放HTTP端口8080。

采用以下命令启动监控：
```shell
docker compose -f docker-compose.monitoring.yml up -d
```

#### 组合配置

可以组合(m)TLS 和 GraphDB 的配置起来启动服务器，即：

```shell script
docker compose -f docker-compose.yml -f docker-compose.tls.yml -f docker-compose.graphdb.yml \
  -f docker-compose.graphdb-server.yml -f docker-compose.mockserver.yml up -d
```

> **_NOTE：_** 在每种情况下，“docker-compose.yml”都必须是列表中的第一个文件。

### 测试两台NE:ONE服务器之间的互操作性

要测试通知和订阅，需要两个NE:ONE服务器和前面提到的模拟服务器。
使用 docker compose来启动模拟服务器。

```shell script
docker compose -f docker-compose.mockserver.yml up -d
```

这将启动模拟服务器并将其开放localhost上的端口1080，请确保端口 1080 尚未使用。

之后，可以使用NE:ONE docker镜像启动两个NE:ONE服务器。
连接两台服务器的最简单方法就是使用 docker 的主机网络驱动。

确保端口 8080 和 8081 尚未在主机系统上使用。

```shell script
docker run -d --name ne-one-1 --net=host \
  -e QUARKUS_REST_CLIENT_SUBSCRIPTION_CLIENT_URL=http://localhost:1080 \
  git.openlogisticsfoundation.org:5050/wg-digitalaircargo/ne-one:dev

docker run -d --name ne-one-2 --net=host \
  -e LO_ID_CONFIG_PORT=8081 \
  -e QUARKUS_HTTP_PORT=8081 \
  -e QUARKUS_REST_CLIENT_SUBSCRIPTION_CLIENT_URL=http://localhost:1080 \
  git.openlogisticsfoundation.org:5050/wg-digitalaircargo/ne-one:dev
```

模拟服务器设置为接受所有发布者发起的订阅。

## 在Redis中缓存远程物流对象

NE:ONE服务器包括一项用于获取远程物流对象的服务。
如果订阅远程对象的物流对象或物流对象类型，那就会放在Redis缓存服务器中。
如果对象发生了更改，并且收到有关更改的通知，则释放缓存条目。

默认情况下，缓存处于禁用状态。
为了启用缓存，必须将 Quarkus 配置中的“quarkus.cache.enabled”属性设置为'true' 。

redis 缓存服务器的配置记录在[Quarkus redis缓存指南]（https://quarkus.io/guides/cache-redis-reference）。

为了同时启用 Redis 运行状况检查，NE:ONE服务器的[re-augmentation](https://quarkus.io/guides/reaugmentation)是必需的。
NE:ONE docker 镜像中启用了运行状况检查。
自定义 docker 文件要包含此过程。

```dockerfile
FROM git.openlogisticsfoundation.org:5050/wg-digitalaircargo/ne-one as builder

# enable redis health check
ENV QUARKUS_REDIS_HEALTH_ENABLED=true
# enable health-ui
ENV QUARKUS_SMALLRYE_HEALTH_UI_ALWAYS_INCLUDE=true
# enable caching
ENV QUARKUS_CACHE_ENABLED=true
# set redis host
ENV QUARKUS_REDIS_HOSTS=redis://localhost:6379

WORKDIR /deployments/quarkus-app

# run re-augmentation
RUN java -jar -Dquarkus.launch.rebuild=true quarkus-run.jar

# create new custom image from the re-augmented jar
FROM git.openlogisticsfoundation.org:5050/wg-digitalaircargo/ne-one

# copy re-augmented application to original destination
COPY --from=builder /deployments/quarkus-app/ /deployments/quarkus-app/
```

然后使用“docker build -t ne-one-redis .”构建映像。
现在，生成的映像使用 Redis 作为缓存系统，并启用 Redis 的运行状况检查。

# NE:ONE 开发 - 入门

这个项目使用了 Quarkus，即超音速亚原子 Java 框架。

如果您想了解更多关于Quarkus的信息，请访问其网站：https://quarkus.io/。

NE:ONE服务器是使用Java版本17开发的，也使用Docker来启动 [Quarkus开发服务](https://quarkus.io/guides/dev-services)
请确保您的开发环境满足这些要求。

## 在开发模式下运行应用程序

使用以下命令在开发模式下运行应用程序，该模式支持实时编码：

```shell script
./mvnw compile quarkus:dev
```

> **_NOTE：_** Quarkus 现在附带了一个仅在开发模式下可用的Dev UI，链接为 http://localhost:8080/q/dev/。

### 使用持久化 RDF 数据存储进行开发

NE:ONE服务器默认使用内存中的RDF存储。
但是，可以使用[ontotext GraphDB](https://www.ontotext.com) 
或[Blazepgraph](https://www.ontotext.com/)
或[RDF4J本地存储](https://rdf4j.org/documentation/programming/repository/#native-rdf-repository) 实现持续RDF 存储。

设置属性“repository-type”来指定存储库的类型：

* in-memory（默认）表示内存存储
* native 表示 RDF4J 本地存储
* http 表示 GraphDB 存储

**使用 RDF4J 本机存储**

本地存储以二进制格式将所有三元组存储在磁盘上，以便紧凑存储和检索。
该存储适合高达1亿多个的三元组。

配置：

| 属性             | 值                |
| ---------------- | ------------------- |
| repository-type     | native              |
| repository-data-dir | PATH_TO_DIRECTORY |

**使用 GraphDB**

要使用GraphDB，须在NE:ONE服务器启动之前启动并运行。
可使用Docker compose文件来启动 GraphDB 实例。

```shell script
cd src/main/docker-compose
docker docker compose -f docker-compose.graphdb-server.yml up -d
```

此命令还会在 GraphDB 实例中配置 ID 为“neone”的存储库。

现在，必须将“repository-type”属性设置为“http”。
可以使用quarkus默认配置来实现（'application.properties'、Java 系统属性、环境变量）。

即：

```shell script
./mvnw compile quarkus:dev -Drepository-type=http
```

> **_NOTE：_** 属性“http-repository-url”默认配置为“http://localhost:7200/repositories/neone”
> 这是使用 docker compose 文件创建的存储库的URL，
> 如果使用与提供的 docker compose 文件不同的方法启动GraphDB则需要修改这个配置值。

配置：

| 属性             | 值                  |
| ---------------- | --------------------- |
| repository-type     | http        |
| http-repository-url | URL_OF_GRAPHDB_REPO |

### 使用SPARQL兼容端
将repository-type属性值设为 sparql 来启用SPARQL兼容端，这可通过默认的quarkus配置来完成（application.properties, Java系统属性, 环境变量）。
而且，还需要设置属性sparql-query-endpoint和sparql-update-endpoint。

配置：

| 属性             | 值                  |
| ---------------- | --------------------- |
| repository-type     | sparql        |
| sparql-query-endpoint | SPARQL_QUERY_URL |
| sparql-update-endpoint | SPARQL_UPDATE_URL |

> **_NOTE：_** GraphDB也提供SPARQL端点。
> [GraphDB docker-compose文件](https://git.openlogisticsfoundation.org/wg-digitalaircargo/ne-one/-/blob/develop/src/main/docker-compose/docker-compose.graphdb-server.yml) 的默认配置中，
> SPARQL查询端的值为http://localhost:7200/repositories/neone，
> SPARQL更新端的值为 http://localhost:7200/repositories/neone/statements.
> SPARQL查询端用于读操作，更新段用于写操作。

# 授权 API

NE:ONE服务器的授权是通过[W3C ACL Ontology](https://www.w3.org/ns/auth/acl) 实现的。

## 创建ACL

### 授予对具体物流对象的访问权限

|           |                                  |
| --------- | -------------------------------- |
| Endpoint  | /internal/acls/grant                |
| HTTP Method | POST                          |
| Content TYpe  | application/x-www-form-urlencoded |

表单参数：

| 名称   | 描述                       | 备注                                                         |
| ------ | -------------------------- | ------------------------------------------------------------ |
| accessTo | 要授予访问权限的对象的 IRI |                                                              |
| agent | 应授予访问权限的代理的 IRI |                                                              |
| modes | 访问方式                   | 可以是“acl：Read”或“acl：Write”，可以在单个请求中多次出现以授予这两种模式 |

### 为特定请求者创建 ACL

|           |                    |
| --------- | ------------------ |
| Endpoint  | /internal/acls              |
| HTTP Method | POST                          |
| Content TYpe  | application/ld+json |

请求正文：

```json
{
  "@context": {
    "@vocab": "http://www.w3.org/ns/auth/acl#",
    "acl": "http://www.w3.org/ns/auth/acl#"
  },
  "@type": "acl:Authorization",
  "agent": {
    "@id": "<ACCESS_SUBJECT_IRI>"
  },
  "accessTo": {
    "@id": "<ACCESS_OBJECT_IRI>"
  },
  "mode": [
    {
      "@id": "<ACL_MODE>"
    }
  ]
}
```

| 变量                 | 值                                                         |
| -------------------- | ------------------------------------------------------------ |
| ACCESS_SUBJECT_IRI | 应授予访问权限的“cargo:LogisticsAgent”的 IRI                |
| ACCESS_OBJECT_IRI  | 应授予访问权限的 cargo:LogisticsObject、cargo：LogisticsEvent 或 api：ActionRequest 的 IRI |
| ACL_MODE           | acl：Read、acl：Write 或两者兼而有之                     |

响应头：

| 响应头   | 值             |
| ------ | ---------------- |
| Location | 已创建ACL的URL |

### 为所有经过身份验证的请求者创建单个 ACL

为所有经过身份验证的请求者创建 ACL，可采用“http://www.w3.org/ns/auth/acl#AuthenticatedAgent”作为“acl：agent”谓语的主语。

```json
{
  "@context": {
    "@vocab": "http://www.w3.org/ns/auth/acl#",
    "acl": "http://www.w3.org/ns/auth/acl#"
  },
  "@type": "acl:Authorization",
  "agent": {
    "@id": "http://www.w3.org/ns/auth/acl#AuthenticatedAgent"
  },
  "accessTo": {
    "@id": "<ACCESS_OBJECT_IRI>"
  },
  "mode": [
    {
      "@id": "<ACL_MODE>"
    }
  ]
}
```

## 获取ACL

|           |                              |
| --------- | ---------------------------- |
| Endpoint      | /internal/acls/<unique-id> |
| HTTP Method | POST                     |
| Accept      | application/ld+json           |

响应：

JSON-LD格式的ACL。

## 更新 ACL

|           |                              |
| --------- | ---------------------------- |
| Endpoint      | /internal/acls/<unique-id> |
| HTTP Method | POST                     |
| Accept      | application/ld+json           |

请求正文：

```json
{
  "@context": {
    "@vocab": "http://www.w3.org/ns/auth/acl#",
    "acl": "http://www.w3.org/ns/auth/acl#"
  },
  "@type": "acl:Authorization",
  "agent": {
    "@id": "<ACCESS_SUBJECT_IRI>"
  },
  "accessTo": {
    "@id": "<ACCESS_OBJECT_IRI>"
  },
  "mode": [
    {
      "@id": "<ACL_MODE>"
    }
  ]
}
```

| 变量                 | 值                                                         |
| -------------------- | ------------------------------------------------------------ |
| ACCESS_SUBJECT_IRI | 应授予访问权限的cargo：LogisticsAgent的 IRI                |
| ACCESS_OBJECT_IRI  | 应授予访问权限的 cargo：LogisticsObject、cargo：LogisticsEvent 或 api：ActionRequest 的 IRI |
| ACL_MODE           | acl：Read、acl：Write 或两者兼而有之                     |

已有的ACL将被作为请求正文提供的 ACL 覆盖。

响应：

HTTP 状态码 200 表示成功，如果未找到要更新的 ACL，则为 404。

## 删除ACL

|           |                              |
| --------- | ---------------------------- |
| Endpoint      | /internal/acls/<unique-id> |
| HTTP Method | DELETE                       |
| Accept      | application/ld+json           |

响应：

HTTP 状态 200 表示成功，如果未找到要更新的 ACL，则为 404。

## 查找 ACL

|           |                    |
| --------- | ------------------ |
| Endpoint      | /internal/acls       |
| HTTP Method | POST             |
| Accept      | application/ld+json |

查询参数：

| 参数   | 值                                                       |
| ------ | ---------------------------------------------------------- |
| agent | 有权访问某个对象的主体。如果未设置“accessTo”，则为必填项。 |
| accessTo | ACL 链接到的对象。如果未设置“agent”，则为必填项。          |

响应正文：

与给定查询匹配的 ACL 列表。

# Blobstore 接口

NE:ONE服务器允许存储blob并将定义的ACL应用于存储的对象。
ACL 继承自它们链接到的“cargo：ExternalReference”物流对象。

## 上传 blob

|           |                   |
| --------- | ----------------- |
| Endpoint      | files/upload/<SHORT_LO_ID>   |
| HTTP Method | POST            |
| Content-Type  | multipart/form-data |

表单参数：

| 名称     | 描述             |
| -------- | ---------------- |
| mimetype   | 文件的 MIME 类型 |
| filename | 文件名           |
| data  | 要上传的文件     |

<SHORT_LO_URI>必须是已有'cargo：ExternalReference'的URI的UUID。

响应标头：

| 响应头   | 值           |
| ------ | -------------- |
| Location | 上传文件的 URL |

## 下载文件

|           |                            |
| --------- | -------------------------- |
| Endpoint      | files/download/<SHORT_LO_ID>/<filename>   |
| HTTP Method | POST            |

<SHORT_LO_URI>必须是已有'cargo：ExternalReference'的URI的UUID。

HTTP 响应：

请求的文件。

# 远程物流对象代理 API

NE:ONE服务器能够将请求代理给第三方物流对象。
为了获取远程对象，NE:ONE服务器需要使用以下属性对受信任的身份提供程序进行身份验证：

```properties
quarkus.oidc-client.auth-server-url=<trusted_idp_url>
quarkus.oidc-client.client-id=<client_id>
quarkus.oidc-client.credentials.secret=<client_secret>
```

> **_NOTE：_** 遵循 IATA ONE Record规范

开发时，这些属性被预配置为使用提供的Keycloak实例。

|           |                    |
| --------- | ------------------ |
| Endpoint      | /internal/proxy       |
| HTTP Method | GET            |
| Accept      | application/ld+json |

查询参数：

| 名称  | 描述               |
| ----- | ------------------ |
| iri | 远程物流对象的 IRI |

响应是使用 JSON-LD 上下文规范化的物流对象
'“@vocab”: “https://onerecord.iata.org/ns/cargo#”'。

# 第一个物流对象入门

> **_NOTE：_** 假定数据持有者属性的所有值都取自
> [提供的Keycloak配置](#starting-keycloak-for-authentication)。

1. 按照 IATA ONE Record规范中所述，使用 API 创建物流对象。
   严格来说，Logistics Objects 不是 ONE Record API 的一部分，不需要身份验证。
   保护端点超出了 NE:ONE 服务器的范围。

例如：

```shell
 curl --request POST \
 --url http://localhost:8080/logistics-objects \
 --header 'Accept: application/ld+json' \
 --header 'Content-Type: application/ld+json' \
 --data '{
   "@context": {
   "@vocab": "https://onerecord.iata.org/ns/cargo#",
   "cargo": "https://onerecord.iata.org/ns/cargo#"
 },
   "@type": "cargo:Piece",
   "handlingInstructions": [
     {
       "@type": "cargo:HandlingInstructions",
       "hasDescription": "Valuable Cargo",
       "isOfHandlingInstructionsType": "SPH",
       "isOfHandlingInstructionsTypeCode": "VAL"
     }
   ]
 }'
```

2.使用“Location”响应标头为已创建的“物流对象”来创建 ACL 条目，使用
   [ACL 接口](#authorization-API)，即

```shell
curl --request POST \
  --url http://localhost:8080/internal/acls \
  --header 'Content-Type: application/ld+json' \
  --data '{
  "@context": {
    "@vocab": "http://www.w3.org/ns/auth/acl#",
    "acl": "http://www.w3.org/ns/auth/acl#"
  },
  "@type": "acl:Authorization",
  "agent": {
    "@id": "http://localhost:8080/logistics-objects/_data-holder"
  },
  "accessTo": {
    "@id": "[LOCATION_OF_CREATED_LOGISTICS_OBJECT]"
  },
  "mode": [
    {
      "@id": "acl:Read"
    },
    {
      "@id": "acl:Write"
    }
  ]
}
'
```

3. 使用IATA ONE Record API来和物流对象进行交互。通过IATA ONE Record API进行交互是安全的，
   因为它默认将JWT令牌（获取自 [Keycloak实例](https://git.openlogisticsfoundation.org/wg-digitalaircargo/ne-one#starting-keycloak-for-authentication) ） 包含在每一次的请求中。

# 配置

## 配置订阅者验证、通知转发和订阅请求审批

要为通知启用订阅者验证，可以启用属性“validate-subscribers”（默认为'false'）。
如果启用，则物流对象上发生的每个事件都将触发对第三方应用程序的请求，应使用要通知的合作伙伴服务器列表进行响应。
该请求作为“GET”请求发出给端点定义为“${quarkus.rest-client.notification-client.url}/notifications/partner?loid=${loid}”。
这允许管理服务器以从第三方应用程序发出通知。

服务器默认不将收到的通知转发到第三方服务器。
若要启用转发通知，属性“forward-notifications”必须设置为“true”。
要配置接受转发的通知的终端节点，属性“quarkus.rest-client.notification-client.url”必须设置为指向接受“POST”请求的服务器的基本URL，
它可以接受包含带有路径“/notifications”的通知。

服务器配置为自动接受 60 分钟后过期的所有订阅请求。
若要更改此行为，必须将属性“auto-accept-subscription-proposals”值设置为“false”。
如果设置为“false”，服务器将向配置的终结点发送“GET”请求以批准订阅请求。

使用属性“quarkus.rest-client.subscription-client.url”配置发送订阅请求的端点。
此端点是 Web 服务的基本URL，该服务接受带有查询参数的“GET”请求，请求里带有路径 '/proposal' 下的 'topicType' 和 'topic'两个参数。
若要更改自动创建的订阅请求响应的到期时间，可使用“default-subscription-lifespan”属性。

## 内部IRI

NE:ONE服务器在处理请求时，将所有空白节点替换为内部IRI。
该IRI的模式可使用属性“lo-id-config.internal-iri-scheme”进行配置。

| 属性                                | 默认值     | 描述              |
| ---------------------------------- | -------- | ----------------- |
| “lo-id-config.internal-iri-scheme” | “neone” | 内部IRI使用的模式 |

替换方式将采用一个空白节点并将其转换为 '<lo-id-config.internal-iri-scheme>:<UUID>'，
例如默认设置中，空白节点“_:b0”将被转换为“neone:87d2d6b1-af8b-45de-b25c-98264a7ddd22”。
所有链接将得到维护。

## 使用短UIDs
NanoIDs可用来替代[UUIDs](https://github.com/ai/nanoid) 作为标识符。
NE:ONE服务器使用默认Nano ID。可查看 [Nano ID Collision Calculator](https://zelark.github.io/nano-id-cc/) 更多关于collision可能性的详细信息。
若要使用Nano ID，需设置 lo-id-config.random-id-strategy 属性值为 nanoid。
该配置使用内置于 java.util.UUID类找那个的Java来生成 ID。

## 设置JSON-LD模式
JSON-LD表单可以通过jsonld.mode属性来设置。

| 属性                                | 默认值     | 描述              |
| ---------------------------------- | -------- | ----------------- |
| jsonld.mode | compact | JSON-LD表单，可以是 compact， flatten，或者expand，可查看 [JSON-LD表单](https://www.w3.org/TR/json-ld11/#forms-of-json-ld) |

## 使用 mTLS 访问服务器

NE:ONE服务器可以使用TLS进行访问。默认 TLS 端口为“8443”。
'src/test/tls' 文件夹包含所有准备用于 **test** 和 **development** 的必要密钥和证书。

> **_WARNING：_** 请勿将这些文件用于生产，而只能将它们用于测试目的。

在开发模式下，服务器默认使用“src/test/tls”文件夹中提供的密钥和证书。
如果不使用提供的文件，服务器可以使用属性“quarkus.http.ssl.certificate.key-store-file”，
'quarkus.http.ssl.certificate.key-store-password'， 'quarkus.http.ssl.certificate.trust-store-file' 和
'quarkus.http.ssl.certificate.trust-store-password'进行配置。

### 生产环境中 mTLS 配置

| 属性                                                         | 默认值              | 描述                                 |
| ------------------------------------------------------------ | ----------------- | ------------------------------------ |
| “quarkus.http.ssl.client-auth” | “required”            | 拒绝所有没有受信任客户端证书的客户端 |
| “quarkus.http.ssl.certificate.trust-store-file” | “config/truststore.p12” | 信任库路径                           |
| “quarkus.http.ssl.certificate.trust-store-password” | “changeit”            | 信任库密码                           |
| “quarkus.http.ssl.certificate.key-store-file” | “config/keystore.p12” | 服务器密钥库的路径                   |
| “quarkus.http.ssl.certificate.key-store-password” | “changeit”            | 密钥库的密码                         |
| “quarkus.http.port”                     | `0`               | 禁用非 TLS http 端口                 |

### 创建自己的证书

以下示例使用 'openssl' 和 java 'keytool' 来创建必要文件以运行启用了mTLS的NE:ONE服务器。

1. 创建一个能够对 CSR 进行签名的根 CA（我们使用 CA 对服务器和客户端证书进行签名）

```shell script
openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes -keyout rootCA.key -out rootCA.crt -subj "/CN=NEONE CA"
```

2.为服务器创建证书签名请求 （CSR）

```shell script
openssl req -new -newkey rsa:4096 -nodes \
    -keyout localhost.key -out localhost.csr \
    -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"                                                                                                                                                                               
```

3.对 CSR 进行签名以获取服务器证书

```shell script
openssl x509 -req -CA rootCA.crt -CAkey rootCA.key \
    -in localhost.csr -out localhost.crt \
    -days 365 -CAcreateserial -copy_extensions copyall
```

4.创建服务器密钥库（密码为“changeit”） 

```shell script
openssl pkcs12 -export -out localhost.p12 -name "localhost" \
    -inkey localhost.key -in localhost.crt \
    -passout pass:changeit
```

5.创建一个信任库，该信任库信任由之前创建的根 CA 颁发的所有证书（密码为“changeit”）

```shell script
keytool -import -file rootCA.crt -alias neoneCA -keystore truststore.p12 -storepass changeit
```

6.为客户端证书创建证书签名请求 

```shell script
openssl req -new -newkey rsa:4096 -nodes \
    -keyout client.key -out client.csr \
    -subj "/CN=neone-client" \
    -addext "extendedKeyUsage=clientAuth"
```

7.使用根 CA 对客户端 CSR 进行签名以获取客户端证书                  

```shell script
openssl x509 -req -CA rootCA.crt -CAkey rootCA.key \
    -in client.csr -out client.crt \
    -days 365 -CAcreateserial -copy_extensions copyall
```

8.创建客户端密钥库（密码为“changeit”）

```shell script
openssl pkcs12 -export -out client.p12 -name "neone-client" \
    -inkey client.key -in client.crt -passout pass:changeit
```

### 配置客户端

与服务器交互时，必须将客户端配置为使用受信任的证书。
使用时[Insomnia](https://insomnia.rest) 这是使用_Collection Settings_配置的。
例如，使用提供的证书，请按照以下步骤为 mTLS 配置 Insomnia。

1. 打开集合设置
   ![收藏设置](.\images\失眠集合设置.png)
2. 切换到客户端证书部分以添加 CA 证书和客户端证书
 ![客户端证书部分](.\images\失眠-集合-设置-证书1.png)
    * 单击_Choose PEM file_，然后选择“rootCA.crt”文件
    * 点击_New Certificate_
3. 添加客户端证书
 ![添加证书](.\images\失眠-集合-设置-证书2.png)
    * 将 _host_ 设置为 'localhost：8443'
    * 单击_Choose Cert_并选择“client.crt”文件
    * 单击_Choose Key_并选择“client.key”文件
    *（在MacOS上，单击_Choose File_并选择“client.p12”文件并将_Passphrase_设置为“changeit”）

### 使用不受信任的客户端证书进行测试

为了使用不受信任的证书测试 mTLS 配置，“src/test/tls”文件夹包含一个自签名证书，可用作客户端证书。

要创建不受信任的自签名证书，可以使用“openssl”。

```shell script
# create CSR and key
openssl req -newkey rsa:4096 -nodes -keyout self-signed.key -out self-signed.csr -subj "/CN=not-known"

# use created key to sign the CSR
openssl x509 -signkey self-signed.key -in self-signed.csr -req -days 3650 -out self-signed.crt
```

### 禁用 mTLS

可以通过将“quarkus.http.ssl.client-auth”属性设置为“none”来禁用mTLS客户端身份验证。
这确实未禁用 TLS，因此服务器仍提供 TLS 端点（端口 8443），但不要求提供客户端证书。

# 打包并运行应用程序

可以使用以下方法打包应用程序：

```shell script
./mvnw package
```

它在“target/quarkus-app/”目录中生成“quarkus-run.jar”文件。
请注意，它不是_über jar_，因为依赖项被复制到“target/quarkus-app/lib/”目录中。

该应用程序现在可以使用“java -jar target/quarkus-app/quarkus-run.jar”运行。

如果要构建_über jar_，请执行以下命令：

```shell script
./mvnw package -Dquarkus.package.type=uber-jar
```

该应用程序打包为 _über-jar_，现在可以使用“java -jar target/*-runner.jar”运行。

# 创建原生可执行文件

您可以使用以下方法创建本机可执行文件：

```shell script
./mvnw package -Pnative
```

或者，如果未安装 GraalVM，可以使用以下命令在容器中运行本机可执行版本：

```shell script
./mvnw package -Pnative -Dquarkus.native.container-build=true
```

然后，您可以使用以下命令执行本机可执行文件：“./target/ne-one-1.0-SNAPSHOT-runner”

如果您想了解有关构建本机可执行文件的更多信息，请咨询 https://quarkus.io/guides/maven-tooling。

# 相关指南

- RESTEasy Reactive [guide](https://quarkus.io/guides/resteasy-reactive), 利用构建时的 JAX-RS 实现
  处理和 Vert.x.此扩展与 quarkus-resteasy 扩展或任何基于它的扩展不兼容。

# 性能测试
项目提供了一个基础的JMeter性能测试计划。
可用于了解你所期望的工作载荷，或者检测特殊运行设置时的负载能力。

1. 安装 Apache JMeter
2. 打开 Performance Test Plan.jmx
3. 在测试计划内配置参数
4. 启动NE:ONE和所有需要的服务
5. 在JMeter中启动测试计划

![](.\images\Jmeter.png)


执行步骤如下：
- 设置全局配置属性
- 登录身份认证服务器
- 创建一个物流对象
- 获取这个物流对象
- 创建基于该物流对象的订阅
- 通过修改请求修改该物流对象
- 创建物流事件
- 用一组视图输出结果

推荐采用测试计划来展开你的测试案例以获取更多有意义的成果。

若要运行测试计划，你还要在 Set global properties 测试步骤中输入有效的参数。
通过调整Throuput shaping timer中的 request per second 曲线，可控制生成的负载。
注意，Main Thread Group 要为shaping timer提供充足的 Number of threads (users),
因为它只能限制负载，但不会生成负载。
所以，增加或减少shaping timer中每秒请求的最大数量，与线程组中的匹配的线程数量密切相关。