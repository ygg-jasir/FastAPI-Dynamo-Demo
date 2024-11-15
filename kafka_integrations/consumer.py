from typing import Dict
from kafka_integrations import kafka_config
from ygag_kafka_generic import KafkaSyncProducer,KafkaSyncConsumer


class ConsumerClassNew(KafkaSyncConsumer):
  
  
  @staticmethod
  def get_consumer_errors(error):
      """
      consumer error method errors received from Kafka consumer
      :param error: autogenrated by kafka class
      """
      pass
       
  @staticmethod
  def get_kafka_config():
      """
      : return configurations module of Kafka settings or dict
      
      return your settings or configuration dict from this file
      eg:
        return Django.conf.settings | config_dict
      """
      print("\n\n\nConfig ")
      return kafka_config
      
  @staticmethod
  def run_consumer_events(data: Dict,*args,**kwargs):
      """
      "run_consumer_events" this method will be invoked each time an event received
      on connected consumer topic
      : param data: consumer data received from events
      
      add you functions or logics that need to be invoked when receiving an event data
      here
      """
      print("run_consumer_events ",data)
      
      
  @staticmethod
  def get_exceptions(err):
       """
       "get_consumer_exceptions" method will catch runtime exceptions
       consumer event loop will be terminated if this method invocation happens
       : param err: consumer exceptions during runtime
       """
       print("Exc ",err)
       raise err
     
if __name__ == "__main__":
    ConsumerClassNew().run_consumer()