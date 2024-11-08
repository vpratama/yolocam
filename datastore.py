import pika
import json

# initialize parameter
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_VIRTUAL_HOST = '/'
RABBITMQ_USERNAME = 'camera'
RABBITMQ_PASSWORD = 'camera'
QUEUE_NAMES = ['camera-front', 'camera-side-1', 'camera-side-2', 'camera-back']
EXCHANGE_NAME = 'amq.direct'

# json container
camera = {
    "camera-front": None,
    "camera-side-1": None,
    "camera-side-2": None,
    "camera-back": None
}

def callback(ch, method, properties, body):
    # Parse the incoming message
    queue_name = method.routing_key  # Get the queue name from the routing key
    if(queue_name == 'camera-front'):
        data = json.loads(body)
        camera['camera-front'] = data
    elif(queue_name == 'camera-side-1'):
        data = json.loads(body)
        camera['camera-side-1'] = data
    elif(queue_name == 'camera-side-2'):
        data = json.loads(body)
        camera['camera-side-2'] = data
    elif(queue_name == 'camera-back'):
        data = json.loads(body)
        camera['camera-back'] = data

    # if data complete then process as whole
    if (camera['camera-front'] and 
        camera['camera-side-1']):
        # camera['camera-side-1'] and 
        # camera['camera-side-2'] and 
        # camera['camera-back']):
        store(camera)

def store(json):
    print(json)
    camera['camera-front'] = None
    camera['camera-side-1'] = None
    camera['camera-side-2'] = None
    camera['camera-back'] = None
    
def main():
    # Establish connection to RabbitMQ with credentials
    credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            virtual_host=RABBITMQ_VIRTUAL_HOST,
            credentials =credentials
        )
    )
    channel = connection.channel()

    # Declare the queues (make sure they exist)
    for queue_name in QUEUE_NAMES:
        channel.queue_declare(queue=queue_name)

    # Bind the queues to the exchange with the routing key
    for queue_name in QUEUE_NAMES:
        channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=queue_name)

    # Subscribe to the queues
    for queue_name in QUEUE_NAMES:
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    main()