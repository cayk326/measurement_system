import os
path = os.getcwd()
from collections import deque
import numpy as np
import adafruit_bno055
import busio
import board

class MeasBNO055:
    
    def __init__(self, BNO_UPDATE_FREQUENCY_HZ=10, INTERVAL=1000):
        '''
        
        self.COLUMNS = ["Time","euler_x", "euler_y", "euler_z", "gyro_x", "gyro_y", "gyro_z", "gravity_x", "gravity_y", "gravity_z",
                        "linear_accel_x", "linear_accel_y", "linear_accel_z","accel_x", "accel_y", "accel_z",
                        "quaternion_1", "quaternion_2", "quaternion_3", "quaternion_4", 
                        "calibstat_sys", "calibstat_gyro", "calibstat_accel", "calibstat_mag",
                        "Roll", "Pitch", "Yaw"]
        '''
    
        self.COLUMNS = ["Time", "gyro_x", "gyro_y", "gyro_z", 
                        "linear_accel_x", "linear_accel_y", "linear_accel_z",
                        "quaternion_1", "quaternion_2", "quaternion_3", "quaternion_4", 
                        "calibstat_sys", "calibstat_gyro", "calibstat_accel", "calibstat_mag",
                        "Roll", "Pitch", "Yaw"]
        
    
        self.BNO_UPDATE_FREQUENCY_HZ = BNO_UPDATE_FREQUENCY_HZ
        self.exepath = path + '/measurement_system'
        self.datapath = path + '/data'
    
    
        self.INTERVAL = INTERVAL
        self.INIT_LEN = self.INTERVAL // self.BNO_UPDATE_FREQUENCY_HZ

        self.Time_data = deque(np.zeros(self.INIT_LEN))# Time
        self.linear_accel_x_data = deque(np.zeros(self.INIT_LEN))# linear_accel_x
        self.linear_accel_y_data = deque(np.zeros(self.INIT_LEN))# linear_accel_y
        self.linear_accel_z_data = deque(np.zeros(self.INIT_LEN))# linear_accel_z
        self.gyro_x_data = deque(np.zeros(self.INIT_LEN))# gyro_x
        self.gyro_y_data = deque(np.zeros(self.INIT_LEN))# gyro_y
        self.gyro_z_data = deque(np.zeros(self.INIT_LEN))# gyro_z
        
        self.assy_data = None
        
        self.i2c, self.bno = self.connect()

            
    def connect(self):
        i2c = busio.I2C(board.SCL, board.SDA)# Access i2c using SCL and SDA
        bno = adafruit_bno055.BNO055_I2C(i2c)# Connect BNO055. Default: NDOF_MODE(12)
        #self.bno.use_external_crystal = True
        print("Established connection with BNO055")
        return i2c, bno
    
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