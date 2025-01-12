from fastapi import FastAPI, HTTPException, Request
from kafka_app.producer import KafkaProducer
from kafka_app.consumer import KafkaConsumer
from kafka_app.config import KAFKA_TOPIC, MAX_REQUEST_SIZE
import asyncio
app = FastAPI()

kafka_producer = KafkaProducer()
kafka_consumer = KafkaConsumer()

@app.on_event("startup")
async def startup_event():
    print("STARTUP EVENT")
    await kafka_producer.start()
    await kafka_consumer.start()
    app.state.consumer_task = asyncio.create_task(kafka_consumer.consume_messages())
    print("Kafka Producer and Consumer started.")

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down Kafka...")
    await kafka_consumer.stop()
    await kafka_producer.stop()
    await app.state.consumer_task
    print("Kafka stopped.")

@app.post("/produce")
async def produce_message(request: Request,message: dict):
    
    request_body = await request.body()  # Get the raw body of the request
    request_length = len(request_body)  # Calculate the length of the request data
    
    print(f"Request data length: {request_length} bytes")  # Log the length     
        
    try:
        
        if request_length > MAX_REQUEST_SIZE:
            print("Request body is too large")
            raise HTTPException(status_code=413, detail="Request body is too large")
        
        await kafka_producer.send_message(KAFKA_TOPIC, message)
        return {"status": "Message sent successfully!", "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Kafka FastAPI Integration"}