# ME405_Romi
## Demo Link
https://www.youtube.com/watch?v=Af5d2OA-lL0
## Task Description
For the final project, two tasks were used to accomplish the course. A sensor task and a motor task. The sensor task was in control of interfacing the encoder, line sensor, and IMU. The motor task was in control of the motors and determining the state based on data collected from the sensors. Each task ran with a period of 10ms. In order to ensure a faster response time from the sensors, the sensor task was given higher priority (2) than the motor task (1). Five shared variables were used: centroid, mode, R_pos, L_pose, and heading.
### Task Diagram
![image](https://github.com/user-attachments/assets/254409aa-eb37-448f-8fd5-a06ac079c9aa)
## Shared Variables Table
![image](https://github.com/user-attachments/assets/7ba4bc43-2b9c-462e-a30d-fc0775dd18af)
## Code Descriptions
### Sensor Task Description
The sensor task first begins by initializing the encoder, line sensor, and IMU objects. First, the line sensors are measured via an ADC. This returns an analog value of the sensor voltage, corresponding to the brightness of the line (0 = White, 4095 = Black). Then the centroid of this distribution is found by normalizing each ADC values (dividing by 4095), and multiplying the resulting value by its position in the array and summing each element of the sensor array. With a seven sensor array, -3 corresponds to the left and +3 corresponds to the right. The resulting sum indicates where the line is most likely to be. This number is stored in the centroid shared variable. Then the L_Encoder position, R_Encoder position are collected from the encoders and stored as a shared variable. Finally, the heading is extracted from the IMU via I2C.
### Motor Task Description
This task begins in a similar way, first initializing the motor pins/signals, bump sensors, and battery level pin. The task then becomes an FSM 
### Motor Task FSM
![image](https://github.com/user-attachments/assets/4893dd7f-52cb-4422-808b-9b6b2304b2e8)
## Wiring Diagram
![image](https://github.com/user-attachments/assets/09459eef-f5c5-4136-8a6a-c664eb1e672c)
## Parts List
![image](https://github.com/user-attachments/assets/b60b1ccc-fc10-49ac-b510-24000380d65e)
## Romi Images
![image1](https://github.com/user-attachments/assets/4c83a1d7-53ff-4788-8b39-0844754e152d)
![image0](https://github.com/user-attachments/assets/4b948b96-745c-4155-9ff5-fa4173e7f579)
