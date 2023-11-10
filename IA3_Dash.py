import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px


# Import the CSV file
try:
    df = pd.read_csv('C:\\Users\\HP\\Desktop\\SQIT5043 Programming For Analytics_Python Project\\Indiviual Assignment 3 Dash\\2023 Scrap List.csv')
except FileNotFoundError:
    print("Error: CSV file not found. Please check the file path.")
    raise SystemExit

# Check the column names in the DataFrame
print("Column Names in the DataFrame:")
print(df.columns)

# Convert 'Date' to datetime format
try:
    df['Appropriate Date'] = pd.to_datetime(df['Appropriate Date'], format='%d/%m/%Y')
except KeyError:
    print("Error: 'Appropriate Date' column not found. Please check the column name.")
    raise SystemExit

# Filter the DataFrame to include only rows where 'Scrap Reason' is 'LBC-L'
filtered_df = df[df['Scrap Reason'] == 'LBC-L']

# Check if filtered DataFrame is empty
if filtered_df.empty:
    print("Error: No data found for 'Scrap Reason' equals 'LBC-L'.")
    raise SystemExit

# Group by 'Date' and find the sum of 'LBC-L' in 'Scrap Reason'
df_grouped_day = filtered_df.groupby(filtered_df['Appropriate Date'].dt.date)['Scrap Reason'].count()

# Group by 'Month' for Bar Chart
df['Month'] = filtered_df['Appropriate Date'].dt.to_period('M')
df_grouped_month = df.groupby(df['Month'])['Scrap Reason'].count().reset_index()
df_grouped_month['Month'] = df_grouped_month['Month'].dt.to_timestamp()

# Group by 'Year' for Pie Chart
df['Year'] = filtered_df['Appropriate Date'].dt.to_period('Y')
df_grouped_year = df.groupby(df['Year'])['Scrap Reason'].count().reset_index()
df_grouped_year['Year'] = df_grouped_year['Year'].dt.to_timestamp()

print(filtered_df)

# Convert 'Month' column to string format for filtering
df['Month'] = df['Month'].astype(str)

# Get unique months from the DataFrame for the dropdown options
available_months = df['Month'].unique()

# Initialize Dash app
app = dash.Dash(__name__)

# Define layout with both line chart, bar chart, and month filter
app.layout = html.Div([
    html.H1('Bladder Leak Scrap Trend 2023'),

    # Month Filter Dropdown
    html.Div([
        html.Label('Select Month:'),
        dcc.Dropdown(
            id='month-filter',
            options=[{'label': month, 'value': month} for month in available_months],
            multi=True  # Allow multiple selection
        ),
    ]),

     # Bar Chart
    html.Div([
        html.H2('Total Bladder Leak Scrap Per Month (in Pcs)'),
        dcc.Graph(id='bar-chart'),
    ], style={'width': '49%', 'display': 'inline-block'}),

    # Line Chart
    html.Div([
        html.H2('Daily Bladder Leak Scrap Trend (in Pcs)'),
        dcc.Graph(id='line-chart'),
    ], style={'width': '49%', 'display': 'inline-block'}),

])

# Define callbacks to update charts based on selected month
@app.callback(
    [Output('line-chart', 'figure'),
     Output('bar-chart', 'figure')],
    [Input('month-filter', 'value')]
)
def update_charts(selected_months):
    # Filter data based on selected months
    if selected_months:
        filtered_data = df[df['Month'].isin(selected_months)]
    else:
        filtered_data = df  # Show all data if no month is selected

    # Group by 'Date' and find the sum of 'LBC-L' in 'Scrap Reason' for the line chart
    line_chart_data = filtered_data.groupby(filtered_data['Appropriate Date'].dt.date)['Scrap Reason'].count()

    # Group by 'Month' for the bar chart
    bar_chart_data = filtered_data.groupby(filtered_data['Month'])['Scrap Reason'].count().reset_index()
    bar_chart_data['Month'] = pd.to_datetime(bar_chart_data['Month'])  # Convert 'Month' back to timestamp

    # Create line chart and bar chart figures with data labels
    line_chart_figure = px.line(line_chart_data, x=line_chart_data.index, y='Scrap Reason', labels={'Scrap Reason': 'Total Scrap (in Pcs)'})
    line_chart_figure.update_traces(text=line_chart_data.values, mode='lines+text', textposition='top center')

    bar_chart_figure = px.bar(bar_chart_data, x='Month', y='Scrap Reason', labels={'Scrap Reason': 'Total Scrap (in Pcs)'})
    bar_chart_figure.update_traces(text=bar_chart_data['Scrap Reason'], textposition='outside')

    # Set maximum y-axis value for the bar chart
    bar_chart_figure.update_yaxes(range=[0, 400])

    return line_chart_figure, bar_chart_figure

if __name__ == '__main__':
    app.run_server(debug=True)