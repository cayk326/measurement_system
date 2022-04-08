from pkgutil import get_data
from unittest import main
import adafruit_bno055
import busio# I2C用のインターフェースを使用するためのモジュール
import board
import json
import threading
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import OrderedDict
import os
path = os.getcwd()



class measurement:
    def __init__(self):
        print('Initialize')
        self.IsStartStop = False# False:Stop, True:Start
        self.IsMonitor = False# False:Not monitoring, True:Monitoring
        self.BNO_UPDATE_FREQUENCY_HZ = 10    
        self.columns = ["Time","euler_x", "euler_y", "euler_z", "gyro_x", "gyro_y", "gyro_z", "gravity_x", "gravity_y", "gravity_z",
                        "linear_accel_x", "linear_accel_y", "linear_accel_z","accel_x", "accel_y", "accel_z",
                        "quaternion_1", "quaternion_2", "quaternion_3", "quaternion_4", 
                        "calibstat_sys", "calibstat_gyro", "calibstat_accel", "calibstat_mag"]
        self.exepath = path + '/measurement_system'
        self.datapath = path + '/measurement_system/data'
        
    def connect(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)# I2CBusにアクセスするためのインターフェースを用意。SCLとSDAを使ってアクセス
        self.bno = adafruit_bno055.BNO055_I2C(self.i2c)# BNO055センサに接続する。DefaultではNDOF_MODE(12)
        #self.bno.use_external_crystal = True
        print("Established connection with BNO055")
        return
        
    def get_data(self):
        
        '''
        センサからある時点の値を抽出
        '''
        
        euler_x, euler_y, euler_z = [val for val in self.bno.euler]# 角度[deg]
        gyro_x, gyro_y, gyro_z = [val for val in self.bno.gyro]# 角速度[rad/s]
        gravity_x, gravity_y, gravity_z = [val for val in self.bno.gravity]# 重力加速度[m/s^2]
        linear_accel_x, linear_accel_y, linear_accel_z = [val for val in self.bno.linear_acceleration]# 重力分を差し引いた加速度[m/s^2]
        accel_x, accel_y, accel_z = [val for val in self.bno.acceleration]# 重力+リニア加速度
        quaternion_1, quaternion_2, quaternion_3, quaternion_4 = [val for val in self.bno.quaternion]# クオータニオン
        calibstat_sys, calibstat_gyro, calibstat_accel, calibstat_mag = [val for val in self.bno.calibration_status]# キャリブレーション状態
        
        return euler_x, euler_y, euler_z, gyro_x, gyro_y, gyro_z, gravity_x, gravity_y, gravity_z,\
               linear_accel_x, linear_accel_y, linear_accel_z, accel_x, accel_y, accel_z,\
               quaternion_1, quaternion_2, quaternion_3, quaternion_4,\
               calibstat_sys, calibstat_gyro, calibstat_accel, calibstat_mag

    def update_graph(self, assy_data):
        print()
        # 描画領域を取得
        fig, ax = plt.subplots(1, 1)
        ax.set_ylim((-10, 10))
        
        
    
    def monitor(self):
        print('Monitor')
        self.IsMonitor = True
        try:
            print('Start Monitoring')
            counter = 0
            while True:
                Time = counter / self.BNO_UPDATE_FREQUENCY_HZ
                '''
                Time, euler_x, euler_y, euler_z, gyro_x, gyro_y, gyro_z, gravity_x, gravity_y, gravity_z,\
                linear_accel_x, linear_accel_y, linear_accel_z, accel_x, accel_y, accel_z,\
                quaternion_1, quaternion_2, quaternion_3, quaternion_4,\
                calibstat_sys, calibstat_gyro, calibstat_accel, calibstat_mag]
                '''                 
                data = np.array([Time] + list(meas.get_data())).reshape(-1, len(self.columns))#センサからデータを抽出しTimeの結合

                if counter == 0:
                    assy_data = data.copy()
                else: 
                    assy_data = np.concatenate((assy_data, data), axis = 0)# 行方向に結合
                    
                print(assy_data[-1])
                #self.update_graph(assy_data)
                time.sleep(1.0 / self.BNO_UPDATE_FREQUENCY_HZ)
                counter += 1
            
        
        except KeyboardInterrupt:
            print('executed ctrl-c')
            assy_data = pd.DataFrame(assy_data, columns=list(self.columns))
            assy_data.to_csv(self.datapath + '/'+ str(time.time()) +'_data.csv')
    
        return
            
    def start(self):
        print('Start Logging')
        return



if __name__ == '__main__':
    print('Start Application')
    meas = measurement()
    meas.connect()
    mode = input()
    
    if mode == '1':# Monitor mode
        meas.monitor()
    elif mode == '2':# Start Logging
        meas.start()
    else:
        print()