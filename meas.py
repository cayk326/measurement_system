import adafruit_bno055
import busio# I2C用のインターフェースを使用するためのモジュール
import board
import json
import threading
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Measurement:
    def __init__(self):
        # どのくらいの周波数でセンサ値を更新するか[Hz]
        self.BNO_UPDATE_FREQUENCY_HZ = 100
        self.CALIBRATION_FILE = "calibration.json"
        self.Time = []# 時間
        self.euler_x, self.euler_y, self.euler_z  = [], [], []# 角度[deg]
        self.gyro_x, self.gyro_y, self.gyro_z  = [], [], []# 各速度[rad/s]
        self.gravity_x, self.gravity_y, self.gravity_z  = [], [], []# 重力加速度[m/s^2]
        self.linear_accel_x, self.linear_accel_y, self.linear_accel_z  = [], [], []# 重力分を差し引いた加速度[m/s^2]
        self.quaternion_1, self.quaternion_2, self.quaternion_3, self.quaternion_4  = [], [], [], []# クオータニオン
        #キャリブレーション状態(システム/ジャイロ/加速度/地磁気)
        # 0: Not Calibrated, 3: Calibrated
        self.calibstat_sys, self.calibstat_gyro, self.calibstat_accel, self.calibstat_mag = [],[],[],[]
        self.columns = ["Time","euler_x", "euler_y", "euler_z", "gyro_x", "gyro_y", "gyro_z", "gravity_x", "gravity_y", "gravity_z",
                        "linear_accel_x, linear_accel_y", "linear_accel_z", "quaternion_1", "quaternion_2", "quaternion_3",
                        "quaternion_4", "calibstat_sys", "calibstat_gyro", "calibstat_accel", "calibstat_mag"]
        self.measured_data = None
        
        
    def connect(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)# I2CBusにアクセスするためのインターフェースを用意。SCLとSDAを使ってアクセス
        self.bno = adafruit_bno055.BNO055_I2C(self.i2c)# BNO055センサに接続する。DefaultではNDOF_MODE(12)
        #self.bno.use_external_crystal = True

        print("Established connection with BNO055")
        return




    def assy_measured_data(self):
        print('Assemble measured data')
        self.measured_data = pd.DataFrame()
        
        
        return






    # センサ値の更新
    def read_bno(self):
        """Function to read the BNO sensor and update the bno_data object with the
        latest BNO orientation, etc. state.  Must be run in its own thread because
        it will never return!
        """
        print('Start Monitoring')
        counter = 0
        try:
            while True:
                # Capture the lock on the bno_changed condition so the bno_data shared
                # state can be updated.
                # 一度各センサデータを一括で取る方がよさそう
                bno_data['Time'] = counter / self.BNO_UPDATE_FREQUENCY_HZ
                bno_data["euler"] = self.bno.euler# 角度[deg]
                bno_data['Gyro'] = self.bno.gyro# 角速度[rad/s]
                bno_data["gravity"] = self.bno.gravity# 重力加速度[m/s^2]
                bno_data["linear_accel"] = self.bno.linear_acceleration# 重力分を差し引いた加速度[m/s^2]
                bno_data["acceleration"] = self.bno.acceleration# 重力+リニア加速度
                bno_data["quaternion"] = self.bno.quaternion# クオーテーション
                bno_data["calibration"] = self.bno.calibration_status# キャリブレーション状態
                
                self.Time.append(counter / self.BNO_UPDATE_FREQUENCY_HZ)# Time    
                self.euler_x.append(bno_data["euler"][0]), self.euler_y.append(bno_data["euler"][1]), self.euler_z.append(bno_data["euler"][2])
                self.gyro_x.append(bno_data["Gyro"][0]), self.gyro_y.append(bno_data["Gyro"][1]), self.gyro_z.append(bno_data["Gyro"][2])
                self.gravity_x.append(bno_data["gravity"][0]), self.gravity_y.append(bno_data["gravity"][1]), self.gravity_z.append((bno_data["gravity"][2]))
                self.linear_accel_x.append(bno_data["linear_accel"][0]), self.linear_accel_y.append(bno_data["linear_accel"][1]), self.linear_accel_z.append(bno_data["linear_accel"][2])
                self.quaternion_1.append(bno_data["quaternion"][0]), self.quaternion_2.append(bno_data["quaternion"][1])
                self.quaternion_3.append([bno_data["quaternion"][2]]), self.quaternion_4.append(bno_data["quaternion"][3])
                self.calibstat_sys.append(bno_data["calibration"][0]), self.calibstat_gyro.append(bno_data["calibration"][1])
                self.calibstat_accel.append(bno_data["calibration"][2]), self.calibstat_mag.append(bno_data["calibration"][3])
                # Notify any waiting threads that the BNO state has been updated.
                # Sleep until the next reading.
                time.sleep(1.0 / self.BNO_UPDATE_FREQUENCY_HZ)
                counter += 1

        except KeyboardInterrupt:
            print('executed ctrl-c')
            
            self.assy_measured_data()
            
            return



        


    def start_monitor(self):
        self.read_bno()


    def save_calibration(self):
        # Save calibration data to disk.
        #
        # TODO: implement this
        #
        return "OK"


    def load_calibration(self):
        # Load calibration from disk.
        #
        # TODO: implement this
        #
        return "OK"






if __name__ == '__main__':

    meas =  Measurement()
    meas.connect()
    bno_data = {}
    meas.start_monitor()
  

