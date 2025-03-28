import pika

amqp_host = "localhost"
amqp_port = 5672
exchange_name = "hangout_exchange"
exchange_type = "topic"

def create_connection():
    print(f"Connecting to AMQP broker {amqp_host}:{amqp_port}...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=amqp_host,
            port=amqp_port,
            heartbeat=300,
            blocked_connection_timeout=300,
        )
    )
    print("Connected")
    return connection

def create_exchange(connection):
    print("Opening channel")
    channel = connection.channel()
    
    # Set up the exchange if it doesn't exist
    print(f"Declaring exchange: {exchange_name}")
    channel.exchange_declare(
        exchange=exchange_name, exchange_type=exchange_type, durable=True
    )
    return channel

def create_queue(channel, queue_name, routing_key):
    print(f"Binding to queue: {queue_name}")
    channel.queue_declare(queue=queue_name, durable=True)
    
    # Bind the queue to the exchange via the routing_key
    channel.queue_bind(
        exchange=exchange_name, queue=queue_name, routing_key=routing_key
    )

# Create a default connection and channel
connection = create_connection()
channel = create_exchange(connection)

# Define queues
create_queue(channel, queue_name="inbox_messages", routing_key="inbox.#")
create_queue(channel, queue_name="event_joins", routing_key="event.join.#")

def get_channel():
    connection = create_connection()
    return create_exchange(connection), connection