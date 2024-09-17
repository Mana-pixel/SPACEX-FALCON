# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into a pandas DataFrame
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Determine the maximum and minimum payload values for the slider
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'Cape Canaveral Launch Complex 40 (CAFS LC-40)', 'value': 'CCAFS LC-40'},
            {'label': 'Cape Canaveral Space Launch Complex 40 (CCAFS SLC-40)', 'value': 'CCAFS SLC-40'},
            {'label': 'Kennedy Space Center Launch Complex 39A (KSC LC-39A)', 'value': 'KSC LC-39A'},
            {'label': 'Vandenberg Air Force Base Space Launch Complex (VAFB SLC-4E)', 'value': 'VAFB SLC-4E'}
        ],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    
    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback for updating the pie chart based on the selected site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        filtered_df = spacex_df.groupby('Launch Site').mean().reset_index()
        return px.pie(filtered_df, values='class', names='Launch Site', title='Launch Success Rate For All Sites')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        filtered_df['outcome'] = filtered_df['class'].apply(lambda x: 'Success' if x == 1 else 'Failure')
        return px.pie(filtered_df, values='outcome', names='outcome', title='Launch Success Rate For ' + entered_site)

# Callback for updating the scatter chart based on the selected site and payload range
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id="payload-slider", component_property="value")]
)
def get_scatter_chart(entered_site, slider):
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= slider[0]) &
        (spacex_df['Payload Mass (kg)'] <= slider[1])
    ]
    
    if entered_site == 'ALL':
        return px.scatter(
            filtered_df,
            x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title='Launch Success Rate For All Sites'
        )
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        return px.scatter(
            filtered_df,
            x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title='Launch Success Rate For ' + entered_site
        )

if __name__ == '__main__':
    app.run_server(port=8080)
          