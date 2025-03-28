import json
import pika
from amqp_setup import get_channel

class MessageConsumer:
    def __init__(self, queue_name, callback):
        """
        Initialize a consumer for the specified queue.
        
        Args:
            queue_name: Name of the queue to consume messages from
            callback: Function to process messages (receives message body as parsed JSON)
        """
        self.queue_name = queue_name
        self.user_callback = callback
        self.channel, self.connection = get_channel()
        
    def _process_message(self, ch, method, properties, body):
        """Internal callback that handles message processing"""
        try:
            message = json.loads(body)
            print(f"Received message with routing key '{method.routing_key}': {message}")
            
            # Call the user-provided callback with the parsed message
            self.user_callback(message, method.routing_key)
            
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            # Negative acknowledgment, requeue the message
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self):
        """Start consuming messages from the queue"""
        try:
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self._process_message,
                auto_ack=False
            )
            print(f"Started consuming from queue: {self.queue_name}")
            print("Waiting for messages. To exit press CTRL+C")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("Consumer stopped by user")
            self.connection.close()
        except Exception as e:
            print(f"Error in consumer: {str(e)}")
            self.connection.close()

# Example usage
# def handle_inbox_message(message, routing_key):
#     print(f"Processing inbox message: {message}")
#     # Your message handling logic here
#
# consumer = MessageConsumer("inbox_messages", handle_inbox_message)
# consumer.start_consuming()