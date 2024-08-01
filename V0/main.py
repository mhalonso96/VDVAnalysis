from asammdf import MDF
import matplotlib.pyplot as plt
from datetime import timedelta
import glob, sys, os
from pathlib import Path
import numpy as np
import pandas
# set variables
mdf_extension = ".MDF"
input_folder = "input"
output_folder = "output"

# load MDF/DBC files from input folder
path = Path(__file__).parent.absolute()
path_in = Path(path, input_folder)
path_out = Path(path, output_folder)

logfiles = list(path_in.glob("*" + mdf_extension))
signals = [
    "TransCurrentGear",

    "TransSelectedGear",
    "ActualEngPercentTorque",
    "EngReferenceTorque",
    "NominalFrictionPercentTorque",
    "WheelBasedVehicleSpeed",
    "EngSpeed",
    "TransOutputShaftSpeed",
    "TransInputShaftSpeed",
    ]

print("Log file(s): ", logfiles)

mdf = MDF.concatenate(logfiles)
mdf_scaled = mdf.filter(signals)
mdf_scaled.export(
    "csv", filename=Path(path_out, "scaled"), time_as_date=True, time_from_zero=False, single_time_base=True, raster=0.5,
)



pd = mdf_scaled.to_dataframe(time_as_date=True)
filtered_df = pd.loc[pd["TransSelectedGear"] != pd["TransCurrentGear"]]  
filter_df_Selected = filtered_df.loc[filtered_df['TransSelectedGear'] == 2] 
filter_df_Current = filter_df_Selected.loc[(filter_df_Selected['TransCurrentGear'] >= 1) & (filter_df_Selected['TransCurrentGear'] <= 2) ] 
data = filter_df_Current

start_index = 0
windows = []
maxGearArray = []



for  i in range(0, len(data)):
    maxTransCurrentGear = data.iloc[i]['TransCurrentGear'] 
    if maxTransCurrentGear > 1.98 and maxTransCurrentGear <=2:
        test = maxGearArray.append(maxTransCurrentGear)
        
    for j in range(len(maxGearArray)):
        if data.iloc[i]["TransCurrentGear"] == maxGearArray[j]:
            end_index = i
            windows.append(data.iloc[start_index:end_index+1])
            start_index = i + 1
           
for i in range(len(windows)):
    window = pandas.DataFrame(windows[i])
    window.loc[:,'Delta_Time'] = window.loc[:,"Time"].diff()
    shiftDuration = window.loc[:, 'Delta_Time'].sum()
    dt = window.loc[:, 'Delta_Time'].median()

    window.loc[:,'TransOutputShaftSpeedVelocity'] = (window.loc[:,"TransOutputShaftSpeed"]/60)*0.762
    window.loc[:,'Delta_TransOutputShaftSpeedVelocity'] = window.loc[:,"TransOutputShaftSpeedVelocity"].diff()
    window.loc[:,'TransOutputShaftAcceleration'] = window.loc[:,'Delta_TransOutputShaftSpeedVelocity'] / window.loc[:,'Delta_Time']
    window.loc[:,'TransOutputShaftAccelerationForth'] = window.loc[:,'TransOutputShaftAcceleration'] ** 4
    integerOS = np.sum(window.loc[:,'TransOutputShaftAccelerationForth']) * dt
    vdvOS = integerOS ** (1/4)

    window.loc[:,'TransInputShaftSpeedVelocity'] = (window.loc[:,"TransInputShaftSpeed"]/60)*0.762
    window.loc[:,'Delta_TransInputShaftSpeedVelocity'] = window.loc[:,"TransInputShaftSpeedVelocity"].diff()
    window.loc[:,'TransInputShaftAcceleration'] = window.loc[:,'Delta_TransInputShaftSpeedVelocity'] / window.loc[:,'Delta_Time']
    window.loc[:,'TransInputShaftAccelerationForth'] = window.loc[:,'TransInputShaftAcceleration'] ** 4
    integerIS = np.sum(window.loc[:,'TransInputShaftAccelerationForth']) * dt
    vdvIS = integerIS ** (1/4)

    window.loc[:,'EngSpeedVelocity'] = (window.loc[:,"EngSpeed"]/60)*0.762
    window.loc[:,'Delta_EngSpeedVelocity'] = window.loc[:,"EngSpeedVelocity"].diff()
    window.loc[:,'EngSpeedAcceleration'] = window.loc[:,'Delta_EngSpeedVelocity'] / window.loc[:,'Delta_Time']
    window.loc[:,'EngSpeedAccelerationForth'] = window.loc[:,'EngSpeedAcceleration'] ** 4
    integerES = np.sum(window.loc[:,'EngSpeedAccelerationForth']) * dt
    vdvES = integerES ** (1/4)

    window = window.fillna(0)

    results = [{
        'Name' : "TRANS INPUT SHAFT SPEED",
        'Shift Duration' : shiftDuration, 
        'dt': dt,
        'integer': integerIS,
        'VDV': vdvIS
    },
    {
        'Name' : "TRANS OUTPUT SHAFT SPEED",
        'Shift Duration' : shiftDuration, 
        'dt': dt,
        'integer': integerOS,
        'VDV': vdvOS
    },
    {   'Name' : "ENG SPEED",
        'Shift Duration' : shiftDuration, 
        'dt': dt,
        'integer': integerES,
        'VDV': vdvES
    }]
    print(results)
    # filtered_df = filtered_df.drop(columns=["Time"])
    window.to_csv(f'VDV_Project_{i}_v2.csv')
   




# # mdf_scaled.export(
# #     "csv", filename=Path(path_out, "scaled"), time_as_date=True, time_from_zero=False, single_time_base=True, raster=0.5,
# # )

