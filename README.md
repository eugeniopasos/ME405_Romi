# ME405_Romi
## Demo Link
https://www.youtube.com/watch?v=Af5d2OA-lL0
## Task Description
For the final project, two tasks were used to accomplish the course. A sensor task and a motor task. The sensor task was in control of interfacing the encoder, line sensor, and IMU. The motor task was in control of the motors and determining the state based on data collected from the sensors. Each task ran with a period of 10ms. In order to ensure a faster response time from the sensors, the sensor task was given higher priority (2) than the motor task (1). Five shared variables were used: centroid, mode, R_pos, L_pose, and heading.
#### Task Diagram
![image](https://github.com/user-attachments/assets/254409aa-eb37-448f-8fd5-a06ac079c9aa)
## Shared Variables Table
![image](https://github.com/user-attachments/assets/7ba4bc43-2b9c-462e-a30d-fc0775dd18af)
## Code Descriptions
### Main Code Description
The main code is responsible for setting up the tasks, shares, and scheduler. For easy control, a button is implemented to start and stop Romi as needed. In addition, a voltage divider is used to keep track of the battery voltage to properly scale the gains. After the button has been pressed, the tasks are created and appended to the task list. Then a forever loop is entered to schedule the next task unless there is a keyboard interrupt or the button is pressed. If the button is pressed, the motor stop function is run, disabling the motor, and breaking out of the loop.
### Sensor Task Description
The sensor task first begins by initializing the encoder, line sensor, and IMU objects. First, the line sensors are measured via an ADC. This returns an analog value of the sensor voltage, corresponding to the brightness of the line (0 = White, 4095 = Black). Then, the centroid of this distribution is found by normalizing each ADC value (dividing by 4095), and multiplying the resulting value by its position in the array and summing each element of the sensor array. With a seven-sensor array, -3 corresponds to the left and +3 corresponds to the right. The resulting sum indicates where the line is most likely to be. This number is stored in the centroid shared variable. Then, the L_Encoder position, and R_Encoder position are collected from the encoders and stored as a shared variable. Finally, the heading is extracted from the IMU via I2C.
### Motor Task Description
This task begins similarly, first initializing the motor pins/signals, bump sensors, and battery level pin. The task then becomes an FSM with the four modes, LINE, AVOID, BUMP, and ALIGN. 
#### LINE
The FSM begins in LINE mode. Using the centroid computed from the line sensors, the error signal (centroid) is put through a PID controller and is then added to the opposite wheel to compensate for the error (Centroid is left, right wheel goes faster etc). During this time, three conditions are being posed: "if (head >= 82 and head <= 95) and (diamond_flag == 1)", "elif ((rpos >= 4150) and (lpos >= 4900)) and (head >= 176 and head <= 184)", and "for pin in bumps: if pin.value() == 0:". The first one waits until the heading of Romi is ~90 degrees from its initial pose. When this condition is met, the motors are powered equally to skip over the diamond obstacle. The diamond_flag is then set to zero so this condition is never satisfied again. The next condition is the heading and encoder values. These values correspond to the point on the track where the frame obstacle occurs. This conditional changes the state to AVOID. The last condition checks if the bump sensors have been pressed. If they have, the state is changed to BUMP.
#### AVOID
This state is created for the specific task of using the encodes and IMU to navigate the frame portion of the course. The first task of this state is to move forward in for ~800 encoder counts. The heading is also used to ensure a straight path through the frame. This is done by computing the error from the heading to the desired direction (180 degrees from the start). This is done by adding the error to the effort of the corresponding motor. When the encoder counts exceed the set value, the state is changed to ALIGN.
#### ALIGN
The ALIGN state will align Romi to a specific direction with respect to the initial direction. The heading is read from the IMU and is compared to the desired direction. If this error is not within a certain tolerance (2 degrees), the robot turns in the desired direction until this tolerance is met. This is done by setting the effort of one motor to be positive and the other to be negative with an amplitude determined by the error signal. When the tolerance is met, the state is changed to LINE.
#### BUMP
The final state is triggered if a bump sensor is pressed. When the motor is pressed, a series of motions are performed. This is done by defining the time requirements for specific movements to be completed. First a rotation of 90 degrees (turn towards the cup), then a movement to push the cup, a second rotation of 90 degrees, a small movement to align Romi with the end destination, then a final rotation of 90 degrees, and a forward motion to end the course.
#### Motor Task FSM
![image](https://github.com/user-attachments/assets/4893dd7f-52cb-4422-808b-9b6b2304b2e8)
## Wiring Diagram
![image](https://github.com/user-attachments/assets/09459eef-f5c5-4136-8a6a-c664eb1e672c)
## Parts List
![image](https://github.com/user-attachments/assets/b60b1ccc-fc10-49ac-b510-24000380d65e)
## Romi Images
![image1](https://github.com/user-attachments/assets/4c83a1d7-53ff-4788-8b39-0844754e152d)
![image0](https://github.com/user-attachments/assets/4b948b96-745c-4155-9ff5-fa4173e7f579)
