import pika
import keyboard
import argparse
 
# Argument parser setup
parser = argparse.ArgumentParser(description='Megabot Control')
parser.add_argument('rmq_server', type=str, help='RabbitMQ Server Host IP Address / Domain')
parser.add_argument('queue_name', type=str, help='Queue Name')  # Changed to str for queue name
args = parser.parse_args()
 
# RabbitMQ connection parameters
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=args.rmq_server,
        port=5672,
        virtual_host='/megabot',
        credentials=pika.PlainCredentials('megabot', '12345678'),
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
    1: {'max_pwm_straight': 180, 'max_pwm_turn': 180, 'max_pwm_backward': 180},
    2: {'max_pwm_straight': 215, 'max_pwm_turn': 200, 'max_pwm_backward': 215},
    3: {'max_pwm_straight': 230, 'max_pwm_turn': 215, 'max_pwm_backward': 230}
}
 
# Motor Direction
motor_direction = "e"
 
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
            if(motor_direction == "e"):
                message = bytes([max_pwm_straight, max_pwm_straight, 101, 101])
                publish_message(message)
                print(f"Forward using Power L = {max_pwm_straight} R = {max_pwm_straight}")
            elif(motor_direction == "r"):
                message = bytes([0, 0, 114, 114])
                publish_message(message)
                print(f"Forward using Power L = 0 R = 0")
        elif event.name == 's':
            if(motor_direction == "e"):
                message = bytes([0, 0, 101, 101])
                publish_message(message)
                print(f"Backward using Power L = 0 R = 0")
            elif(motor_direction == "r"):
                message = bytes([max_pwm_backward, max_pwm_backward, 114, 114])
                publish_message(message)
                print(f"Backward using Power L = {max_pwm_backward} R = {max_pwm_backward}")
        elif event.name == 'a':
            if(motor_direction == "e"):
                message = bytes([0, max_pwm_turn, 101, 101])
                publish_message(message)
                print(f"Left using Power L = 0 R = {max_pwm_turn}")
            elif(motor_direction == "r"):
                message = bytes([max_pwm_backward, 0, 114, 114])
                publish_message(message)
                print(f"Left using Power L = {max_pwm_backward} R = 0")
        elif event.name == 'd':
            if(motor_direction == "e"):
                message = bytes([max_pwm_turn, 0, 101, 101])
                publish_message(message)
                print(f"Right using Power L = {max_pwm_turn} R = 0")
            if(motor_direction == "r"):
                message = bytes([0, max_pwm_backward, 114, 114])
                publish_message(message)
                print(f"Right using Power L = 0 R = {max_pwm_backward}")
        elif event.name in ['1', '2', '3']:
            current_gear = int(event.name)
            print(f"Gear changed to: {current_gear}")
            print(f"Gear Settings {current_gear} = {gear_settings[current_gear]}")
        elif event.name == 'e' or event.name == 'r':
            motor_direction = event.name
            print(f"Motor direction {event.name}")
 
# initiation
print(f"Program Start using Gear Settings {current_gear} = {gear_settings[current_gear]} and Direction = {motor_direction}")
 
# Register keyboard event handler
keyboard.on_press(handle_keyboard_input)
 
# Start listening for keyboard events
keyboard.wait()