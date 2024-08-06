from utils.vdvanalysis import VDVAnalysis
import matplotlib.pyplot as plt

signals = [
    "TransCurrentGear",
    "TransSelectedGear",
    # "ActualEngPercentTorque",
    # "EngReferenceTorque",
    # "NominalFrictionPercentTorque",
    # "WheelBasedVehicleSpeed",
    # "EngSpeed",
    "TransOutputShaftSpeed",
    "TransInputShaftSpeed",
    "TransShiftInProcess"
    ]
mdf_extension = ".mf4"
input_folder = "logs"

test = VDVAnalysis(currentGear=10,
                    selectedGear=8, 
                    signals=signals, 
                    mdf_extension=mdf_extension, 
                    input_folder=input_folder,
                    shift_mode="DOWNSHIFT"
                    )

res = test.analyzer()
print(test.result(res, index=0))
print(test.result(res, index=1))
