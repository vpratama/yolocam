import pika
import keyboard

# RabbitMQ connection parameters
credentials = pika.PlainCredentials('TMDG2022', 'TMDG2022')
parameters = pika.ConnectionParameters('rmq2.pptik.id', '5672', '/TMDG2022', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Queue name
queue_name = 'Aktuator'

# Function to publish message to RabbitMQ
def publish_message(message):
    channel.basic_publish(exchange='amq.topic', routing_key=queue_name, body=message)
    print("Message published:", message)

# Function to handle keyboard input
def handle_keyboard_input(event):
    if event.event_type == keyboard.KEY_DOWN:
        if event.name == 'w':
            message = 'xxFF'
            publish_message(message.encode('utf-8'))
            print("Forward")
        elif event.name == 's':
            message = 'xxBB'
            publish_message(message.encode('utf-8'))
            print("Backward")
        elif event.name == 'a':
            message = 'xxBF'
            publish_message(message.encode('utf-8'))
            print("Left")
        elif event.name == 'd':
            message = 'xxFB'
            publish_message(message.encode('utf-8'))
            print("Right")
        
# initiation
print("Program Start")

# Register keyboard event handler
keyboard.on_press(handle_keyboard_input)

# Start listening for keyboard events
keyboard.wait()