import pika
import json
import os


def publish_to_inbox(message):
    try:
        amqp_host = os.environ.get("RABBITMQ_HOST", "localhost")
        amqp_port = int(os.environ.get("RABBITMQ_PORT", 5672))
        exchange_name = os.environ.get("EXCHANGE_NAME", "hangout_exchange")
        routing_key = os.environ.get("ROUTING_KEY", "inbox_message")

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=amqp_host, port=amqp_port)
        )
        channel = connection.channel()

        # Convert message to JSON and publish
        message_json = json.dumps(message)
        channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=message_json,
            properties=pika.BasicProperties(
                delivery_mode=2,
            ),
        )

        connection.close()
    except Exception as e:
        print(f"Error publishing message to inbox: {e}")


publish_to_inbox(
    {
        "type": "report_outcome",
        "receiver_id": "auth0|67cd8623469fee2d24e73bfb",
        "subject": "Report Outcome",
        "content": "Your report was successful",
    }
)


publish_to_inbox(
    {
        "type": "event_creation",
        "receiver_ids": [
            "auth0|67cd8623469fee2d24e73bfb",
            "auth0|67ee225a0e55bc13f7a2dd17",
        ],
        "subject": "New cycling event created in your community!",
        "content": "A cycling event by userid has been created",
    }
)
