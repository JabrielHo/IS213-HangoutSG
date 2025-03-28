import json
import pika
from amqp_setup import exchange_name, get_channel

class MessageProducer:
    def __init__(self):
        self.channel, self.connection = get_channel()
        
    def publish_message(self, routing_key, message):
        """
        Publishes a message to the exchange with the given routing key.
        
        Args:
            routing_key: The routing key for message routing
            message: The message payload (will be converted to JSON)
        """
        try:
            self.channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json'
                )
            )
            print(f"Published message with routing key '{routing_key}': {message}")
            return True
        except Exception as e:
            print(f"Error publishing message: {str(e)}")
            return False
    
    def close(self):
        """Close the connection"""
        if self.connection and self.connection.is_open:
            self.connection.close()

# Example usage
# producer = MessageProducer()
# producer.publish_message("inbox.new", {"user_id": "123", "content": "Hello!"})
# producer.close()