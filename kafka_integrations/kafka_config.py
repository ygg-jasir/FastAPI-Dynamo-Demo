from decouple import config
from ygag_kafka_generic.datatypes import MetaTopicDataType, AllowedSerdeFormats

BOOTSTRAP_SERVERS = config("KAFKA_BOOTSTRAP_SERVERS")
SECURITY_PROTOCOL = config("KAFKA_SECURITY_PROTOCOL")
SSL_CA_LOCATION = config('KAFKA_SSL_CA_LOCATION')
SSL_KEY_LOCATION = config('KAFKA_SSL_KEY_LOCATION')
SSL_CERTIFICATE_LOCATION = config('KAFKA_SSL_CERTIFICATE_LOCATION')

PROJECT_NAME = 'fastapi-dynamodb'
AUTO_OFFSET_RESET = 'earliest'

KAFKA_TOPICS = [
    "SampleTopic",
    "SampleTopic2",
    # "Ecommerce.EcomUsers.ServiceIntendedInternalUserDataPull"
    # DEPT.PROJECT.TOPIC_NAME
]

META_KAFKA_CONFIG= {
    "KAFKA_TOPICS_META_CONFIG": {
        "SampleTopic": MetaTopicDataType(
            PARTITION_NUMBER=3,
            REPLICATION_FACTOR=1
        ),
        "SampleTopic2": MetaTopicDataType(
            PARTITION_NUMBER=3,
            REPLICATION_FACTOR=1
        ),
        "NewTopic": MetaTopicDataType(
            PARTITION_NUMBER=3,
            REPLICATION_FACTOR=1
        )
    }
}

# {"id":[{"data":"test4"},{"data":"test5"},{"data":"test6"}]}