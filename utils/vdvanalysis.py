from pathlib import Path
from asammdf import MDF, Signal
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class VDVAnalysis:
    def __init__(self, currentGear, selectedGear, signals, mdf_extension, input_folder, shift_mode) -> None:
        self.currentGear = int(currentGear)
        self.selectedGear = int(selectedGear)
        self.MAXCURRENTGEAR = float(f'{currentGear}.9')
        self.MINCURRENTGEAR = float(f'{selectedGear}.06')
        self.signals = signals
        self.mdf_extension = mdf_extension
        self.input_folder = input_folder
        self.shift_mode = shift_mode
        self.timestampChangeToShiftInProcess = []
        self.timestampChangeToShiftNotInProcess = []
        self.windows = []
        self.data = []
        self.results = []

    def __initialization(self):
        # load MDF/DBC files from input folder
        path = Path(__file__).parent.parent
        path_in = Path(path, self.input_folder)
        
        logfiles = list(path_in.glob("*" + self.mdf_extension))
        # mdf = MDF.concatenate(logfiles)
        # mdf_scaled = mdf.filter(self.signals)
        mdf= MDF(logfiles[0])
        mdf_scaled = mdf.to_dataframe(time_as_date=True)
        frame = mdf_scaled[self.signals]
        if self.shift_mode == "UPSHIFT":

            data = frame.loc[(frame['TransSelectedGear'] == self.selectedGear) & (frame['TransCurrentGear'] <= self.selectedGear)]
            data["StateChange"] = (data["TransShiftInProcess"] != data["TransShiftInProcess"].shift()).astype(int)
        
        else:
            #data = frame
            data = frame.loc[(frame['TransSelectedGear'] == self.selectedGear) & (frame['TransCurrentGear'] <= self.currentGear)]
            data["StateChange"] = (data["TransShiftInProcess"] != data["TransShiftInProcess"].shift()).astype(int)
            data["TransSelectedGear"]= pd.to_numeric(data['TransSelectedGear']).astype(int)
            data["TransCurrentGear"]= pd.to_numeric(data['TransCurrentGear']).astype(int)
            
        
        return data
    
    def __processing(self, data):
        # data.to_csv('teste.csv')
        windows =self.set_window(data)  
        print(f'Process VDV finished')            
        return windows

    def analyzer(self):
        data = self.__initialization()
        windows = self.__processing(data)
        
        for i in range(len(windows)):
            window = pd.DataFrame(windows[i])
            window = self.__verificationFirstRow(window)
            isWindowCorrect = self.__existsSignalInWindow(signal_1="TransCurrentGear", signal_2="TransSelectedGear", window=window)
            isShiftMode = self. __isShiftMode(window=window)
            window.loc[:,'Delta_Time'] = window.index.to_series().diff()
            window.loc[:,'Delta_Time'] = window.loc[:,'Delta_Time'].dt.total_seconds()  
            dt = self.__dtCalculation(signal_delta_time="Delta_Time", window=window)
            shiftDuration = self.__shiftDurationCalculation(signal_delta_time="Delta_Time", window=window)
           
            if len(window) > 70 and isWindowCorrect and not isShiftMode and (shiftDuration < 5):

                vdvIS = self.__calculationVDV(signal="TransInputShaftSpeed",signal_delta_time="Delta_Time", window=window, dt=dt, diameter=0.762)
                vdvOS = self.__calculationVDV(signal="TransOutputShaftSpeed",signal_delta_time="Delta_Time", window=window, dt=dt, diameter=0.762)
                window = window.fillna(0)
                
                result = {
                    'name_IS' : "TRANS INPUT SHAFT SPEED",
                    'shift_duration' : shiftDuration, 
                    'VDV_IS': vdvIS,
                    'name_OS' : "TRANS OUTPUT SHAFT SPEED",
                    'VDV_OS': vdvOS,
                    'select_gear' : self.selectedGear,
                    'current_gear' : self.currentGear,
                    'window' : window,
                }
                
                window.to_csv(f'VDV_{self.shift_mode}_{self.selectedGear}_GEAR_{i}_.csv') 
                self.results.append(result)
                print(f"The Acquisition {i} was approved ...")
                

            else:
                print(f"The Acquisition {i} was rejected ...")

        print(f'Analyzer VDV finished')
        return self.results

    def get_maxCurrentGear(self):
        return float(self.MAXCURRENTGEAR)
    
    def get_signals(self):
        return self.signals
    
    def get_extension(self):
        return self.mdf_extension
    
    def get_input_folder(self):
        return self.input_folder
    
    def get_output_folder(self):
        return self.output_folder
    
    def set_window(self, data):
        for i in range(0, len(data)):
            stateChange = data.iloc[i]['StateChange']
            ## Define a janela de Start
            if self.shift_mode == "UPSHIFT":
            
                if stateChange == 1 and (data.iloc[i]["TransShiftInProcess"] == b'ShiftInProcess' or data.iloc[i]["TransShiftInProcess"] == b'Shift in process') and data.iloc[i]["TransCurrentGear"] <= self.MAXCURRENTGEAR:
                    self.timestampChangeToShiftInProcess.append(i)
          
            else:
                if stateChange == 1 and (data.iloc[i]["TransShiftInProcess"] == b'ShiftInProcess' or data.iloc[i]["TransShiftInProcess"] == b'Shift in process') and data.iloc[i]["TransSelectedGear"] == self.selectedGear and data.iloc[i]["TransCurrentGear"] == self.currentGear:
                    self.timestampChangeToShiftInProcess.append(i)
                    
        for j in range(len(self.timestampChangeToShiftInProcess)):
            
            for k in range(self.timestampChangeToShiftInProcess[j], len(data)):
                if self.shift_mode == "UPSHIFT":
                    stateChange = data.iloc[k]['StateChange']
                    if stateChange == 1 and (data.iloc[k]["TransShiftInProcess"] ==  b'ShiftIsNotInProcess' or data.iloc[k]["TransShiftInProcess"] ==  b'Shift is not in process'):                                          
                        self.timestampChangeToShiftNotInProcess.append(k)  
                        break 
                else:
                    stateChange = data.iloc[k]['StateChange']
                    # condition = (data.iloc[k]["TransShiftInProcess"] ==  b'ShiftIsNotInProcess' or data.iloc[k]["TransShiftInProcess"] ==  b'Shift is not in process')
                    # print(condition)
                    if stateChange == 1 and (data.iloc[k]["TransShiftInProcess"] ==  b'ShiftIsNotInProcess' or data.iloc[k]["TransShiftInProcess"] ==  b'Shift is not in process') and data.iloc[k]["TransCurrentGear"] == self.selectedGear and data.iloc[k]["TransSelectedGear"] == self.selectedGear:
                        self.timestampChangeToShiftNotInProcess.append(k)  
                                          
                        break 

            try:  
                #print(f'Start: {self.timestampChangeToShiftInProcess} End: {self.timestampChangeToShiftNotInProcess}') 
                self.windows.append(data.iloc[self.timestampChangeToShiftInProcess[j]:self.timestampChangeToShiftNotInProcess[j]])
            except:
                continue
        return self.windows

    def __calculationVDV(self, signal, signal_delta_time, window, dt, diameter=1):
        window.loc[:,f'{signal}Velocity'] = (window.loc[:,f"{signal}"]/60)*diameter
        window.loc[:,f'Delta_{signal}Velocity'] = window.loc[:,f"{signal}Velocity"].diff()
        window.loc[:,f'{signal}Acceleration'] = window.loc[:,f'Delta_{signal}Velocity'] / window.loc[:,f'{signal_delta_time}']
        window.loc[:,f'{signal}AccelerationForth'] = window.loc[:,f'{signal}Acceleration'] ** 4
        integerOS = np.sum(window.loc[:,f'{signal}AccelerationForth']) * dt
        result = f'vdv{signal}'
        result = integerOS ** (1/4)
        return result
    
    def __shiftDurationCalculation(self, signal_delta_time, window):
        return window.loc[:, f'{signal_delta_time}'].sum()
    
    def __dtCalculation(self, signal_delta_time, window):
        return window.loc[:, f'{signal_delta_time}'].median()
    
    def __calculationLFP(self, signal, window):
        maxAccOS = window.loc[:,f'{signal}Acceleration'].max()
        minAccOS = window.loc[:,f'{signal}Acceleration'].min()
        step1= (((maxAccOS) - abs(minAccOS)))
        step2 = maxAccOS
        result = (step1/step2*100)
        return result

    def __maxSignal(self, signal, window):
        return window.loc[:, f"{signal}"].max()
    
    def __minSignal(self, signal, window):
        return window.loc[:, f"{signal}"].min()
    
    def __existsSignalInWindow(self, signal_1, signal_2, window):
        for j in range(len(window)):
            if self.shift_mode == "UPSHIFT":
                if (window.iloc[j][f'{signal_1}'] == window.iloc[j][f'{signal_2}']):
                    result = True
                else:
                    result = False
            else:
                if (window.iloc[j][f'{signal_1}'] == window.iloc[j][f'{signal_2}']):
                    result = True
                else:
                    result = False

        return result
                
                
    def __verificationFirstRow(self, data):
        series = data.index.to_series().diff()
        max_diff_value = series.max()
        max_diff_index = series.idxmax()
        drop = data.loc[(data.index < max_diff_index)]
        
        if np.all(max_diff_value.seconds > 1) and self.__isFirst(drop):
            data = data.drop(drop.index)
        else:
            data = data
    
        return data
    
    def __isFirst(self, drop):
        if len(drop.index) == 1:
            return True
        else:
            return False
        
    def __isShiftMode(self, window):
        if self.shift_mode == "UPSHIFT":
            return False
        else:
            verification =   window['TransCurrentGear'] == int(self.selectedGear - 1)
            result = verification.any()
            return result

    def __normalizedScale(self, signal):
        return (signal - min(signal)) / (max(signal) - min(signal))
        


    def plot(self, res):
        ...
    # #    fig, axs = plt.subplots(2, 2, layout='constrained')
    #     for i in range(len(res)):
    #         x = res[i]['window']
    #         print(x)
        # y1 = data['TransSelectedGear']
        # y2 = data['TransCurrentGear']
        # y3 = data['TransInputShaftSpeed']
        # y4 = data['EngSpeed']
        # y5 = data['TransOutputShaftSpeed']
        # y6 = data['WheelBasedVehicleSpeed']
        # name_1 =res[0]['name']
        # shift_duration_1 = res[0]['shift_duration']
        # VDV_1 = res[0]['VDV']
        # name_2 =res[1]['name']
        # shift_duration_2 = res[1]['shift_duration']
        # VDV_2 = res[1]['VDV']
                
    
        # fig, ax1 = plt.subplots()
        # ax1.plot(x, y1, label="TransSelectedGear", color="orange")
        # ax1.plot(x, y2, label ="TransCurrentGear", color="blue")

        # ax2 = ax1.twinx()
        # ax2.plot(x, y3, label='TransInputShaftSpeed', color= "red")
        # ax2.plot(x, y4, label='EngSpeed', color= "yellow")   
        # ax2.plot(x, y5, label='TransOutputShaftSpeed', color= "grey")
        # ax3 = ax1.twinx()
        # ax3.plot(x, y6, label='WheelBasedVehicleSpeed', color= "black")
        # textstr_1 = f'name={name_1}\nShit Duration={shift_duration_1:.2f}\nVDV={VDV_1:.2f}'
        # textstr_2 = f'name={name_2}\nShit Duration={shift_duration_2:.2f}\nVDV={VDV_2:.2f}'
        # props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        # ax1.text(0.05, 0.55, textstr_1, transform=ax1.transAxes, fontsize=8,
        # verticalalignment='top', bbox=props)
        # ax1.text(0.05, 0.35, textstr_2, transform=ax1.transAxes, fontsize=8,
        # verticalalignment='top', bbox=props)
        # plt.title('VDV WINDOW ANALYSIS')
        # plt.legend() 
        # plt.show()    

    def result(self, result):
        for i in range (len(result)):
            name_IS =result[i]['name_IS']
            name_OS =result[i]['name_OS']
            shift_duration = result[i]['shift_duration']
            vdv_IS = result[i]['VDV_IS']
            vdv_OS = result[i]['VDV_OS']
            selectGear = result[i]['select_gear']
            currentGear = result[i]['current_gear']
            print(f' {i} - The Vibration Dose Value of {name_IS} in {currentGear}->{selectGear} gear is {vdv_IS} with {shift_duration} seconds.')
            print(f' {i} - The Vibration Dose Value of {name_OS} in {currentGear}->{selectGear} gear is {vdv_OS} with {shift_duration} seconds.')
            x = result[i]['window'].index
            y1 = result[i]['window']['TransSelectedGear']
            y2 = result[i]['window']['TransCurrentGear']
            y3 = result[i]['window']['TransInputShaftSpeed']
            y4 = result[i]['window']['EngSpeed']
            y5 = result[i]['window']['TransOutputShaftSpeed']
            y6 = result[i]['window']['WheelBasedVehicleSpeed']
            
            fig, ax1 = plt.subplots()
            ax1.plot(x, y1, label="TransSelectedGear", color="orange")
            ax1.plot(x, y2, label ="TransCurrentGear", color="blue")

            ax2 = ax1.twinx()
            ax2.plot(x, y3, label='TransInputShaftSpeed', color= "red")
            ax2.plot(x, y4, label='EngSpeed', color= "yellow")   
            ax2.plot(x, y5, label='TransOutputShaftSpeed', color= "grey")
            ax3 = ax1.twinx()
            ax3.plot(x, y6, label='WheelBasedVehicleSpeed', color= "black")
            textstr_1 = f'name={name_IS}\nShit Duration={shift_duration:.2f}\nVDV={vdv_IS:.2f}'
            textstr_2 = f'name={name_OS}\nShit Duration={shift_duration:.2f}\nVDV={vdv_OS:.2f}'
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax1.text(0.05, 0.55, textstr_1, transform=ax1.transAxes, fontsize=8,
            verticalalignment='top', bbox=props)
            ax1.text(0.05, 0.35, textstr_2, transform=ax1.transAxes, fontsize=8,
            verticalalignment='top', bbox=props)
            plt.legend() 
            plt.title('VDV WINDOW ANALYSIS')
        
        plt.show()    

            