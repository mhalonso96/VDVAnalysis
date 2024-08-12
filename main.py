from utils.vdvanalysis import VDVAnalysis
import matplotlib.pyplot as plt
import dash
from dash import Dash, html, dcc
from plotly.subplots import make_subplots

import plotly.graph_objs as go

app = dash.Dash(__name__)

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
                    active_plot=True
                    )

res = test.analyzer()

print(test.result(res))

# for i in range(len(res)):
#     data = res[i]['window']
#     name_IS = res[i]['name_IS']
#     name_OS = res[i]['name_OS']
#     shift_duration = res[i]['shift_duration']
#     vdv_IS = res[i]['VDV_IS']
#     vdv_OS = res[i]['VDV_OS']
#     textstr_1 = f'The {name_IS}\nShift Duration is {shift_duration:.2f}\n and VDV is {vdv_IS:.2f}'
#     textstr_2 = f'The {name_OS}\nShift Duration is {shift_duration:.2f}\n and VDV is {vdv_OS:.2f}'

#     fig = go.Figure()
#     fig.add_trace(
#         go.Scatter(x=data.index,
#                 y=data['TransCurrentGear'],
#                 mode='lines+markers',
#                 name='TransCurrentGear')
#     )
#     fig.add_trace(
#         go.Scatter(x=data.index,
#                 y=data['TransSelectedGear'],
#                 mode='lines+markers',
#                 name='TransSelectedGear'),
#     )
#     fig.add_trace(
#         go.Scatter(x=data.index,
#                 y=data['TransInputShaftSpeed'],
#                 mode='lines+markers',
#                 name='TransInputShaftSpeed',
#                 yaxis='y2')  
#     )
#     fig.add_trace(
#         go.Scatter(x=data.index,
#                 y=data['TransOutputShaftSpeed'],
#                 mode='lines+markers',
#                 name='TransOutputShaftSpeed',
#                 yaxis='y3')  
#     )
#     fig.add_trace(
#         go.Scatter(x=data.index,
#                 y=data['EngSpeed'],
#                 mode='lines+markers',
#                 name='EngSpeed',
#                 yaxis='y4')  
#     )
#     fig.update_layout(
#         xaxis=dict(domain=[0.25, 0.75]),
#         yaxis=dict(
#             title="Gears",
#         ),
#         yaxis2=dict(
#             title="TransInputShaftSpeed",
#             overlaying="y",
#             side="right",
#         ),
#         yaxis3=dict(title="TransOutputShaftSpeed",anchor='free',  overlaying="y", side="right", autoshift= True),
#         yaxis4=dict(
#             title="EngSpeed",
#             anchor="free",
#             overlaying="y",
#             side="right",
#             autoshift=True,
#         ),
#     )
#     app.layout = html.Div([
#         html.H1('VDV Analysis'),
#         dcc.Graph(
#             id='VDV Analysis',
#             figure=fig
#         ),
        
#         html.Div(dcc.Input(id='bin1', type='number', value=1),
#                     style={
#                               'display' : 'inline-block',
                              
#                     }),
#         html.H3(
#             f'{textstr_1}'
#         ),
#         html.H3(
#             f'{textstr_2}'
#         )

#     ])
# if __name__ == '__main__':
#     app.run_server(debug=True)


