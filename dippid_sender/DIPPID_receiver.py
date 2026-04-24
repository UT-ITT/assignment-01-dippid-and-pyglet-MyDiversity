import time
from DIPPID import SensorUDP

# use UDP
PORT = 5700
sensor = SensorUDP(PORT)

# Define how button press/release is handled
def handle_button_press(data):
    if int(data) == 0:
        print('button released')
    else:
        print('button pressed')

sensor.register_callback('button_1', handle_button_press)

# Define how accelerometer data is handled
def handle_accelerometer(data):

    # Check if the sensor has 'accelerometer' capability
    if(sensor.has_capability('accelerometer')):

        # print accelerometer value of every axis
        print('accelerometer X:', sensor.get_value('accelerometer')['x'])
        print('accelerometer Y:', sensor.get_value('accelerometer')['y'])
        print('accelerometer Z:', sensor.get_value('accelerometer')['z'])

sensor.register_callback('accelerometer', handle_accelerometer)

while True:
    time.sleep(10)