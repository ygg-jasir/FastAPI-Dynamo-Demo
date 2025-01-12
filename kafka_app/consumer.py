import asyncio
import json
from aiokafka import AIOKafkaConsumer
from .config import FETCH_MAX_BYTES, KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, MAX_REQUEST_SIZE

class KafkaConsumer:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            # This will consume only new messages
            auto_offset_reset="latest", # possible values: earliest, latest, none
            
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            group_id="your_consumer_group_proejctname",
            
            fetch_max_bytes=FETCH_MAX_BYTES
        )
        self.stop_event = asyncio.Event()

    async def start(self):
        await self.consumer.start()

    async def stop(self):
        self.stop_event.set()
        await self.consumer.stop()
        print("Kafka consumer stopped.")

    async def consume_messages(self):
        try:
            async for message in self.consumer:
                print(f"Consumed message: {message.value}")
                if self.stop_event.is_set():
                    break
        except Exception as e:
            print(f"Error while consuming messages: {e}")
            
            
            # Group Coordinator Request failed: [Error 15] GroupCoordinatorNotAvailableError