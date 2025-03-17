from time import ticks_us, ticks_diff 
from pyb import Timer
class Encoder:

    def __init__(self, tim, chA_pin, chB_pin):
        
        self.timer = tim
        self.timch1 = self.timer.channel(1, Timer.ENC_AB, pin = chA_pin)
        self.timch2 = self.timer.channel(2, Timer.ENC_AB, pin = chB_pin)

        self.position   = 0 # Total accumulated position of the encoder
        self.prev_count = 0 # Previous Timer Count
        self.delta      = 0 # Change in count
        self.prev_t     = 0 # Previous time from last update
        self.dt         = 0 # Change in Timer

    def update(self):
        
        self.delta = self.timer.counter() - self.prev_count
        if self.delta > 8000:
            self.delta -= 16000
        if self.delta < -8000:
            self.delta += 16000
        
        self.position += self.delta 
        
        self.prev_count = self.timer.counter()
        self.dt = (ticks_us() - self.prev_t)/1_000_000
        self.prev_t = ticks_us()

    def get_position(self):
        return self.position
    
    def get_velocity(self):
        return self.delta/self.dt
    
    def zero(self):
        self.position   = 0
        self.prev_count = self.timer.counter()# Previous Timer Count
        self.delta      = 0 # Change in count
        self.prev_t     = ticks_us() # Previous time from last update
        self.dt         = 0 # Change in Timer