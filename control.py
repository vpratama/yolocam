import pika
import keyboard
import argparse

# Argument parser setup
parser = argparse.ArgumentParser(description='Megabot Control')
parser.add_argument('queue_name', type=str, help='Queue Name')  # Changed to str for queue name
args = parser.parse_args()

# RabbitMQ connection parameters
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        port=5672,
        virtual_host='/',
        credentials=pika.PlainCredentials('control', 'control'),
        heartbeat=600
    )
)
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue=args.queue_name, durable=True, auto_delete=True)

# Bind the queue to the exchange with the routing key
channel.queue_bind(exchange='amq.topic', queue=args.queue_name, routing_key=args.queue_name)

# Gear settings
gear_settings = {
    1: {'max_pwm_straight': 70, 'max_pwm_turn': 35, 'max_pwm_backward': 10},
    2: {'max_pwm_straight': 140, 'max_pwm_turn': 70, 'max_pwm_backward': 30},
    3: {'max_pwm_straight': 255, 'max_pwm_turn': 140, 'max_pwm_backward': 50}
}

# Motor Direction
motor_direction = "+"

# Current gear
current_gear = 1

# Function to publish message to RabbitMQ
def publish_message(message):
    channel.basic_publish(exchange='amq.topic', routing_key=args.queue_name, body=message)
    print("Message published:", message)

# Function to handle keyboard input
def handle_keyboard_input(event):
    global current_gear 
    global motor_direction
    max_pwm_straight = gear_settings[current_gear]['max_pwm_straight']
    max_pwm_turn = gear_settings[current_gear]['max_pwm_turn']
    max_pwm_backward = gear_settings[current_gear]['max_pwm_backward']
    
    message = ''
    
    if event.event_type == keyboard.KEY_DOWN:
        if event.name == 'w':
            if(motor_direction == "+"):
                message = chr(max_pwm_straight) + chr(max_pwm_straight) + chr(43) + chr(43)
                publish_message(message.encode('utf-8'))
                print(f"Forward using Power L = {max_pwm_straight} R = {max_pwm_straight}")
            elif(motor_direction == "-"):
                message = chr(0) + chr(0) + chr(45) + chr(45)
                publish_message(message.encode('utf-8'))
                print(f"Forward using Power L = 0 R = 0")
        elif event.name == 's':
            if(motor_direction == "+"):
                message = chr(0) + chr(0) + chr(43) + chr(43)
                publish_message(message.encode('utf-8'))
                print(f"Backward using Power L = 0 R = 0")
            elif(motor_direction == "-"):
                message = chr(max_pwm_backward) + chr(max_pwm_backward) + chr(45) + chr(45)
                publish_message(message.encode('utf-8'))
                print(f"Backward using Power L = {max_pwm_backward} R = {max_pwm_backward}")
        elif event.name == 'a':
            if(motor_direction == "+"):
                message = chr(0) + chr(max_pwm_turn) + chr(43) + chr(43)
                publish_message(message.encode('utf-8'))
                print(f"Left using Power L = 0 R = {max_pwm_turn}")
            elif(motor_direction == "-"):
                message = chr(max_pwm_backward) + chr(0) + chr(45) + chr(45)
                publish_message(message.encode('utf-8'))
                print(f"Left using Power L = {max_pwm_backward} R = 0")
        elif event.name == 'd':
            if(motor_direction == "+"):
                message = chr(max_pwm_turn) + chr(0) + chr(43) + chr(43)
                publish_message(message.encode('utf-8'))
                print(f"Right using Power L = {max_pwm_turn} R = 0")
            if(motor_direction == "-"):
                message = chr(0) + chr(max_pwm_backward) + chr(45) + chr(45)
                publish_message(message.encode('utf-8'))
                print(f"Right using Power L = 0 R = {max_pwm_backward}")
        elif event.name in ['1', '2', '3']:
            current_gear = int(event.name)
            print(f"Gear changed to: {current_gear}")
            print(f"Gear Settings {current_gear} = {gear_settings[current_gear]}")
        elif event.name == '+' or event.name == '-':
            motor_direction = event.name
            print(f"Motor direction {event.name}")

# initiation
print(f"Program Start using Gear Settings {current_gear} = {gear_settings[current_gear]} and Direction = {motor_direction}")

# Register keyboard event handler
keyboard.on_press(handle_keyboard_input)

# Start listening for keyboard events
keyboard.wait()