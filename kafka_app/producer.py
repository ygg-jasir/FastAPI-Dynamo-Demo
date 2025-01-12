import asyncio
import json
from aiokafka import AIOKafkaProducer
from .config import KAFKA_BOOTSTRAP_SERVERS, MAX_REQUEST_SIZE

class KafkaProducer:
    def __init__(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            max_request_size=MAX_REQUEST_SIZE 
        )

    async def start(self):
        print("\n\nMAIN THREAD: Starting Kafka Producer... ^^^^^^^ \n\n")
        await self.producer.start()

    async def stop(self):
        print("\n\nMAIN THREAD: Stopping Kafka Producer... -------  ---- -- - - 0\n\n")
        
        await self.producer.stop()

    async def send_message(self, topic: str, message: dict):
        await self.producer.send_and_wait(topic, message)