# Step 1: Data Cleaning
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from sklearn.utils import resample


# Load data (assume CSV from previous step)
filepath = os.path.join("data", 'mock_combined_marketing_data.csv')
df = pd.read_csv(filepath, parse_dates=['timestamp'])

# Basic cleaning
df.dropna(inplace=True)
df = df[df['ad_cost'] >= 0]

# Step 2: Feature Generation - Adstock Transformation
import numpy as np

def adstock(series, alpha=0.5):
    result = []
    carryover = 0
    for val in series:
        carryover = val + carryover * alpha
        result.append(carryover)
    return result

# Apply adstock per channel
df['adstocked_spend'] = df.groupby('channel_name')['ad_cost'].transform(lambda x: adstock(x, alpha=0.6))

# Add time-based features
df['hour'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.dayofweek

# Step 3: Model Fitting using Linear Regression
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

features = ['adstocked_spend', 'homepage_visits', 'branded_searches', 'conversion_rate', 'hour', 'day_of_week']
target = 'sales'

scaler = StandardScaler()
X = scaler.fit_transform(df[features])
y = df[target].values

model = LinearRegression()
model.fit(X, y)

# Step 4: Cross-validation
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error

scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
rmse_scores = np.sqrt(-scores)
print("Cross-validated RMSE:", rmse_scores)

# Step 5: Enhanced Plotly What-If Dashboard
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# List of unique channels
channel_list = df['channel_name'].unique()

# Initialize app
app = dash.Dash(__name__)

# Create sliders for each channel
sliders = [
    html.Div([
        html.Label(f"{channel} Ad Spend:"),
        dcc.Slider(id=f'{channel}-slider', min=0, max=10000, step=100, value=1000)
    ]) for channel in channel_list
]

app.layout = html.Div([
    html.H1("Multi-Channel Marketing Mix Optimization"),
    *sliders,
    html.Div(id='predicted-sales-output', style={'fontSize': 20, 'margin': '20px 0'}),
    dcc.Graph(id='sales-prediction-graph')
])

# Create dynamic inputs
inputs = [Input(f'{channel}-slider', 'value') for channel in channel_list]

@app.callback(
    [Output('sales-prediction-graph', 'figure'),
     Output('predicted-sales-output', 'children')],
    inputs
)
def update_graph(*spend_values):
    spend_dict = dict(zip(channel_list, spend_values))
    total_spend = sum(spend_values)

    # Use channel spend proportions to simulate features
    proportions = {ch: v / total_spend if total_spend > 0 else 0 for ch, v in spend_dict.items()}

    # Simulate new input features based on channel weights
    avg_data = df.groupby('channel_name')[features].mean()

    weighted_inputs = pd.Series(dtype='float64')
    for feature in features:
        weighted_inputs[feature] = sum(proportions[ch] * avg_data.loc[ch, feature] for ch in channel_list)

    X_new = scaler.transform([weighted_inputs])
    predicted_sales = model.predict(X_new)[0]

    # Historical Sales Line
    sales_trend = df.groupby('timestamp')['sales'].sum().reset_index()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=sales_trend['timestamp'],
        y=sales_trend['sales'],
        mode='lines',
        name='Historical Sales',
        line=dict(color='blue')
    ))

    predicted_time = sales_trend['timestamp'].max() + pd.Timedelta(hours=1)
    fig.add_trace(go.Scatter(
        x=[predicted_time],
        y=[predicted_sales],
        mode='markers+text',
        name='Predicted Sales',
        text=['Prediction'],
        textposition='top center',
        marker=dict(color='red', size=10, symbol='diamond')
    ))

    fig.update_layout(
        title='Total Sales Trend with Dynamic Prediction',
        xaxis_title='Time',
        yaxis_title='Sales',
        showlegend=True,
        template='plotly_white'
    )

    predicted_text = f"Predicted Sales: {predicted_sales:,.2f}"

    return fig, predicted_text


if __name__ == '__main__':
    app.run_server(debug=False, port=8051)
