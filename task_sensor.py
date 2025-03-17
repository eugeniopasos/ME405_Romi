from pyb import Pin, Timer, ADC
from line_sensor import LineSensor, LineSensorArray
from BNO055 import BNO055
from encoder import Encoder
import time

def find_centroid(nums):
    
    # Finds centroid of sensor array given 7 IR sensors
    a = 0.0
    for i, num in enumerate(nums):
        b = float(num/4096)
        a += b * (i - 2.9)
    return a

def setup_line_sensor():
    
    # Setup Line Sensor Pins
    pin_names = [
        Pin.cpu.C0,
        Pin.cpu.C1,
        Pin.cpu.B0,
        Pin.cpu.A4,
        Pin.cpu.A1,
        Pin.cpu.A0,
        Pin.cpu.B1
        ]
    pins = []
    ctrl_even = Pin.cpu.C11
    ctrl_odd = Pin.cpu.D2

    # Create LineSensor Class array
    for pin_name in pin_names:
        pins.append(LineSensor(pin_name))
    Line_Sensor_Array = LineSensorArray(pins,ctrl_even, ctrl_odd)
    Line_Sensor_Array.set_brightness(90)

    return Line_Sensor_Array

def setup_encoder():
    # Encoder Setup
    timer3 = Timer(3, freq = 1000)
    timer1 = Timer(1, freq = 1000)
    L_Encoder = Encoder(timer3, Pin.cpu.B5, Pin.cpu.B4)
    R_Encoder = Encoder(timer1, Pin.cpu.A9, Pin.cpu.A8)
    L_Encoder.zero()
    R_Encoder.zero()

    return L_Encoder, R_Encoder

def setup_imu():
    # IMU Setup
    SDA_PIN = Pin.cpu.B11
    SCL_PIN = Pin.cpu.B10
    RST_PIN = Pin.cpu.C5

    imu = BNO055(SDA_PIN, SCL_PIN, RST_PIN)
    imu.initialize()
    return imu

def read_sensor(shares):
    # Unpack Shares
    centroid, mode, R_pos, L_pos, heading = shares
   
    # Initalize Sensor
    Line_Sensor_Array = setup_line_sensor()
    L_Encoder, R_Encoder = setup_encoder()
    imu = setup_imu()
    
    while True:
        # Reads line sensor data and computes the centroid
        a = Line_Sensor_Array.read()
        b = find_centroid(a)
        centroid.put(b)

        # Update shares to include encoder positions and headings
        L_Encoder.update()
        R_Encoder.update()

        L_pos.put(L_Encoder.get_position())
        R_pos.put(R_Encoder.get_position())
        heading.put(imu.read_euler()[0])

        yield 0
