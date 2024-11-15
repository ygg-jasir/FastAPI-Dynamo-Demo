from kafka_integrations import kafka_config
from ygag_kafka_generic import KafkaSyncProducer

class ProdcuerClassNew(KafkaSyncProducer):
  @staticmethod
  def get_acknowledgement(err , event) -> None:
     """
     The "get_acknowledgement" function is a callback function that is called after each producer
     request
     
     here "err" and "event" will be passed to after each data pushed to brocker
     err will be a KafkaException object 
     
     if err.code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
     
     This callback is called exactly once per message, indicating if
     the message was succesfully delivered
     
     err  = None or permanently failed delivery (err = error message type :: string.
     
     This callback is triggered by rd_kafka_poll() or rd_kafka_flush()
     for client instance-level errors, such as broker connection failures,
     authentication issues, etc.
     
     These errors should generally be considered informational as
     the underlying client will automatically try to recover from
     any errors encountered, the application does not need to take
     action on them.
     
     
     callback  attribute "event" will be in serialized object format, if you want to unpack key or value
     you have to deserialize the objects

     you can use self.deserializer for deserializing key|value
      from ygag_kafka_generic import MessageField
     eg: event_value = self.deserializer(event : kafka event, MessageField.VALUE/MessageField.KEY)
     """
     print("Event ",event.value())
    
  @staticmethod
  def get_error(err) -> None:
     """
     The "get_error" function will usually be invoked when the producer throws a fatal Kafka error
     
     When a fatal error is detected by the producer instance,
     it will trigger an get_error with ERR__FATAL set.
     The application should use the actual underlying error code and description, 
     propagate it to the user (for troubleshooting), and then terminate the
     producer since it will no longer accept any new messages to
     produce().
     
     * Note:
        After a fatal error has been raised, KafkaSyncProducer will
        fail with the original error code.
     """
     print("Err ",err)
    
  @staticmethod
  def get_kafka_config():
     """
     : return configurations module of Kafka settings or dict
     
     return your settings or configuration dict from this file
     eg:
       return Django.conf.settings | config_dict
     """
     print("get_kafka_config")
     return kafka_config 
  
  @staticmethod
  def get_exceptions(err):
       """
       "get_consumer_exceptions" method will catch runtime exceptions
       consumer event loop will be terminated if this method invocation happens
       : param err: consumer exceptions during runtime
       """
       print("Exc ",err)
       raise err