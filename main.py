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
# df = res[0][3]
# fig, ax = plt.subplot()
# ax3 = ax.twinx()
# rspine = ax3.spines['right']
# rspine.set_position(('axes', 1.15))
# # Plote os dados nos eixos
# df['EngSpeed'].plot(ax=ax, style='b-')
# # df[].plot(ax=ax, style='r-', secondary_y=True)
# # df.C.plot(ax=ax3, style='g-')
print(test.result(res, index=0))
print(test.result(res, index=1))
print(test.result(res, index=2))