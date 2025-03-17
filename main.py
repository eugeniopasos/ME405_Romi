
from pyb import Pin, ADC
import cotask
import task_share

import task_sensor
import task_motor
import gc

import time


def main():
    
    while True:
        # Set up button input and source voltage measurement.
        button = Pin(Pin.cpu.C13, mode=Pin.IN, pull=Pin.PULL_UP)
        Vin_pin = Pin(Pin.cpu.C4,  mode = Pin.ANALOG)
        Vin = ADC(Vin_pin)
        V = (Vin.read() / 4095.0)
        print("\nBattery Percentage: " + str(int(V * 100)) + "%\n")

        # Wait to start
        print("Press to Start")
        while button.value():
            button_pressed = False
        print("Started!")
        while not(button.value()):
            pass   

        # Create Shares and add Tasks to Task List

        # Centroid contains the value of the centroid from the line sensor
        centroid = task_share.Share('f', thread_protect = False, name = "Centroid Value")
        centroid.put(0)

        # The mode variable controls the FSM of the robot
        mode = task_share.Share('H', thread_protect = False, name = "Mode")
        mode.put(0)

        # The L and R encoder position 
        R_pos = task_share.Share('I', thread_protect = False, name = "R_pos")
        R_pos.put(0)

        L_pos = task_share.Share('I', thread_protect = False, name = "L_pos")
        L_pos.put(0)
        
        # The heading of the robot from the IMU
        heading = task_share.Share('f', thread_protect = False, name = "Heading")
        heading.put(0)
        
        shared_data = [centroid, mode, R_pos, L_pos, heading]
        
        # There are two tasks, one to interface with the sensors, the other to control the motor.
        sensors_obj = cotask.Task(task_sensor.read_sensor, name = "Read Sensors Task", priority = 2, 
                                period = 10, profile = True, trace = False, shares = shared_data)
        
        motor_control_obj = cotask.Task(task_motor.drive_motor, name = "Drive Task", priority = 1, 
                                period = 10, profile = True, trace = False, shares = shared_data)
        
        cotask.task_list.append(sensors_obj)
        cotask.task_list.append(motor_control_obj)

        gc.collect()

        while True:
            try:
                # If the button is pressed, stop the motor and break from the loop
                if not(button.value()) or button_pressed == True:
                    button_pressed = True
                    task_motor.motor_stop()                    
                    break
                else:
                    cotask.task_list.pri_sched()
            
            
            except KeyboardInterrupt:
                task_motor.motor_stop()
                break

if __name__ == "__main__":
    main()