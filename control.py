import pika
import keyboard
import argparse
import threading
import time
import sys
import json

# Argument parser setup
parser = argparse.ArgumentParser(description='Megabot Control')
parser.add_argument('rmq_server', type=str, help='RabbitMQ Server Host IP Address / Domain')
parser.add_argument('queue_name', type=str, help='Queue Name')
parser.add_argument('queue_name_camera', type=str, help='Queue Name Camera')
args = parser.parse_args()

camera_data = None
exit_program = False  # Flag to indicate when to exit

# RabbitMQ connection parameters
def create_connection():
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=args.rmq_server,
            port=5672,
            virtual_host='/megabot',
            credentials=pika.PlainCredentials('megabot', '12345678'),
            heartbeat=600
        )
    )

# Function to publish message to RabbitMQ
def publish_message(channel, message):
    try:
        channel.basic_publish(exchange='amq.topic', routing_key=args.queue_name, body=message)
        print("Message published:", message)
    except pika.exceptions.ChannelClosed:
        print("Channel is closed, trying to reconnect...")
        reconnect_channel()

# Global variables
connection = create_connection()
channel = connection.channel()
channel.queue_declare(queue=args.queue_name, durable=True, auto_delete=True)
channel.queue_bind(exchange='amq.topic', queue=args.queue_name, routing_key=args.queue_name)

# Bind the camera queue
channel.queue_declare(queue=args.queue_name_camera, durable=True, auto_delete=True)
channel.queue_bind(exchange='amq.direct', queue=args.queue_name_camera, routing_key=args.queue_name_camera)

# Gear settings
gear_settings = {
    1: {'max_pwm_straight': 180, 'max_pwm_turn': 180, 'max_pwm_backward': 180, 'max_pwm_braking': 90},
    2: {'max_pwm_straight': 215, 'max_pwm_turn': 200, 'max_pwm_backward': 215, 'max_pwm_braking': 125},
    3: {'max_pwm_straight': 230, 'max_pwm_turn': 215, 'max_pwm_backward': 230, 'max_pwm_braking': 150}
}

# Motor Direction
motor_direction = "e"
current_gear = 1

# Function to handle incoming messages from RabbitMQ
def callback(ch, method, properties, body):
    global camera_data
    camera_data = json.loads(body)

# Function to start consuming messages
def start_consuming():
    channel.basic_consume(queue=args.queue_name_camera, on_message_callback=callback, auto_ack=True)
    print("Waiting for messages. To exit press F4")
    try:
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError:
        print("Connection lost, attempting to reconnect...")
        reconnect_channel()

# Function to handle reconnection
def reconnect_channel():
    global connection, channel
    while True:
        try:
            connection = create_connection()
            channel = connection.channel()
            channel.queue_declare(queue=args.queue_name, durable=True, auto_delete=True)
            channel.queue_bind(exchange='amq.topic', queue=args.queue_name, routing_key=args.queue_name)
            print("Reconnected to RabbitMQ")
            break
        except Exception as e:
            print(f"Reconnection failed: {e}")
            time.sleep(5)  # Wait before trying to reconnect

# Function to handle keyboard input
def handle_keyboard_input(event):
    global camera_data
    global current_gear, motor_direction
    global forward_stop, left_stop, right_stop, back_stop
    global detection_soft_treshold, detection_hard_treshold
    global front_cam_distance, left_cam_distance, right_cam_distance, back_cam_distance

    max_pwm_straight = gear_settings[current_gear]['max_pwm_straight']
    max_pwm_turn = gear_settings[current_gear]['max_pwm_turn']
    max_pwm_backward = gear_settings[current_gear]['max_pwm_backward']
    max_pwm_braking = gear_settings[current_gear]['max_pwm_braking']

    detection_soft_treshold = 2
    detection_hard_treshold = 1

    front_cam_distance = 0
    left_cam_distance = 0
    right_cam_distance = 0
    back_cam_distance = 0

    forward_stop = False
    left_stop = False
    right_stop = False
    back_stop = False

    if(camera_data is not None and camera_data['camera-front'] != []):
        for cam in camera_data['camera-front']:
            front_cam_distance = cam['distance']
            if front_cam_distance < detection_soft_treshold:
                forward_stop = True
                print('Force stop forward, obstacle detected')
            elif front_cam_distance < detection_hard_treshold:
                forward_stop = True
                print('Force stop forward, obstacle detected')
            else:
                forward_stop = False

    if(camera_data is not None and camera_data['camera-side-1'] != []):
        for cam in camera_data['camera-side-1']:
            left_cam_distance = cam['distance']
            if left_cam_distance < detection_soft_treshold:
                left_stop = True
                print('Force stop left, obstacle detected')
            elif left_cam_distance < detection_hard_treshold:
                left_stop = True
                print('Force stop left, obstacle detected')
            else:
                left_stop = False

    if(camera_data is not None and camera_data['camera-side-2'] != []):
        for cam in camera_data['camera-side-2']:
            right_cam_distance = cam['distance']
            if right_cam_distance < detection_soft_treshold:
                right_stop = True
                print('Force stop right, obstacle detected')
            elif right_cam_distance < detection_hard_treshold:
                right_stop = True
                print('Force stop right, obstacle detected')
            else:
                right_stop = False

    if(camera_data is not None and camera_data['camera-back'] != []):
        for cam in camera_data['camera-back']:
            back_cam_distance = cam['distance']
            if back_cam_distance < detection_soft_treshold:
                back_stop = True
                print('Force stop backward, obstacle detected')
            elif back_cam_distance < detection_hard_treshold:
                back_stop = True
                print('Force stop backward, obstacle detected')
            else:
                back_stop = False
    
    message = b''  # Initialize message as bytes
    
    if event.event_type == keyboard.KEY_DOWN:
        if event.name == 'w':
            if motor_direction == "e" and forward_stop == False:
                message = bytes([max_pwm_straight, max_pwm_straight, 101, 101])
                publish_message(channel, message)
                print(f"Forward using Power L = {max_pwm_straight} R = {max_pwm_straight}")
            elif motor_direction == "e" and forward_stop == True:
                message = bytes([max_pwm_braking, max_pwm_braking, 114, 114])
                publish_message(channel, message)
                print(f"Hard Braking Using Backward Direction with power {max_pwm_braking}")
            elif motor_direction == "r" and back_stop == False:
                message = bytes([0, 0, 114, 114])
                publish_message(channel, message)
                print(f"Forward using Power L = 0 R = 0")
            elif motor_direction == "r" and back_stop == True:
                message = bytes([max_pwm_braking, max_pwm_braking, 101, 101])
                publish_message(channel, message)
                print(f"Hard Braking Using Forward Direction with power {max_pwm_braking}")
        elif event.name == 's' and back_stop == False:
            if motor_direction == "e" and back_stop == False:
                message = bytes([0, 0, 101, 101])
                publish_message(channel, message)
                print(f"Backward using Power L = 0 R = 0")
            elif motor_direction == "e" and back_stop == True:
                message = bytes([max_pwm_braking, max_pwm_braking, 101, 101])
                publish_message(channel, message)
                print(f"Hard Braking Using Forward Direction with power {max_pwm_braking}")
            elif motor_direction == "r" and forward_stop == False:
                message = bytes([max_pwm_backward, max_pwm_backward, 114, 114])
                publish_message(channel, message)
                print(f"Backward using Power L = {max_pwm_backward} R = {max_pwm_backward}")
            elif motor_direction == "r" and forward_stop == True:
                message = bytes([max_pwm_braking, max_pwm_braking, 114, 114])
                publish_message(channel, message)
                print(f"Hard Braking Using Backward Direction with power {max_pwm_braking}")
        elif event.name == 'a':
            if motor_direction == "e" and left_stop == False:
                message = bytes([0, max_pwm_turn, 101, 101])
                publish_message(channel, message)
                print(f"Left using Power L = 0 R = {max_pwm_turn}")
            elif motor_direction == "e" and left_stop == True:
                message = bytes([max_pwm_braking, max_pwm_braking, 114, 114])
                publish_message(channel, message)
                print(f"Hard Braking Using Backward Direction with power {max_pwm_braking}")
            elif motor_direction == "r" and right_stop == False:
                message = bytes([max_pwm_backward, 0, 114, 114])
                publish_message(channel, message)
                print(f"Left using Power L = {max_pwm_backward} R = 0")
            elif motor_direction == "r" and right_stop == True:
                message = bytes([max_pwm_braking, max_pwm_braking, 101, 101])
                publish_message(channel, message)
                print(f"Hard Braking Using Forward Direction with power {max_pwm_braking}")
        elif event.name == 'd':
            if motor_direction == "e" and right_stop == False:
                message = bytes([max_pwm_turn, 0, 101, 101])
                publish_message(channel, message)
                print(f"Right using Power L = {max_pwm_turn} R = 0")
            elif motor_direction == "e" and right_stop == True:
                message = bytes([max_pwm_braking, max_pwm_braking, 114, 114])
                publish_message(channel, message)
                print(f"Hard Braking Using Backward Direction with power {max_pwm_braking}")
            elif motor_direction == "r" and left_stop == False:
                message = bytes([0, max_pwm_backward, 114, 114])
                publish_message(channel, message)
                print(f"Right using Power L = 0 R = {max_pwm_backward}")
            elif motor_direction == "r" and left_stop == True:
                message = bytes([max_pwm_braking, max_pwm_braking, 101, 101])
                publish_message(channel, message)
                print(f"Hard Braking Using Forward Direction with power {max_pwm_braking}")
        elif event.name == 'shift':
            if motor_direction == "e":
                message = bytes([max_pwm_braking, max_pwm_braking, 114, 114])
                publish_message(channel, message)
                print(f"Hard Braking Using Backward Direction with power {max_pwm_braking}")
            elif motor_direction == "r":
                message = bytes([max_pwm_braking, max_pwm_braking, 101, 101])
                publish_message(channel, message)
                print(f"Hard Braking Using Forward Direction with power {max_pwm_braking}")
        elif event.name in ['1', '2', '3']:
            current_gear = int(event.name)
            print(f"Gear changed to: {current_gear}")
            print(f"Gear Settings {current_gear} = {gear_settings[current_gear]}")
        elif event.name in ['e', 'r']:
            motor_direction = event.name
            print(f"Motor direction {event.name}")
        elif event.name == 'f4':  # Check for F4 key press
            global exit_program
            exit_program = True  # Set the exit flag

# Start the consumer in a separate thread
consumer_thread = threading.Thread(target=start_consuming)
consumer_thread.start()

# Initiation
print(f"Program Start using Gear Settings {current_gear} = {gear_settings[current_gear]} and Direction = {motor_direction}")

# Register keyboard event handler
keyboard.on_press(handle_keyboard_input)

# Main loop to check for exit condition
while not exit_program:
    time.sleep(0.1)  # Sleep briefly to avoid busy waiting

# Cleanup before exiting
print("Exiting program...")
channel.stop_consuming()
connection.close()
sys.exit(0)