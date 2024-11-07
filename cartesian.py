import pika
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# RabbitMQ connection parameters
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_VIRTUAL_HOST = '/'
RABBITMQ_USERNAME = 'camera'
RABBITMQ_PASSWORD = 'camera'
QUEUE_NAMES = ['camera-front', 'camera-side-1']
EXCHANGE_NAME = 'amq.direct'

# Create a figure and axis for plotting
fig, ax = plt.subplots()

def update_plot(data, queue_name):
    # Clear the previous plot
    ax.clear()

    # Draw the car icon at the origin (0, 0)
    car_size = 2  # Size of the car box (2x2)
    car_icon = patches.Rectangle((-car_size / 2, -car_size / 2), car_size, car_size, linewidth=2, edgecolor='blue', facecolor='blue')
    ax.add_patch(car_icon)

    # Annotate the car position
    ax.annotate('Car (0,0)', (0, 0), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='lightblue'))

    # Draw obstacles from the received data
    for item in data:
        x1 = item['x1']
        y1 = item['y1']
        x2 = item['x2']
        y2 = item['y2']
        name = item.get('name', 'Obstacle')  # Get the name from the data, default to 'Obstacle' if not provided
        
        # Calculate the center of the obstacle
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        # Apply transformations based on the queue name
        if queue_name == 'camera-front':
            center_x -= 640  # For camera front
            color = 'red'  # Set color to red for camera front
        elif queue_name == 'camera-side-1':
            center_x = center_y - 640   # For camera side 1
            center_y = center_x - 640
            color = 'blue'  # Set color to blue for camera side 1

        # Calculate distance from the car to the center of the obstacle
        distance = np.sqrt(center_x**2 + center_y**2)

        # Create a rectangle for the obstacle
        obstacle = patches.Rectangle((center_x, center_y), x2 - x1, y2 - y1, linewidth=1, edgecolor=color, facecolor=color, alpha=0.5)
        ax.add_patch(obstacle)

        # Annotate the obstacle with its name and distance
        # ax.annotate(f'{name}\nDistance: {distance:.2f}\nX: {center_x:.2f} Y: {center_y:.2f}', (center_x, center_y), 
        #             textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, 
        #             bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='lightgrey'))

    # Set limits and labels to -1500 to 1500
    ax.set_xlim(-1500, 1500)  # Original x-coordinates on the x-axis
    ax.set_ylim(-1500, 1500)  # Distances on the y-axis
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Obstacles')

    # Redraw the grid and axes
    plt.grid()
    plt.axhline(0, color='black', linewidth=0.5, ls='--')
    plt.axvline(0, color='black', linewidth=0.5, ls='--')

    # Draw the updated plot
    plt.draw()
    plt.pause(0.1)

def callback(ch, method, properties, body):
    # Parse the incoming message
    queue_name = method.routing_key  # Get the queue name from the routing key
    if(queue_name == 'camera-front'):
        data = json.loads(body)
        update_plot(data, 'camera-front')
    elif(queue_name == 'camera-side-1'):
        data = json.loads(body)
        update_plot(data, 'camera-side-1')

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