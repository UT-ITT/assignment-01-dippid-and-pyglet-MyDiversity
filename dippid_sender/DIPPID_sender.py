import socket
import time
import random
import threading
import math
import json

IP = '127.0.0.1'
PORT = 5700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# sends button press signal randomly every 1-5 seconds

def send_random_button1_press():

    # messages for Button press and release
    message_press = '{"button_1": ' + str(1)  + '}'
    message_release = '{"button_1": ' + str(0) + '}'

    while True:
        # Computes a random holding time for the button press
        hold_time = random.uniform(1, 3)

        # sends button press
        print(message_press)
        sock.sendto(message_press.encode(),(IP, PORT))

        # holds button
        print(f'hold for {hold_time} seconds')
        time.sleep(hold_time)

        #releases button
        print(message_release)
        sock.sendto(message_release.encode(),(IP, PORT))

        # Computes a random pause of 1 to 5 seconds between presses
        waiting_time = random.uniform(1, 5)
        print(f'wait for {waiting_time} to press again')
        time.sleep(waiting_time)

def accelerometer_sinus_sample(frequency):
    # specify basic sinus parameters
    t = time.time()

    # calculate sinus value at time t
    value = math.sin(2*math.pi * frequency * t)

    return value

def send_accelerometer_sample():

    # Set different frequencies for each axis to receive different functions
    x_freq = 1
    y_freq = 1.5
    z_freq = 2

    while True:
        # send accelerometer value in json format as encode()-function requires string format
        message_accelerometer = json.dumps ({
                            "accelerometer": {
                                "x": accelerometer_sinus_sample(x_freq),
                                "y": accelerometer_sinus_sample(y_freq),
                                "z": accelerometer_sinus_sample(z_freq)
                            } 
        })
        sock.sendto(message_accelerometer.encode(),(IP, PORT))
        
        # Print accelerometer content
        print(message_accelerometer)

        # set smaller sleep value to ensure smoother function curve
        time.sleep(0.5)

# Start threads to allow simultaneous sending of both values
threading.Thread(target = send_random_button1_press, daemon=True).start()
threading.Thread(target = send_accelerometer_sample, daemon=True).start()

while True:
    time.sleep(10)

