# Prerequisites

fastapi
aiokafka
uvicorn



## To Run

1. Make sure docker is running else run `docker-compose up` from kafka_fastapi directory

2. Run `uvicorn kafka_app.main:app --reload` 

or to run on another port

`uvicorn kafka_app.main:app --reload --port 8001`
