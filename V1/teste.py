from V1.vdvanalysis import VDVAnalysis
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
input_folder = "input"
output_folder = "output"

test = VDVAnalysis(currentGear=2,
                    selectedGear=1, 
                    signals=signals, 
                    mdf_extension=mdf_extension, 
                    input_folder=input_folder,
                    output_folder=output_folder,
                    shift_mode="DOWSHIFT"
                    )

res = test.analyzer()
print(res)