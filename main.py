import yfinance as yf
import pandas_datareader.data as web
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. CONFIGURATION ---
COLOR_RED = "#FF412C"  # Updated Red
COLOR_GREY = "#959595" # Standard Grey

start_date = "2023-01-01"
end_date = "2025-12-01"

print("Fetching real-time data...")

# --- 2. DATA FETCH & PREP ---
afrm = yf.download("AFRM", start=start_date, end=end_date)
afrm_clean = afrm['Close'].reset_index()
afrm_clean.columns = ['Date', 'AFRM_Price']

savings = web.DataReader('PSAVERT', 'fred', start_date, end_date).reset_index()
savings.columns = ['Date', 'Savings_Rate']

# Sync Data (Forward fill monthly savings to daily)
savings_daily = savings.set_index('Date').resample('D').ffill().reset_index()
df = pd.merge(afrm_clean, savings_daily, on='Date', how='inner')

correlation = df['AFRM_Price'].corr(df['Savings_Rate'])

# --- 3. VISUALIZATION ---

fig = make_subplots(specs=[[{"secondary_y": True}]])

# Trace 1: Savings (Grey Line, Grey Text)
fig.add_trace(
    go.Scatter(
        x=df['Date'], y=df['Savings_Rate'],
        name="Personal Savings Rate (%)",
        mode='lines',
        line=dict(color=COLOR_GREY, width=3),
        # HTML styling to force the text color to match the line
        hovertemplate=f"<span style='color:{COLOR_GREY}; font-size:16px; font-weight:bold'>%{{y:.1f}}%</span><extra></extra>"
    ),
    secondary_y=False,
)

# Trace 2: Affirm Stock (Red Line, Red Text)
fig.add_trace(
    go.Scatter(
        x=df['Date'], y=df['AFRM_Price'],
        name="Affirm Stock Price ($)",
        mode='lines',
        line=dict(color=COLOR_RED, width=3),
        # HTML styling to force the text color to match the line
        hovertemplate=f"<span style='color:{COLOR_RED}; font-size:16px; font-weight:bold'>$%{{y:.2f}}</span><extra></extra>"
    ),
    secondary_y=True,
)

# --- 4. LAYOUT & HOVER LOGIC ---

fig.update_layout(
    title=dict(
        text=f"<b>The Divergence Index</b>: Stagnant Savings vs. Exploding Credit Usage",
        font=dict(size=20, family="Arial", color="black"),
        y=0.95
    ),
    plot_bgcolor='white',
    
    # "x" mode keeps tooltips separate so they float near their lines
    hovermode="x", 
    
    # Global hover label settings (White background so colored text pops)
    hoverlabel=dict(
        bgcolor="white",      
        font_size=14, 
        font_family="Arial",
        bordercolor="#black" # Very subtle border
    ),
    
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

# Annotations (Correlation Box)
fig.add_annotation(
    text=f"<b>Statistical Correlation: {correlation:.2f}</b><br>(Inverse relationship)",
    xref="paper", yref="paper",
    x=0.05, y=0.9, showarrow=False,
    bgcolor="rgba(240,240,240,0.8)",
    bordercolor="black", borderwidth=1,
    font=dict(size=12, color="black")
)

# Axis 1: Savings (Grey)
s_min, s_max = df['Savings_Rate'].min(), df['Savings_Rate'].max()
fig.update_yaxes(
    title_text="Savings Rate (%)",
    title_font=dict(color=COLOR_GREY),
    tickfont=dict(color=COLOR_GREY),
    secondary_y=False,
    range=[s_min - 2, s_max + 2],
    showgrid=True, gridcolor='rgba(0,0,0,0.05)'
)

# Axis 2: Affirm (Red)
fig.update_yaxes(
    title_text="Affirm Share Price ($)",
    title_font=dict(color=COLOR_RED),
    tickfont=dict(color=COLOR_RED),
    secondary_y=True,
    showgrid=False
)

# Timeline Cursor (Dotted Line)
fig.update_xaxes(
    title_text="Timeline (Sync Data)",
    showgrid=False,
    rangeslider_visible=True,
    showspikes=True, 
    spikemode="across", 
    spikesnap="cursor", 
    showline=True, 
    linewidth=1, 
    linecolor='black',
    spikedash='dot',
    spikecolor="black",
    spikethickness=1
)

print(f"Generated Divergence Index with Correlation: {correlation:.2f}")
fig.write_html("divergence_index_final.html")
fig.show()