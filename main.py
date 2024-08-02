from utils.vdvanalysis import VDVAnalysis
import matplotlib.pyplot as plt

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
    "TransShiftInProcess"
    ]
mdf_extension = ".MDF"
input_folder = "logs"

test = VDVAnalysis(currentGear=4,
                    selectedGear=5, 
                    signals=signals, 
                    mdf_extension=mdf_extension, 
                    input_folder=input_folder,
                    shift_mode="UPSHIFT"
                    )

res = test.analyzer()
print(test.result(res, index=0))
print(test.result(res, index=1))
print(test.result(res, index=2))