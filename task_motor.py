from pyb import Pin, Timer, ADC
from motor import Motor
from line_sensor import PIDController
import time

# FSM Modes
LINE, AVOID, BUMP, ALIGN = 0, 1, 2, 3

def setup_bump():
    # Setup bump sensors
    bumpL1 = Pin(Pin.cpu.C2, Pin.IN,Pin.PULL_UP)
    bumpL2 = Pin(Pin.cpu.H1, Pin.IN,Pin.PULL_UP)
    bumpL3 = Pin(Pin.cpu.H0, Pin.IN,Pin.PULL_UP)
    bumpR1 = Pin(Pin.cpu.C12, Pin.IN,Pin.PULL_UP)
    bumpR2 = Pin(Pin.cpu.C10, Pin.IN,Pin.PULL_UP)
    bumpR3 = Pin(Pin.cpu.B7, Pin.IN,Pin.PULL_UP)
    return [bumpL1, bumpL2, bumpL3, bumpR1, bumpR2, bumpR3]

def drive_motor(shares):
    # Motor Setup
    timer8 = Timer(8, freq = 20000)
    tim8ch1 = timer8.channel(1, Timer.PWM, pulse_width_percent = 10)
    tim8ch2 = timer8.channel(2, Timer.PWM, pulse_width_percent = 10)
    R_Motor = Motor(Pin.cpu.C7, Pin.cpu.C8,  Pin.cpu.C9, tim8ch1)
    L_Motor = Motor(Pin.cpu.C6, Pin.cpu.A10, Pin.cpu.B3, tim8ch2)

    Vin_pin = Pin(Pin.cpu.C4,  mode = Pin.ANALOG)
    Vin = ADC(Vin_pin)
    V = (Vin.read() / 4095.0)
 
    # PID Values for tuning
    Kp = 22/V # Scaled by the inverse of the voltage percentage
    Ki = 0.03
    Kd = 0.3
    PID = PIDController(Kp,Ki,Kd)

    # Unpack the shares
    centroid, mode, R_pos, L_pos, heading = shares

    # Setup the bump sensors
    bumps = setup_bump()

    # Motor Initlization
    base_speed = 12

    L_Motor.set_effort(base_speed)
    R_Motor.set_effort(base_speed)

    L_Motor.enable()
    R_Motor.enable()
    L_last = 0
    R_last = 0
    j = 0
    direction = 0
    diamond_flag = 1

    while True:
        # Get current encoder position and IMU heading information
        rpos = R_pos.get()
        lpos = L_pos.get()
        head = heading.get()

        # Line Mode: Follow the line using the centroid
        if mode.get() == LINE:

            # Check for specific heading corresponding to location of the diamond
            # If heading is reached, go forward and clear diamond flag
            if (head >= 82 and head <= 95) and (diamond_flag == 1):
                R_Motor.set_effort(10)
                L_Motor.set_effort(10)
                time.sleep(0.37)
                diamond_flag = 0

            # Check encoder counts for frame section of the course
            elif ((rpos >= 4150) and (lpos >= 4900)) and (head >= 176 and head <= 184):
                R_last = R_pos.get()
                L_last = L_pos.get()
                R_Motor.set_effort(0)
                L_Motor.set_effort(0)
                # Set to avoid mode  
                mode.put(AVOID)
                direction = 180
            
            else:
                # Get the line sensor data and compute PID of error signal
                error = centroid.get()
                control_signal = PID.compute_pid(error)

                # If control signal is negative, Romi must turn right
                if control_signal < 0:
                    L_Motor.set_effort(base_speed + abs(control_signal))
                    R_Motor.set_effort(base_speed)

                # If control signal is positive, Romi must turn left
                else:
                    R_Motor.set_effort(base_speed + abs(control_signal))
                    L_Motor.set_effort(base_speed)

                
                # Check if bump sensor was triggered
                for pin in bumps:
                    if pin.value() == 0:
                        mode.put(BUMP)
                        yield 0
            yield 0

        elif mode.get() == AVOID:

            # First Forward
            if R_pos.get() - R_last < 800 and L_pos.get() - L_last < 800:
                # Go forward for length of frame
                # Use heading as feedback for direction of movement 
                avoid_error = 2*(180 - head)

                # If control signal is positive, Romi must turn right
                if avoid_error > 0:
                    L_Motor.set_effort(base_speed + abs(avoid_error))
                    R_Motor.set_effort(base_speed)

                # If control signal is positive, Romi must turn left
                else:
                    R_Motor.set_effort(base_speed + abs(avoid_error))
                    L_Motor.set_effort(base_speed)
            # Turn
            else:
                L_Motor.set_effort(0)
                R_Motor.set_effort(0)
                direction = 270
                mode.put(ALIGN)
            yield 0

        elif mode.get() == BUMP:
            # Get start time on first run of mode
            if j == 0:    
                start_time = time.ticks_ms()
                j = 1

            # First Rotate: Turn for 0.5s (90deg) 
            if (time.ticks_diff(time.ticks_ms(), start_time) / 100) < 5: 
                L_Motor.set_effort(20)
                R_Motor.set_effort(-20)

            # First Forward: Go forward for 1.5s to hit cup
            elif (time.ticks_diff(time.ticks_ms(), start_time) / 100) < 20:
                L_Motor.set_effort(20)
                R_Motor.set_effort(20)

            # Second Rotate: Turn for 0.5s (90deg)   
            elif (time.ticks_diff(time.ticks_ms(), start_time) / 100) < 25:
                L_Motor.set_effort(-20)
                R_Motor.set_effort(20)
            # Second Forward 
            elif (time.ticks_diff(time.ticks_ms(), start_time) / 100) < 30:
                L_Motor.set_effort(20)
                R_Motor.set_effort(20)
            
            # Third Rotate: Turn for 0.5s (90deg) 
            elif (time.ticks_diff(time.ticks_ms(), start_time) / 100) < 35:
                L_Motor.set_effort(-20)
                R_Motor.set_effort(20)

            # Fourth Forward: Go to finish line
            elif (time.ticks_diff(time.ticks_ms(), start_time) / 100) < 55:
                L_Motor.set_effort(20)
                R_Motor.set_effort(20)
            else:
                L_Motor.set_effort(0)
                R_Motor.set_effort(0)
                # Put FSM into null state
                mode.put(4)
            yield 0

        elif mode.get() == ALIGN:
            # Use heading feedback to align to direction
            head = heading.get()
            if abs(direction - head) > 2:
                L_Motor.set_effort(5*(direction - head))
                R_Motor.set_effort(5*(head - direction))
            else:
                L_Motor.set_effort(0)
                R_Motor.set_effort(0)
                mode.put(LINE)
            yield 0
        else:
            motor_stop()
        

def motor_stop():
    # Motor Setup
    timer8 = Timer(8, freq = 20000)
    tim8ch1 = timer8.channel(1, Timer.PWM, pulse_width_percent = 10)
    tim8ch2 = timer8.channel(2, Timer.PWM, pulse_width_percent = 10)
    R_Motor = Motor(Pin.cpu.C7, Pin.cpu.C8,  Pin.cpu.C9, tim8ch1)
    L_Motor = Motor(Pin.cpu.C6, Pin.cpu.A10, Pin.cpu.B3, tim8ch2)
    
    # Stop both motors
    L_Motor.set_effort(0)
    R_Motor.set_effort(0)
    L_Motor.disable()
    R_Motor.disable()
