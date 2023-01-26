
# import libraries
import threading
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, clear_output
import ipywidgets as widgets
import datetime
from concurrent.futures import ThreadPoolExecutor
import sys

# import models
from models.tools import wait_process
from models import signalprocessing as sp
from models import measurement_BNO055

class measurement_controller:
    def __init__(self, BNO_UPDATE_FREQUENCY_HZ = 10, seq_len=1000, Isautosave = True):
        self.ctrlbutton_state = 'stop'# stop/start
        self.ctrl_button = widgets.Button(description="▶",layout=lay(120,50)) 
        self.save_button = widgets.Button(description="Save",layout=lay(120,50))
        self.calib_button = widgets.Button(description="Calib",layout=lay(120,50))
        
        
        self.output = widgets.Output(layour={'border': '1px solid black'})       
        self.measurement = measurement_BNO055(BNO_UPDATE_FREQUENCY_HZ=10, seq_len=1000)
        self.start_thread = None
        self.stop_thread = None
        self.save_thread = None
        self.calib_thread = None
        self.buttonState = "stop"
        self.Isautosave = Isautosave
        
    def start(self):
        
        self.stop_thread = None
        self.measurement.IsStart = True
        self.ctrl_button.description = '■'
        self.ctrl_button.button_style = 'success'
        print('Measurement will be Started...')
        self.measurement.meas_start()
       
        
        
        
        
    def stop(self):
        self.measurement.IsStop = True
        self.measurement.IsStart = False
        self.start_thread = None
        self.ctrl_button.description = '▶'
        self.ctrl_button.button_style = ''
        try:
            if self.Isautosave:
                self.save()
            self.ctrl_button.description = '▶'
            self.ctrl_button.button_style = ''
        except Exception as e:
            print('Error!')
        
        return

    def save(self):
        try:
            self.save_button.description = 'Saving...'
            self.save_button.button_style = 'success'
            self.measurement.save_data()
            
            wait_process(1)# For user friendly
            
            self.save_button.description = 'Save'
            self.save_button.button_style = ''
            self.save_thread = None
        except Exception:
            pass

    def get_calib_stat(self):
        self.measurement.calibration()


    def Run(self):
        #@self.output.capture()
        def on_click_ctrlbutton_callback(clicked_button: widgets.Button) -> None:
            if self.ctrlbutton_state == 'stop':
                if self.start_thread == None :
                    self.ctrlbutton_state = 'start'
                    self.start_thread = threading.Thread(target=self.start)
                    self.start_thread.start()
                
            elif self.ctrlbutton_state == 'start':
                if self.stop_thread == None :
                    self.ctrlbutton_state = 'stop'
                    self.stop_thread = threading.Thread(target=self.stop)
                    self.stop_thread.start()
                    
        def on_click_savebutton_callback(clicked_button: widgets.Button) -> None:
            if self.ctrlbutton_state == 'stop' and self.measurement.IsStart == False:
                self.save_thread = threading.Thread(target=self.save)
                self.save_thread.start()
        
        @self.output.capture()
        def on_click_calibbutton_callback(clicked_button: widgets.Button) -> None:
            if self.ctrlbutton_state == 'stop' and self.measurement.IsStart  == False:
                self.get_calib_stat()
        
            

        self.calib_button.on_click(on_click_calibbutton_callback)
        self.ctrl_button.on_click(on_click_ctrlbutton_callback)
        self.save_button.on_click(on_click_savebutton_callback)


    def show_historicalgraph(self, mode="gyro"):

        fig, ax = plt.subplots(1, 3, figsize=(8,3), tight_layout=True)
        if mode == "gyro":
            ax[0].plot(self.measurement.df['Time'], self.measurement.df['gyro_x'], marker='*')
            ax[1].plot(self.measurement.df['Time'], self.measurement.df['gyro_y'], marker='*')
            ax[2].plot(self.measurement.df['Time'], self.measurement.df['gyro_z'], marker='*')
            ax[0].set_xlabel('Time[s]')
            ax[0].set_ylabel('Gyro_x(Roll Rate)[rad/s]')
            ax[1].set_xlabel('Time[s]')
            ax[1].set_ylabel('Gyro_y(Pitch Rate)[rad/s]')
            ax[2].set_xlabel('Time[s]')
            ax[2].set_ylabel('Gyro_z(Yaw Rate)[rad/s]')

        if mode == "euler":
            ax[0].plot(self.measurement.df['Time'], self.measurement.df['euler_x'], marker='*')
            ax[1].plot(self.measurement.df['Time'], self.measurement.df['euler_y'], marker='*')
            ax[2].plot(self.measurement.df['Time'], self.measurement.df['euler_z'], marker='*')
            ax[0].set_xlabel('Time[s]')
            ax[0].set_ylabel('Roll Angle[deg]')
            ax[1].set_xlabel('Time[s]')
            ax[1].set_ylabel('Pitch Angle[deg]')
            ax[2].set_xlabel('Time[s]')
            ax[2].set_ylabel('Yaw Angle[deg]') 

        if mode == "linear_accel":
            ax[0].plot(self.measurement.df['Time'], self.measurement.df['linear_accel_x'], marker='*')
            ax[1].plot(self.measurement.df['Time'], self.measurement.df['linear_accel_y'], marker='*')
            ax[2].plot(self.measurement.df['Time'], self.measurement.df['linear_accel_z'], marker='*')
            ax[0].set_xlabel('Time[s]')
            ax[0].set_ylabel('linear_accel_x[m/s^2]')
            ax[1].set_xlabel('Time[s]')
            ax[1].set_ylabel('linear_accel_y[m/s^2]')
            ax[2].set_xlabel('Time[s]')
            ax[2].set_ylabel('linear_accel_z[m/s^2]')

        if mode == "quat_angle":
            ax[0].plot(self.measurement.df['Time'], self.measurement.df['quat_roll'], marker='*')
            ax[1].plot(self.measurement.df['Time'], self.measurement.df['quat_pitch'], marker='*')
            ax[2].plot(self.measurement.df['Time'], self.measurement.df['quat_yaw'], marker='*')
            ax[0].set_xlabel('Time[s]')
            ax[0].set_ylabel('quat_roll[deg]')
            ax[1].set_xlabel('Time[s]')
            ax[1].set_ylabel('quat_pitch[deg]')
            ax[2].set_xlabel('Time[s]')
            ax[2].set_ylabel('quat_yaw[deg]')
                        
        #plt.show()
        #fig = plt.gcf()
        return
        
def lay(width,height):
    return widgets.Layout(width=str(width)+"px",height=str(height)+"px")
def init_meas_system():
    meas_ctrl = measurement_controller(BNO_UPDATE_FREQUENCY_HZ=10, seq_len=1000, Isautosave=False)
    display(widgets.VBox([
            widgets.HBox([meas_ctrl.ctrl_button, meas_ctrl.save_button, meas_ctrl.calib_button, ]), 
            meas_ctrl.output]))


    return meas_ctrl
def main_loop():
    meas_ctrl = init_meas_system()
    meas_ctrl.Run()
    return meas_ctrl
