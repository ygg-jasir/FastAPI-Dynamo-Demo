## ygag-kafka-generic Kafka Integration on Macbook M3 Pro

Setup and run kafka in local for testing purpose, for this you can collect `docker-compose.yml` and run it with docker, make sure docker is installed

Sample Dir structure to test kafka, you can find the code in the repo it self
```
----root
    |__kafka-integration/
       |----consumer.py
       |----kafka_config.py
       |----producer.py
       |----docker-compose.yml
    |   
    |__.env
```

```
#.env
.
.
.
.
KAFKA_BOOTSTRAP_SERVERS='PLAINTEXT://localhost:9092'

KAFKA_SECURITY_PROTOCOL='PLAINTEXT'
KAFKA_SSL_CA_LOCATION = ''
KAFKA_SSL_KEY_LOCATION = ''
KAFKA_SSL_CERTIFICATE_LOCATION = ''
KAFKA_USER_TOPICS = ''
SASL_USERNAME=''
SASL_PASSWORD=''
PROJECT_NAME=fastapi-dynamo
AUTO_OFFSET_RESET=earliest
.
.
.

```


`docker-compose.yml`
```

---
version: '2'
services:

  broker:
    image: confluentinc/cp-kafka:7.6.2
    hostname: broker
    container_name: broker
    ports:
      - "9092:9092"
      - "9101:9101"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: 'CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT'
      KAFKA_ADVERTISED_LISTENERS: 'PLAINTEXT://broker:29092,PLAINTEXT_HOST://localhost:9092'
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_JMX_PORT: 9101
      KAFKA_JMX_HOSTNAME: localhost
      KAFKA_PROCESS_ROLES: 'broker,controller'
      KAFKA_CONTROLLER_QUORUM_VOTERS: '1@broker:29093'
      KAFKA_LISTENERS: 'PLAINTEXT://broker:29092,CONTROLLER://broker:29093,PLAINTEXT_HOST://0.0.0.0:9092'
      KAFKA_INTER_BROKER_LISTENER_NAME: 'PLAINTEXT'
      KAFKA_CONTROLLER_LISTENER_NAMES: 'CONTROLLER'
      KAFKA_LOG_DIRS: '/tmp/kraft-combined-logs'
      CLUSTER_ID: 'MkU3OEVBNTcwNTJENDM2Qk'

  schema-registry:
    image: confluentinc/cp-schema-registry:7.6.2
    hostname: schema-registry
    container_name: schema-registry
    depends_on:
      - broker
    ports:
      - "8081:8081"
    environment:
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: 'broker:29092'
      SCHEMA_REGISTRY_LISTENERS: http://0.0.0.0:8081

  control-center:
    image: confluentinc/cp-enterprise-control-center:7.6.2
    hostname: control-center
    container_name: control-center
    depends_on:
      - broker
      - schema-registry
    ports:
      - "9021:9021"
    environment:
      CONTROL_CENTER_BOOTSTRAP_SERVERS: 'broker:29092'
      CONTROL_CENTER_CONNECT_CONNECT-DEFAULT_CLUSTER: 'connect:8083'
      CONTROL_CENTER_CONNECT_HEALTHCHECK_ENDPOINT: '/connectors'
      CONTROL_CENTER_KSQL_KSQLDB1_URL: "http://ksqldb-server:8088"
      CONTROL_CENTER_KSQL_KSQLDB1_ADVERTISED_URL: "http://localhost:8088"
      CONTROL_CENTER_SCHEMA_REGISTRY_URL: "http://schema-registry:8081"
      CONTROL_CENTER_REPLICATION_FACTOR: 1
      CONTROL_CENTER_INTERNAL_TOPICS_PARTITIONS: 1
      CONTROL_CENTER_MONITORING_INTERCEPTOR_TOPIC_PARTITIONS: 1
      CONFLUENT_METRICS_TOPIC_REPLICATION: 1
      PORT: 9021

```


to run the file, take a terminal and run the below command

```docker-compose up```

This will download kafka image and run it for you. And then keep that terminal aside.

Now we need to install private package from ygag repository. Make sure awscli is installed. And then follow below command to install ygag-kafka-generic

```
CODEARTIFACT_AUTH_TOKEN=`aws codeartifact get-authorization-token --domain yougotagift --domain-owner 507980205015 --query authorizationToken --output text --region us-east-1`
```

```
YGAG_PRIVATE_REPO="https://aws:$CODEARTIFACT_AUTH_TOKEN@yougotagift-507980205015.d.codeartifact.us-east-1.amazonaws.com/pypi/private/simple/"
```



```
pip install ygag-kafka-generic==1.0.6a5  --extra-index-url=$YGAG_PRIVATE_REPO 
```

#### Note: Check for latest stable version in the gitrepo https://github.com/YouGotaGift/ygag_kafka_generic, 1.0.6a5 was during installation

### Errors encountered

1. 

```
Looking in indexes: https://pypi.org/simple, https://aws:****@yougotagift-507980205015.d.codeartifact.us-east-1.amazonaws.com/pypi/private/simple/
Collecting ygag-kafka-generic==1.0.6a5
  Using cached https://yougotagift-507980205015.d.codeartifact.us-east-1.amazonaws.com/pypi/private/simple/ygag-kafka-generic/1.0.6a5/ygag_kafka_generic-1.0.6a5-py3-none-any.whl (19 kB)
Collecting fastavro<2.0.0,>=1.8.1
  Using cached fastavro-1.9.7-cp310-cp310-macosx_10_9_universal2.whl (1.0 MB)
Collecting protobuf<5.0.0,>=4.25.2
  Using cached protobuf-4.25.5-cp37-abi3-macosx_10_9_universal2.whl (394 kB)
Collecting confluent-kafka==1.8.2
  Using cached confluent-kafka-1.8.2.tar.gz (104 kB)
  Preparing metadata (setup.py) ... done
Installing collected packages: confluent-kafka, protobuf, fastavro, ygag-kafka-generic
  DEPRECATION: confluent-kafka is being installed using the legacy 'setup.py install' method, because it does not have a 'pyproject.toml' and the 'wheel' package is not installed. pip 23.1 will enforce this behaviour change. A possible replacement is to enable the '--use-pep517' option. Discussion can be found at https://github.com/pypa/pip/issues/8559
  Running setup.py install for confluent-kafka ... error
  error: subprocess-exited-with-error
  
  × Running setup.py install for confluent-kafka did not run successfully.
  │ exit code: 1
  ╰─> [57 lines of output]
      running install
      /Users/mohamedjasir/.pyenv/versions/3.10.13/envs/fastapi-pynamo-env/lib/python3.10/site-packages/setuptools/command/install.py:34: SetuptoolsDeprecationWarning: setup.py install is deprecated. Use build and pip and other standards-based tools.
        warnings.warn(
      running build
      running build_py
      creating build
      creating build/lib.macosx-14.3-arm64-cpython-310
      creating build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka
      copying src/confluent_kafka/error.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka
      copying src/confluent_kafka/serializing_producer.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka
      copying src/confluent_kafka/__init__.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka
      copying src/confluent_kafka/deserializing_consumer.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka
      creating build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/schema_registry
      copying src/confluent_kafka/schema_registry/avro.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/schema_registry
      copying src/confluent_kafka/schema_registry/error.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/schema_registry
      copying src/confluent_kafka/schema_registry/__init__.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/schema_registry
      copying src/confluent_kafka/schema_registry/json_schema.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/schema_registry
      copying src/confluent_kafka/schema_registry/schema_registry_client.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/schema_registry
      copying src/confluent_kafka/schema_registry/protobuf.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/schema_registry
      creating build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/serialization
      copying src/confluent_kafka/serialization/__init__.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/serialization
      creating build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/admin
      copying src/confluent_kafka/admin/__init__.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/admin
      creating build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/avro
      copying src/confluent_kafka/avro/error.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/avro
      copying src/confluent_kafka/avro/__init__.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/avro
      copying src/confluent_kafka/avro/cached_schema_registry_client.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/avro
      copying src/confluent_kafka/avro/load.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/avro
      creating build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/kafkatest
      copying src/confluent_kafka/kafkatest/verifiable_client.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/kafkatest
      copying src/confluent_kafka/kafkatest/__init__.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/kafkatest
      copying src/confluent_kafka/kafkatest/verifiable_consumer.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/kafkatest
      copying src/confluent_kafka/kafkatest/verifiable_producer.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/kafkatest
      creating build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/avro/serializer
      copying src/confluent_kafka/avro/serializer/__init__.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/avro/serializer
      copying src/confluent_kafka/avro/serializer/message_serializer.py -> build/lib.macosx-14.3-arm64-cpython-310/confluent_kafka/avro/serializer
      running build_ext
      building 'confluent_kafka.cimpl' extension
      creating build/temp.macosx-14.3-arm64-cpython-310
      creating build/temp.macosx-14.3-arm64-cpython-310/private
      creating build/temp.macosx-14.3-arm64-cpython-310/private/var
      creating build/temp.macosx-14.3-arm64-cpython-310/private/var/folders
      creating build/temp.macosx-14.3-arm64-cpython-310/private/var/folders/tl
      creating build/temp.macosx-14.3-arm64-cpython-310/private/var/folders/tl/z_5d6l1529q4sh0tqr3dwc8w0000gn
      creating build/temp.macosx-14.3-arm64-cpython-310/private/var/folders/tl/z_5d6l1529q4sh0tqr3dwc8w0000gn/T
      creating build/temp.macosx-14.3-arm64-cpython-310/private/var/folders/tl/z_5d6l1529q4sh0tqr3dwc8w0000gn/T/pip-install-a1yvurhd
      creating build/temp.macosx-14.3-arm64-cpython-310/private/var/folders/tl/z_5d6l1529q4sh0tqr3dwc8w0000gn/T/pip-install-a1yvurhd/confluent-kafka_c7a0b3e91bf540af9541bcb380b6f8d4
      creating build/temp.macosx-14.3-arm64-cpython-310/private/var/folders/tl/z_5d6l1529q4sh0tqr3dwc8w0000gn/T/pip-install-a1yvurhd/confluent-kafka_c7a0b3e91bf540af9541bcb380b6f8d4/src
      creating build/temp.macosx-14.3-arm64-cpython-310/private/var/folders/tl/z_5d6l1529q4sh0tqr3dwc8w0000gn/T/pip-install-a1yvurhd/confluent-kafka_c7a0b3e91bf540af9541bcb380b6f8d4/src/confluent_kafka
      creating build/temp.macosx-14.3-arm64-cpython-310/private/var/folders/tl/z_5d6l1529q4sh0tqr3dwc8w0000gn/T/pip-install-a1yvurhd/confluent-kafka_c7a0b3e91bf540af9541bcb380b6f8d4/src/confluent_kafka/src
      clang -Wno-unused-result -Wsign-compare -Wunreachable-code -DNDEBUG -g -fwrapv -O3 -Wall -I/Users/mohamedjasir/.pyenv/versions/3.10.13/envs/fastapi-pynamo-env/include -I/Users/mohamedjasir/.pyenv/versions/3.10.13/include/python3.10 -c /private/var/folders/tl/z_5d6l1529q4sh0tqr3dwc8w0000gn/T/pip-install-a1yvurhd/confluent-kafka_c7a0b3e91bf540af9541bcb380b6f8d4/src/confluent_kafka/src/Admin.c -o build/temp.macosx-14.3-arm64-cpython-310/private/var/folders/tl/z_5d6l1529q4sh0tqr3dwc8w0000gn/T/pip-install-a1yvurhd/confluent-kafka_c7a0b3e91bf540af9541bcb380b6f8d4/src/confluent_kafka/src/Admin.o
      In file included from /private/var/folders/tl/z_5d6l1529q4sh0tqr3dwc8w0000gn/T/pip-install-a1yvurhd/confluent-kafka_c7a0b3e91bf540af9541bcb380b6f8d4/src/confluent_kafka/src/Admin.c:17:
      /private/var/folders/tl/z_5d6l1529q4sh0tqr3dwc8w0000gn/T/pip-install-a1yvurhd/confluent-kafka_c7a0b3e91bf540af9541bcb380b6f8d4/src/confluent_kafka/src/confluent_kafka.h:23:10: fatal error: 'librdkafka/rdkafka.h' file not found
      #include <librdkafka/rdkafka.h>
               ^~~~~~~~~~~~~~~~~~~~~~
      1 error generated.
      error: command '/usr/bin/clang' failed with exit code 1
      [end of output]
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
error: legacy-install-failure

× Encountered error while trying to install package.
╰─> confluent-kafka

note: This is an issue with the package mentioned above, not pip.
hint: See above for output from the failure.
```

## Resolution

Install `brew install librdkafka` , used version 1.8.6


Verify Homebrew Installation Path:

`brew --prefix librdkafka`

This should show something like `/opt/homebrew/opt/librdkafka`.

Add to PKG_CONFIG_PATH:

To make sure librdkafka is accessible to compilers and linkers, add it to your PKG_CONFIG_PATH:

```
export PKG_CONFIG_PATH="/opt/homebrew/opt/librdkafka/lib/pkgconfig:$PKG_CONFIG_PATH"
export C_INCLUDE_PATH="/opt/homebrew/include:$C_INCLUDE_PATH"
export LIBRARY_PATH="/opt/homebrew/lib:$LIBRARY_PATH"
export LD_LIBRARY_PATH="/opt/homebrew/lib:$LD_LIBRARY_PATH"
```

and retry installation 

```
pip install ygag-kafka-generic==1.0.6a5  --extra-index-url=$YGAG_PRIVATE_REPO 
```

if still issue, try it with below

```
CFLAGS="-I/opt/homebrew/include" LDFLAGS="-L/opt/homebrew/lib" pip install ygag-kafka-generic==1.0.6a5 --extra-index-url=$YGAG_PRIVATE_REPO
```

This resolved package installation issue.

##Then run consumer

```python kafka_integrations/consumer.py```

if error something like this, 

ModuleNotFoundError: No module named '_lzma'

1.	Install xz Library: Make sure the xz library, which includes liblzma, is installed. You can install it with:

```
Install `brew install xz`
```

2. Rebuild Python with liblzma Support:

Since you’re using pyenv, you may need to rebuild your Python environment to ensure that it links with liblzma. Run:

```
LDFLAGS="-L$(brew --prefix xz)/lib" CFLAGS="-I$(brew --prefix xz)/include" pyenv install 3.10.13
```

##Then run consumer

```python kafka_integrations/consumer.py```

Note: Worked for me.


