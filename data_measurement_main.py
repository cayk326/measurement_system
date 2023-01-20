import time
import os
from collections import deque
import numpy as np
import threading
import sys
import time
import adafruit_bno055
import board
import matplotlib.pyplot as plt


path = os.getcwd()

from time import perf_counter
def wait_process(wait_sec):
    until = perf_counter() + wait_sec
    while perf_counter() < until:
        pass
    return

class measurement_BNO055:
    def __init__(self, BNO_UPDATE_FREQUENCY_HZ=10, seq_len=1000):
        
        self.COLUMNS = ["Time",
                        "linear_accel_x", "linear_accel_y", "linear_accel_z", 
                        "gyro_x", "gyro_y", "gyro_z", 
                        "euler_x", "euler_y", "euler_z",
                        "quat_roll", "quat_pitch", "quat_yaw", 
                        "calibstat_sys", "calibstat_gyro", "calibstat_accel", "calibstat_mag"
                        ]
    
        self.BNO_UPDATE_FREQUENCY_HZ = BNO_UPDATE_FREQUENCY_HZ
        self.exepath = path + '/measurement_system'
        self.datapath = path + '/data'
    
        self.seq_len = seq_len
        self.INIT_LEN = self.seq_len // self.BNO_UPDATE_FREQUENCY_HZ

        self.Time_queue = deque(np.zeros(self.INIT_LEN))# Time
        self.linear_accel_x_queue = deque(np.zeros(self.INIT_LEN))# linear_accel_x
        self.linear_accel_y_queue = deque(np.zeros(self.INIT_LEN))# linear_accel_y
        self.linear_accel_z_queue = deque(np.zeros(self.INIT_LEN))# linear_accel_z
        self.gyro_x_queue = deque(np.zeros(self.INIT_LEN))# gyro_x
        self.gyro_y_queue = deque(np.zeros(self.INIT_LEN))# gyro_y
        self.gyro_z_queue = deque(np.zeros(self.INIT_LEN))# gyro_z
        self.euler_x_queue = deque(np.zeros(self.INIT_LEN))# euler_x Roll
        self.euler_y_queue = deque(np.zeros(self.INIT_LEN))# euler_y Roll
        self.euler_z_queue = deque(np.zeros(self.INIT_LEN))# euler_z yaw
        self.quat_roll_queue = deque(np.zeros(self.INIT_LEN))# quat_roll
        self.quat_pitch_queue = deque(np.zeros(self.INIT_LEN))# quat_pitch
        self.quat_yaw_queue = deque(np.zeros(self.INIT_LEN))# quat_yaw
        self.quat1_queue = deque(np.zeros(self.INIT_LEN))# quat1 w
        self.quat2_queue = deque(np.zeros(self.INIT_LEN))# quat2 x
        self.quat3_queue = deque(np.zeros(self.INIT_LEN))# quat3 y
        self.quat4_queue = deque(np.zeros(self.INIT_LEN))# quat4 z  
        self.calibstat_sys_queue = deque(np.zeros(self.INIT_LEN))# calibstat_sys
        self.calibstat_gyro_queue = deque(np.zeros(self.INIT_LEN))# calibstat_gyro
        self.calibstat_accel_queue = deque(np.zeros(self.INIT_LEN))# calibstat_accel
        self.calibstat_mag_queue = deque(np.zeros(self.INIT_LEN))# calibstat_mag


        self.assy_data = None

        i2c_instance = board.I2C()
        self.bno055_sensor = adafruit_bno055.BNO055_I2C(i2c_instance)


    def calibration(self):
        print("Start calibration!")
        while self.bno055_sensor.calibrated is not True:
            print('SYS: {0}, Gyro: {1}, Accel: {2}, Mag: {3}'.format(*(self.bno055_sensor.calibration_status)))



    def calcEulerfromQuaternion(self, _w, _x, _y, _z):
        sqw = _w ** 2
        sqx = _x ** 2
        sqy = _y ** 2
        sqz = _z ** 2
        COEF_EULER2DEG = 57.2957795131
        yaw = COEF_EULER2DEG * (np.arctan2(2.0 * (_x * _y + _z * _w), (sqx - sqy - sqz + sqw)))# Yaw
        pitch = COEF_EULER2DEG * (np.arcsin(-2.0 * (_x * _z - _y * _w) / (sqx + sqy + sqz + sqw)))# Pitch
        roll = COEF_EULER2DEG * (np.arctan2(2.0 * (_y * _z + _x * _w), (-sqx - sqy + sqz + sqw)))# Roll
        return roll, pitch, yaw




  
    def get_data_from_BNO055(self):
        euler_z, euler_y, euler_x = [val for val in self.bno055_sensor.euler]# X: yaw, Y: pitch, Z: roll
        gyro_x, gyro_y, gyro_z = [val for val in self.bno055_sensor.gyro]# Gyro[rad/s]
        linear_accel_x, linear_accel_y, linear_accel_z = [val for val in self.bno055_sensor.linear_acceleration]# Linear acceleration[m/s^2]

        quaternion_1, quaternion_2, quaternion_3, quaternion_4 = [val for val in self.bno055_sensor.quaternion]# quaternion
        quat_roll, quat_pitch, quat_yaw = self.calcEulerfromQuaternion(quaternion_1, quaternion_2, quaternion_3, quaternion_4)# Cal Euler angle from quaternion
        calibstat_sys, calibstat_gyro, calibstat_accel, calibstat_mag = [val for val in self.bno055_sensor.calibration_status]# Status of calibration

        return linear_accel_x, linear_accel_y, linear_accel_z, \
                gyro_x, gyro_y, gyro_z, \
                euler_x, euler_y, euler_z, \
                (-1)*quat_roll, (-1)*quat_pitch, (-1)*quat_yaw, \
                quaternion_1, quaternion_2, quaternion_3, quaternion_4, \
                calibstat_sys, calibstat_gyro, calibstat_accel, calibstat_mag


    def update_data_stream(self):
        def update_queue(stream_queue, val):
            stream_queue.popleft()
            stream_queue.append(val)
            return stream_queue
        
        linear_accel_x, linear_accel_y, linear_accel_z, \
        gyro_x, gyro_y, gyro_z, \
        euler_x, euler_y, euler_z, \
        quat_roll, quat_pitch, quat_yaw, \
        quat1, quat2, quat3, quat4, \
        calibstat_sys, calibstat_gyro, calibstat_accel, calibstat_mag = self.get_data_from_BNO055()

        update_queue(self.Time_queue, self.current_time)
        update_queue(self.linear_accel_x_queue, linear_accel_x)
        update_queue(self.linear_accel_y_queue, linear_accel_y)
        update_queue(self.linear_accel_z_queue, linear_accel_z)
        update_queue(self.gyro_x_queue, gyro_x)
        update_queue(self.gyro_y_queue, gyro_y)
        update_queue(self.gyro_z_queue, gyro_z)
        update_queue(self.euler_x_queue, euler_x)
        update_queue(self.euler_y_queue, euler_y)
        update_queue(self.euler_z_queue, euler_z)
        update_queue(self.quat_roll_queue, quat_roll)
        update_queue(self.quat_pitch_queue, quat_pitch)
        update_queue(self.quat_yaw_queue, quat_yaw)
        update_queue(self.quat1_queue, quat1)
        update_queue(self.quat2_queue, quat2)
        update_queue(self.quat3_queue, quat3)
        update_queue(self.quat4_queue, quat4)
        update_queue(self.calibstat_sys_queue, calibstat_sys)
        update_queue(self.calibstat_gyro_queue, calibstat_gyro)
        update_queue(self.calibstat_accel_queue, calibstat_accel)
        update_queue(self.calibstat_mag_queue, calibstat_mag)
        return


    def meas_start(self):
        print()
        self.meas_start_time = time.time()#Logic start time
        counter = 0# Clock
        ## Measurement Main Loop ##
        print("Initialize the sensor...")
        wait_process(2)# sensor initialization
        try: 
            while True:


                self.itr_start_time = time.time()# Start time of iteration loop
                self.current_time = counter / self.BNO_UPDATE_FREQUENCY_HZ# Current time                    
                ## Process / update data stream, concat data
                """
                1. get data fron a sensor BNO055
                2. deque data from que
                3. enque data to que
                4. create data set at current sample
                5. concatinate data 

                """
                self.update_data_stream()


                """
                
                if counter == 0:
                        
                    self.assy_data = data.copy()

                else: 
                    self.assy_data = np.concatenate((self.assy_data, data), axis = 0)# Concatenate data
                """




                self.itr_end_time = time.time()# End time of iteration loop
                wait_process((1.0 / self.BNO_UPDATE_FREQUENCY_HZ) - (self.itr_end_time - self.itr_start_time))# For keeping sampling frequency
                counter += 1
                print('Time: {0} sec'.format(self.current_time))

            
        except Exception as e:
            print("Error")
            print(e)
        
        except KeyboardInterrupt:
            print("KeybordInterrupt!")
            plt.plot(self.Time_queue, self.euler_x_queue, 'r', '*')
            plt.show()
            self.meas_end_time = time.time()
            # Elapsed time
            self.elapsed_time = self.meas_end_time - self.meas_start_time         

        print("Finish")


    def Run(self):
        print()



def main():
    print("Main start")
    meas_bno055 = measurement_BNO055(BNO_UPDATE_FREQUENCY_HZ=10, seq_len=1000)
    
    Isneed_calib = False
    if Isneed_calib:
        meas_bno055.calibration()
        print("Calibration was finished!")
    
    if True:
        meas_bno055.meas_start()


        
        
  

if __name__ == '__main__':
    import time
    #simple_main()
    main()
    print()