import pika
import json
import requests
from time import sleep
import os

# RabbitMQ connection parameters
amqp_host = os.environ.get("RABBITMQ_HOST", "localhost")
amqp_port = int(os.environ.get("RABBITMQ_PORT", 5672))
exchange_name = os.environ.get("EXCHANGE_NAME", "hangout_exchange")
exchange_type = os.environ.get("EXCHANGE_TYPE", "direct")
queue_name = os.environ.get("REGISTRATION_QUEUE_NAME", "event_registration")
routing_key = os.environ.get("REGISTRATION_ROUTING_KEY", "event_registration")
api_endpoint = os.environ.get("REGISTRATION_API_ENDPOINT", "http://localhost:5010/api/register_internal")

def setup_rabbitmq():
    """Set up RabbitMQ exchange and queue"""
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=amqp_host, port=amqp_port)
    )
    channel = connection.channel()

    # Check if exchange exists, create if it doesn't
    try:
        channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=True,
            passive=True,  # Passive mode to check if exists
        )
        print(f"Exchange {exchange_name} already exists")
    except pika.exceptions.ChannelClosedByBroker:
        # Reopen channel if it was closed due to exchange not existing
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=amqp_host, port=amqp_port)
        )
        channel = connection.channel()

        # Create the exchange
        channel.exchange_declare(
            exchange=exchange_name, exchange_type=exchange_type, durable=True
        )
        print(f"Exchange {exchange_name} created")

    # Check if queue exists, create if it doesn't
    try:
        channel.queue_declare(
            queue=queue_name,
            durable=True,
            passive=True,  # Passive mode to check if exists
        )
        print(f"Queue {queue_name} already exists")
    except pika.exceptions.ChannelClosedByBroker:
        # Reopen channel if it was closed due to queue not existing
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=amqp_host, port=amqp_port)
        )
        channel = connection.channel()

        # Make sure the exchange is declared
        channel.exchange_declare(
            exchange=exchange_name, exchange_type=exchange_type, durable=True
        )

        # Create the queue
        channel.queue_declare(queue=queue_name, durable=True)
        print(f"Queue {queue_name} created")

    # Bind queue to exchange
    channel.queue_bind(
        exchange=exchange_name, queue=queue_name, routing_key=routing_key
    )
    print(
        f"Queue {queue_name} bound to exchange {exchange_name} with routing key {routing_key}"
    )

    return connection, channel

def callback(ch, method, properties, body):
    """Process registration requests in order"""
    try:
        print(f"Processing registration request: {body}")
        registration_data = json.loads(body)

        # Forward the registration request to the internal API endpoint
        response = requests.post(
            api_endpoint, json=registration_data, headers={"Content-Type": "application/json"}
        )

        if response.status_code == 201:
            print(f"Successfully processed registration: {response.json()}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print(
                f"Failed to process registration: {response.status_code} - {response.text}"
            )
            # Decide if this should be requeued based on the failure type
            # For true capacity issues, don't requeue (waitlist handled elsewhere)
            requeue = "capacity" not in response.text.lower()
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=requeue)

    except Exception as e:
        print(f"Error processing registration request: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_consumer():
    """Start consuming messages from the queue"""
    connection, channel = setup_rabbitmq()

    # Set up quality of service - only process one message at a time
    # This is crucial for the waitlist functionality - process registrations in order
    channel.basic_qos(prefetch_count=1)

    # Set up consumer
    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=False
    )

    print(f"Starting to consume registration requests from {queue_name}...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    except Exception as e:
        print(f"Consumer error: {e}")
    finally:
        connection.close()
        print("Connection closed")

if __name__ == "__main__":
    # Add connection retry logic with increasing backoff
    max_retries = 20
    retry_count = 0

    while retry_count < max_retries:
        try:
            print(f"Attempting to connect to RabbitMQ at {amqp_host}:{amqp_port}")
            start_consumer()
            break
        except pika.exceptions.AMQPConnectionError:
            retry_count += 1
            sleep_time = min(30, 2**retry_count)
            print(
                f"Failed to connect to RabbitMQ. Retrying in {sleep_time} seconds... (Attempt {retry_count}/{max_retries})"
            )
            sleep(sleep_time)

    if retry_count == max_retries:
        print(
            "Failed to connect to RabbitMQ after multiple attempts. Please check if RabbitMQ is running."
        )