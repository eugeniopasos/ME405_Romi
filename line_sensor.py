from pyb import Pin, ADC
import time
class LineSensorArray:

    def __init__(self, pins, ctrl_even, ctrl_odd):
        # Sets up control pins and initializes variables
        self.pins = pins
        self.ctrl_even = Pin(ctrl_even, mode = Pin.OUT_PP)
        self.ctrl_odd = Pin(ctrl_odd, mode = Pin.OUT_PP)
        self.brightness = 100
        
    def read(self):
        # Reads ADC values from all pins
        readings = [0] * len(self.pins)
        for i, pin in enumerate(self.pins):
            readings[i] = pin.adc.read()
        # Returns array of ADC values
        return readings
    
    def set_brightness(self, brightness):
        # Sets brightness of IR Blaster
        self.brightness = brightness
        num = int(((100 - brightness)/100)*32)
        for i in range(num):
            self.ctrl_even.low()
            self.ctrl_odd.low()
            time.sleep_us(1)
            self.ctrl_even.high()
            self.ctrl_odd.high()
            time.sleep_us(1)


class LineSensor:
    # Creates class for IR Sensor
    def __init__(self, pin):
        self.pin = Pin(pin,  mode = Pin.ANALOG)
        self.adc = ADC(self.pin)


class PIDController:
    def __init__(self, Kp, Ki, Kd):
        # Initialize gains (tuned for position control in mm)
        self.Kp = Kp
        self.Ki = Ki 
        self.Kd = Kd
        # Initialize error terms
        self.error_integral = 0
        self.error_prev = 0
        # ms to comply with task period
        self.dt = 0.01
    def compute_pid(self, error):
        P = self.Kp * error
        self.error_integral += error*self.dt
        I = self.Ki * self.error_integral
        D = self.Kd * ((error - self.error_prev)/self.dt)
        self.error_prev = error
        return P + I + D
