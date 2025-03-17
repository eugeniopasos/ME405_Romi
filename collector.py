# import matplotlib.pyplot as plt
# class Plotter:
#     def __init__(self, data_list):
#         self.data_list = data_list
    
#     def show_graph_right(self):
#         plt.subplot(2, 1, 1)
#         for data in self.data_list:
#             plt.plot(data.time_array, data.right_encoder_position)
#         plt.title('Right Encoder Position vs. Time')
#         plt.xlabel('Time (s)')
#         plt.ylabel('Velocity (/s)')
        
#         plt.subplot(2, 1, 2)
#         for data in self.data_list:
#             plt.plot(self.time_array, data.right_encoder_velocity)
#         plt.title('Right Encoder Velocity vs. Time')
#         plt.xlabel('Time (s)')
#         plt.ylabel('Position()')

class Data:
    def __init__(self):
        self.time_array = [0] * 60
        self.left_encoder_position_array =  [0] * 60
        self.right_encoder_position_array = [0] * 60
        self.left_encoder_velocity_array =  [0] * 60
        self.right_encoder_velocity_array = [0] * 60
        self.index = 0

    def append_data_point(self, time, left_position, right_position, left_velocity, right_velocity):
        
        self.time_array[self.index]                   = time
        self.left_encoder_position_array[self.index]  = left_position
        self.right_encoder_position_array[self.index] = right_position
        self.left_encoder_velocity_array[self.index]  = left_velocity
        self.right_encoder_velocity_array[self.index] = right_velocity 
        if self.index >= 49:
            self.index = 0
        else:
            self.index += 1




        


