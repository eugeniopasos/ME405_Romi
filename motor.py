from pyb import Pin, Timer

class Motor:
    def __init__(self, PWM, DIR, nSLP, TimerChannel):
        # Initialize Pins
        self.nSLP_pin = Pin(nSLP, mode=Pin.OUT_PP, value=0)
        self.DIR_pin = Pin(DIR, mode=Pin.OUT_PP, value=0)
        self.PWM_pin = Pin(PWM, mode = Pin.ALT, alt = 3)     
        self.TC = TimerChannel

    def set_effort(self, effort):
        # Change direction pin based on if input is positive or negative
        # Forward = +
        # Reverse = -
        if effort >= 0:
            self.DIR_pin.low()
        else:
            self.DIR_pin.high()

        # Limit Effort to 60%
        if abs(effort) >= 60:
            effort = 60
            
        self.TC.pulse_width_percent(abs(effort))

    def enable(self):
        self.nSLP_pin.high()

    def disable(self):
        self.nSLP_pin.low()
