from utils.vdvanalysis import VDVAnalysis
import matplotlib.pyplot as plt

signals = [
    "TransCurrentGear",
    "TransSelectedGear",
    # "ActualEngPercentTorque",
    # "EngReferenceTorque",
    # "NominalFrictionPercentTorque",
    "WheelBasedVehicleSpeed",
    "EngSpeed",
    "TransOutputShaftSpeed",
    "TransInputShaftSpeed",
    "TransShiftInProcess"
    ]
mdf_extension = ".mf4"
input_folder = "logs"

test = VDVAnalysis(currentGear=5,
                    selectedGear=6, 
                    signals=signals, 
                    mdf_extension=mdf_extension, 
                    input_folder=input_folder,
                    shift_mode="UPSHIFT"
                    )

res = test.analyzer()
print(test.result(res))
test.plot(res)

