# importing libraries
import warnings
warnings.filterwarnings("ignore", "\nPyarrow", DeprecationWarning)  # To ignore pyarrow warning

import pandas as pd     # Pandas for DataFrame object and working with csv
from dash import Dash, html, dcc, callback, Output, Input     # dash for interactive dashboard
import plotly.express as px     # Plotting Library


df = pd.read_csv('NioPracticeUserbase.csv')

print(df.head(5))    # Checking the table structure

print(df.info())    # Quality Assurance of the data i.e. checking for Null values

print(df['Subscription Type'].unique())     # Have 3 unique values
print(df['Country'].unique())     # Have 10 unique values
print(df['Gender'].unique())    # Have 2 unique values
print(df['Device'].unique())    # Have 4 unique values
print(df['Plan Duration'].unique())     # Have only 1 unique value

print(df['Monthly Revenue'].describe())     # Max = 15, Min = 10, Mean = 12.508400

app = Dash(__name__)    # Initializing

# Creating layout using html tags and adding interactive widgets
app.layout = html.Div([
    html.H1('Dashboard', style={'text-align': 'center'}),
    html.Br(),
    html.H2('User Demographics Visualization'),
    html.Label('Select Country'),
    dcc.Dropdown(
        id='gender_dropdown',
        options=[{'label': country, 'value': country} for country in df['Country'].unique()],
        value=df['Country'].unique()[0],  #Default value
        clearable=False, style={'text-align': 'center', 'width':'75%'}
    ),
    dcc.Graph(id='gender_bar', style={'width': '75%'}),
    html.Br(),
    html.H2('Subscription Overview'),
    html.Label('Select Plan Duration'),
    dcc.Dropdown(
        id='subs_dropdown',
        options=[{'label': plan, 'value': plan} for plan in df['Plan Duration'].unique()],
        value=df['Plan Duration'].unique()[0],
        clearable=False, style={'text-align': 'center', 'width':'75%'}
    ),
    dcc.Graph(id='subs_pie', style={'width': '75%'}),
    html.Br(),
    html.H2('Monthly Revenue Trend'),
    dcc.Checklist(
        id='segmentation_checkbox',
        options=[
            {'label': 'Segment by Subscription Type', 'value': 'segmented'},
        ],
        value=[],
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id='revenue_line_chart', style={'width':'75%'}),
    html.H1('Additional Insights'),
    html.Label('Device'),
    dcc.Dropdown(
        id='insight_device',
        options=[{'label': device, 'value': device} for device in df['Device'].unique()],
        value=df['Device'].unique()[0],  #Default value
        clearable=False, style={'text-align': 'center', 'width':'75%'}
    ),
    dcc.Graph(id='device_bar', style={'width': '75%'}),

])

# Decorators to connect the different inputs from widgets to charts
@callback(
    Output('gender_bar', 'figure'),
    [Input('gender_dropdown', 'value')]
)
def gender_count(country):
    filter_country = df[df['Country'] == country]
    gender_counts = filter_country['Gender'].value_counts()
    fig = px.bar(gender_counts, x=gender_counts.index, y=gender_counts.values, color=filter_country['Gender'].unique(),
                 text=gender_counts.values, labels={'x': 'Gender', 'y': 'Count'}, title=f'Gender count in {country}', height=800)
    print(gender_counts)
    return fig

@callback(
    Output('subs_pie', 'figure'),
    [Input('subs_dropdown', 'value')]
)
def subs(duration):
    filter_plan_duration = df[df['Plan Duration'] == duration]
    subs_plan_count = filter_plan_duration['Subscription Type'].value_counts()
    fig = px.pie(subs_plan_count, names=subs_plan_count.index, values=subs_plan_count.values)
    print(subs_plan_count)
    return fig

df['Join Date'] = pd.to_datetime(df['Join Date'])

# Extract year and month from 'Join Date' for grouping
df['YearMonth'] = df['Join Date'].dt.to_period('M').astype(str)

@app.callback(
    Output('revenue_line_chart', 'figure'),
    [Input('segmentation_checkbox', 'value')]
)
def update_revenue_line_chart(checkbox_value):
    if 'segmented' in checkbox_value:
        overall_revenue = df.groupby(['YearMonth', 'Subscription Type'])['Monthly Revenue'].sum().reset_index()
        fig = px.line(overall_revenue, x='YearMonth', y='Monthly Revenue', color='Subscription Type',
                      title='Monthly Revenue Segmented by Subscription Type')
    else:
        overall_revenue = df.groupby('YearMonth')['Monthly Revenue'].sum().reset_index()
        fig = px.line(overall_revenue, x='YearMonth', y='Monthly Revenue',
                      title='Total Monthly Revenue Over Time')
    return fig




# Additional insights
@callback(
    Output('device_bar', 'figure'),
    [Input('insight_device', 'value')]
)
def gender_count(device):
    filter_device = df[df['Device'] == device]
    country_counts = filter_device['Country'].value_counts()
    fig = px.bar(country_counts, x=country_counts.index, y=country_counts.values, color=country_counts.index,
                 text=country_counts.values, labels={'x': 'Country', 'y': 'Count'}, height=800, hover_name=country_counts.index, hover_data={f'{device} users': country_counts.values})
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)