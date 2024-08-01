from pathlib import Path
from asammdf import MDF
import numpy as np
import pandas as pd

class VDVAnalysis:
    def __init__(self, currentGear, selectedGear, signals, mdf_extension, input_folder, output_folder, shift_mode) -> None:
        self.currentGear = int(currentGear)
        self.selectedGear = int(selectedGear)
        self.MAXCURRENTGEAR = float(f'{currentGear}.9')
        self.MINCURRENTGEAR = float(f'{selectedGear}.06')
        self.signals = signals
        self.mdf_extension = mdf_extension
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.shift_mode = shift_mode

    def __initialization(self):
        # load MDF/DBC files from input folder
        path = Path(__file__).parent.absolute()
        path_in = Path(path, self.input_folder)
        path_out = Path(path, self.output_folder)

        logfiles = list(path_in.glob("*" + self.mdf_extension))
        mdf = MDF.concatenate(logfiles)
        mdf_scaled = mdf.filter(self.signals)
        frame = mdf_scaled.to_dataframe(time_as_date=True)
        
        filtered_df = frame.loc[frame["TransSelectedGear"] != frame["TransCurrentGear"]]  
        filter_df_Selected = filtered_df.loc[filtered_df['TransSelectedGear'] == self.selectedGear] 
        if self.shift_mode == "UPSHIFT":
            filter_df_Current = filter_df_Selected.loc[(filter_df_Selected['TransCurrentGear'] >= self.currentGear) & (filter_df_Selected['TransCurrentGear'] <= self.selectedGear) ] 
        else:
            filter_df_Current = filter_df_Selected.loc[(filter_df_Selected['TransCurrentGear'] <= self.currentGear) & (filter_df_Selected['TransCurrentGear'] >= self.selectedGear) ]
            
        data = self.__verificationFirstRow(filter_df_Current)
        
        print(f'Initialization VDV completed')
        # data.to_csv('teste4.csv')
        return data
    
    def __processing(self, data):
        start_index = 0
        windows = []
        maxGearArray = []
      
                
        for  i in range(0, len(data)):
            maxTransCurrentGear = data.iloc[i]['TransCurrentGear']             
            if self.shift_mode == "UPSHIFT":
                                   
                if maxTransCurrentGear >= self.MAXCURRENTGEAR and maxTransCurrentGear < self.selectedGear:
                    maxGearArray.append(maxTransCurrentGear)
            else:
                if maxTransCurrentGear <= self.MINCURRENTGEAR and maxTransCurrentGear > self.selectedGear:
                    maxGearArray.append(maxTransCurrentGear)

            
            for j in range(len(maxGearArray)):
                if self.shift_mode == "UPSHIFT":
                    data.loc[data["TransCurrentGear"] > self.MAXCURRENTGEAR, "TransCurrentGear"][j] = self.MAXCURRENTGEAR 
                else:
                    data.loc[data["TransCurrentGear"] < self.MINCURRENTGEAR, "TransCurrentGear"][j] = self.MINCURRENTGEAR 

                if data.iloc[i]["TransCurrentGear"] == maxGearArray[j]:
                    end_index = i
                    windows.append(data.iloc[start_index:end_index+1])
                    start_index = i + 1
        print(f'Process VDV finished')
        return windows

    def analyzer(self):
        data = self.__initialization()
        windows = self.__processing(data)
        results = []
        for i in range(len(windows)):
            window = pd.DataFrame(windows[i])
            

            if len(window) > 20:

                window.loc[:,'Delta_Time'] = window.index.to_series().diff()
                window.loc[:,'Delta_Time'] = window.loc[:,'Delta_Time'].dt.total_seconds()
                shiftDuration = self.__shiftDurationCalculation(signal_delta_time="Delta_Time", window=window)
                dt = self.__dtCalculation(signal_delta_time="Delta_Time", window=window)
                vdvIS = self.__calculationVDV(signal="TransInputShaftSpeed",signal_delta_time="Delta_Time", window=window, dt=dt, diameter=0.762)
                vdvOS = self.__calculationVDV(signal="TransOutputShaftSpeed",signal_delta_time="Delta_Time", window=window, dt=dt, diameter=0.762)
                vdvES = self.__calculationVDV(signal="EngSpeed",signal_delta_time="Delta_Time", window=window, dt=dt, diameter=0.762)
                window = window.fillna(0)
                
                result = [{
                    'name' : "TRANS INPUT SHAFT SPEED",
                    'shift_duration' : shiftDuration, 
                    'VDV': vdvIS,
                    'select_gear' : self.selectedGear,
                    'current_gear' : self.currentGear
                },
                {
                    'name' : "TRANS OUTPUT SHAFT SPEED",
                    'shift_duration' : shiftDuration,
                    'VDV': vdvOS,
                    'select_gear' : self.selectedGear,
                    'current_gear' : self.currentGear,
                },
                {   'name' : "ENG SPEED",
                    'shift_duration' : shiftDuration,
                    'VDV': vdvES,
                    'select_gear' : self.selectedGear,
                    'current_gear' : self.currentGear,
                }]
                window.to_csv(f'VDV_{self.shift_mode}_{self.selectedGear}_GEAR_{i}_.csv') 
                results.append(result)
        print(f'Analyzer VDV finished')
        return results

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
        
    def result(self, result, index):
        for i in range (len(result)):
            name =result[i][index]['name']
            shift_duration = result[i][index]['shift_duration']
            VDV = result[i][index]['VDV']
            selectGear = result[i][index]['select_gear']
            currentGear = result[i][index]['current_gear']
            print(f' The Vibration Dose Value of {name} in {currentGear}->{selectGear} gear is {VDV} with {shift_duration} seconds.')
