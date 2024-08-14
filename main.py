from utils.vdvanalysis import VDVAnalysis
import matplotlib.pyplot as plt


signals = [
    "TransCurrentGear",
    "TransSelectedGear",
    "ActualEngPercentTorque",
    # "EngReferenceTorque",
    # "NominalFrictionPercentTorque",
    "WheelBasedVehicleSpeed",
    "EngSpeed",
    "TransOutputShaftSpeed",
    "TransInputShaftSpeed",
    "TransShiftInProcess",
    "LCIBEVO_IBkActive",
    ]
mdf_extension = ".mf4"
input_folder = "logs"

test = VDVAnalysis(currentGear=5,
                    selectedGear=6, 
                    signals=signals, 
                    mdf_extension=mdf_extension, 
                    input_folder=input_folder,
                    shift_mode="UPSHIFT",
                    active_plot=True,
                    to_csv=True,
                    )

res = test.analyzer()
print(test.result(res))

