from model import Adafruit_BNO055
import smbus
import time
import struct
import os
from collections import deque
import numpy as np
import board


path = os.getcwd()


from time import perf_counter
def wait_process(wait_sec):
    until = perf_counter() + wait_sec
    while perf_counter() < until:
        pass
    return

class measurement_BNO055:
    def __init__(self, BNO_UPDATE_FREQUENCY_HZ=10, seq_len=1000):
        
        self.COLUMNS = ["Time", "gyro_x", "gyro_y", "gyro_z", 
                        "linear_accel_x", "linear_accel_y", "linear_accel_z",
                        "quaternion_1", "quaternion_2", "quaternion_3", "quaternion_4", 
                        "calibstat_sys", "calibstat_gyro", "calibstat_accel", "calibstat_mag",
                        "Roll", "Pitch", "Yaw"]
    
        self.BNO_UPDATE_FREQUENCY_HZ = BNO_UPDATE_FREQUENCY_HZ
        self.exepath = path + '/measurement_system'
        self.datapath = path + '/data'
    
        self.seq_len = seq_len
        self.INIT_LEN = self.seq_len // self.BNO_UPDATE_FREQUENCY_HZ

        self.Time_data = deque(np.zeros(self.INIT_LEN))# Time
        self.linear_accel_x_data = deque(np.zeros(self.INIT_LEN))# linear_accel_x
        self.linear_accel_y_data = deque(np.zeros(self.INIT_LEN))# linear_accel_y
        self.linear_accel_z_data = deque(np.zeros(self.INIT_LEN))# linear_accel_z
        self.gyro_x_data = deque(np.zeros(self.INIT_LEN))# gyro_x
        self.gyro_y_data = deque(np.zeros(self.INIT_LEN))# gyro_y
        self.gyro_z_data = deque(np.zeros(self.INIT_LEN))# gyro_z
        
        self.assy_data = None

        self.bno = Adafruit_BNO055.BNO055()
        
        
        
        res = self.bno.begin()
        if res is not True:
            print("Error initializing device")
            exit()

        time.sleep(1)
        self.bno.setExternalCrystalUse(True)

    """
    def get_data(self, bno):
        '''
        Get data from new value from BNO055
        
        '''    
        #euler_z, euler_y, euler_x= [val for val in bno.euler]# Euler angle[deg] (Yaw, Roll, Pitch) -> euler_x,euler_y,euler_z = (Roll, Pitch, Yaw)
        #euler_x = (-1.0) * euler_x
        #euler_y = (-1.0) * euler_y
        #euler_z = euler_z - 180.0# 180deg offset
        gyro_x, gyro_y, gyro_z = [val for val in bno.gyro]# Gyro[rad/s]
        #gravity_x, gravity_y, gravity_z = [val for val in bno.gravity]# Gravitaional aceleration[m/s^2]
        linear_accel_x, linear_accel_y, linear_accel_z = [val for val in bno.linear_acceleration]# Linear acceleration[m/s^2]
        #accel_x, accel_y, accel_z = [val for val in bno.acceleration]# Three axis of acceleration(Gravity + Linear motion)[m/s^2]
        quaternion_1, quaternion_2, quaternion_3, quaternion_4 = [val for val in bno.quaternion]# Quaternion
        calibstat_sys, calibstat_gyro, calibstat_accel, calibstat_mag = [val for val in bno.calibration_status]# Status of calibration
        roll, pitch, yaw = self.calcEulerfromQuaternion(quaternion_1, quaternion_2, quaternion_3, quaternion_4)# Cal Euler angle from quaternion
        return  gyro_x, gyro_y, gyro_z,\
                linear_accel_x, linear_accel_y, linear_accel_z,\
                quaternion_1, quaternion_2, quaternion_3, quaternion_4,\
                calibstat_sys, calibstat_gyro, calibstat_accel, calibstat_mag,\
                roll, pitch, yaw
    """
    def get_data_from_BNO055(self):
        euler_z, euler_y, euler_x = [val for val in self.bno.getVector(self.bno.VECTOR_EULER)]
        gyro_x, gyro_y, gyro_z = [val for val in self.bno.getVector(self.bno.VECTOR_GYROSCOPE)]# Gyro[rad/s]
        linear_accel_x, linear_accel_y, linear_accel_z = [val for val in self.bno.getVector(self.bno.VECTOR_LINEARACCEL)]# Linear acceleration[m/s^2]
        print(euler_z, euler_y, euler_x, gyro_x, gyro_y, gyro_z, linear_accel_x, linear_accel_y, linear_accel_z)



    def start(self):
        print()
        while True:
            wait_process(0.1)
            self.get_data_from_BNO055()
        print()



    def Run(self):
        print()






def simple_main():
    print("Hello")
    bno = Adafruit_BNO055.BNO055()
    if bno.begin() is not True:
        print("Error initializing device")
        exit()
    time.sleep(1)
    bno.setExternalCrystalUse(True)
    while True:
        print(bno.getVector(Adafruit_BNO055.BNO055.VECTOR_EULER))
        time.sleep(0.01)





def main():
    print("Main start")
    meas_bno055 = measurement_BNO055(BNO_UPDATE_FREQUENCY_HZ=10, seq_len=100)
    if True:
        meas_bno055.start()


    bno = Adafruit_BNO055.BNO055()
    if bno.begin() is not True:
        print("Error initializing device")
        exit()
    time.sleep(1)
    bno.setExternalCrystalUse(True)
    meas_ctrl = measurement_BNO055(BNO_UPDATE_FREQUENCY_HZ=100, seq_len=1000)
    print("measurement instance was called")
    #meas_ctrl.get_data(bno)
    Ts = 0.1# Sampling time[s]
    fs = 1 / Ts# Sampling frequency[Hz]
    logic_start_time = time.time()#Logic start time
    counter = 0# Clock
    while True:
        euler_z, euler_y, euler_x = [val for val in bno.getVector(bno.VECTOR_EULER)]# # Euler angle[deg] (Yaw, Roll, Pitch) -> euler_x,euler_y,euler_z = (Roll, Pitch, Yaw)
        linear_accel_x, linear_accel_y, linear_accel_z = [val for val in bno.getVector(bno.VECTOR_LINEARACCEL)]# Linear acceleration[m/s^2]
        print(linear_accel_x, linear_accel_y, linear_accel_z, euler_y, euler_x, euler_z)
        time.sleep(0.01)
        
        
  

if __name__ == '__main__':
    import time
    #simple_main()
    main()
    print()