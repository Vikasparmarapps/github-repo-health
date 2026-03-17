# agents/chart_generator.py
"""
Chart Generator Agent - Generates interactive cryptocurrency charts
Integrates with existing Binance AI Agent architecture

Charts generated:
1. Candlestick (OHLCV + volume)
2. Price Trend (line + SMA)
3. RSI Indicator
4. Volume Analysis
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


# ════════════════════════════════════════════════════════════════
# INDICATOR CALCULATIONS
# ════════════════════════════════════════════════════════════════

def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100. / (1. + rs)
    
    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        
        rs = up / down if down != 0 else 0
        rsi[i] = 100. - 100. / (1. + rs)
    
    return rsi


def calculate_sma(prices, period):
    """Calculate Simple Moving Average"""
    return pd.Series(prices).rolling(window=period).mean().values


# ════════════════════════════════════════════════════════════════
# CHART GENERATORS
# ════════════════════════════════════════════════════════════════

def generate_candlestick_chart(klines_data, symbol):
    """
    Generate candlestick chart with volume
    
    Args:
        klines_data: List of [timestamp, open, high, low, close, volume, ...]
        symbol: Cryptocurrency symbol (BTC, ETH, etc.)
    
    Returns:
        plotly.graph_objects.Figure
    """
    try:
        df = pd.DataFrame(klines_data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'buy_volume', 'buy_quote_volume'
        ])
        
        # Convert types
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.dropna()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.12,
            row_heights=[0.7, 0.3],
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # Candlestick
        fig.add_trace(
            go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name=f"{symbol}/USDT",
                hovertemplate="<b>%{x|%Y-%m-%d %H:%M}</b><br>" +
                              "O: $%{open:.2f} | H: $%{high:.2f}<br>" +
                              "L: $%{low:.2f} | C: $%{close:.2f}<extra></extra>"
            ),
            row=1, col=1
        )
        
        # Volume
        colors = ['red' if close < open_ else 'green'
                  for close, open_ in zip(df['close'], df['open'])]
        
        fig.add_trace(
            go.Bar(
                x=df['timestamp'],
                y=df['volume'],
                name='Volume',
                marker=dict(color=colors),
                hovertemplate="<b>%{x|%Y-%m-%d %H:%M}</b><br>Vol: %{y:.2f}<extra></extra>"
            ),
            row=2, col=1
        )
        
        # Layout
        fig.update_layout(
            title=f"<b>{symbol}/USDT Candlestick</b>",
            height=600,
            hovermode='x unified',
            template='plotly_dark',
            font=dict(size=11),
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_yaxes(title_text="Price (USDT)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        return fig
        
    except Exception as e:
        raise Exception(f"Candlestick chart error: {str(e)}")


def generate_line_chart(klines_data, symbol):
    """Generate price trend line chart with moving averages"""
    try:
        df = pd.DataFrame(klines_data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'buy_volume', 'buy_quote_volume'
        ])
        
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.dropna()
        
        sma_20 = calculate_sma(df['close'].values, 20)
        sma_50 = calculate_sma(df['close'].values, 50)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['close'],
            mode='lines', name=f"{symbol} Price",
            line=dict(color='#1f77b4', width=2),
            hovertemplate="<b>%{x|%Y-%m-%d %H:%M}</b><br>$%{y:.2f}<extra></extra>"
        ))
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=sma_20,
            mode='lines', name='SMA 20',
            line=dict(color='#ff7f0e', width=1.5, dash='dash'),
            hovertemplate="<b>SMA 20:</b> $%{y:.2f}<extra></extra>"
        ))
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=sma_50,
            mode='lines', name='SMA 50',
            line=dict(color='#2ca02c', width=1.5, dash='dash'),
            hovertemplate="<b>SMA 50:</b> $%{y:.2f}<extra></extra>"
        ))
        
        fig.update_layout(
            title=f"<b>{symbol}/USDT Price Trend</b>",
            height=500,
            hovermode='x unified',
            template='plotly_dark',
            font=dict(size=11),
            xaxis_title="Time",
            yaxis_title="Price (USDT)",
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        return fig
        
    except Exception as e:
        raise Exception(f"Line chart error: {str(e)}")


def generate_rsi_chart(klines_data, symbol, period=14):
    """Generate RSI indicator chart"""
    try:
        df = pd.DataFrame(klines_data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'buy_volume', 'buy_quote_volume'
        ])
        
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.dropna()
        
        rsi = calculate_rsi(df['close'].values, period)
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.12,
            row_heights=[0.6, 0.4],
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # Price
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], y=df['close'],
                mode='lines', name=f"{symbol} Price",
                line=dict(color='#1f77b4', width=2),
                hovertemplate="<b>%{x|%Y-%m-%d %H:%M}</b><br>$%{y:.2f}<extra></extra>"
            ),
            row=1, col=1
        )
        
        # RSI
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], y=rsi,
                mode='lines', name='RSI (14)',
                line=dict(color='#d62728', width=2),
                hovertemplate="<b>RSI:</b> %{y:.1f}<extra></extra>"
            ),
            row=2, col=1
        )
        
        # Overbought/Oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color="orange",
                      row=2, col=1, annotation_text="Overbought")
        fig.add_hline(y=30, line_dash="dash", line_color="cyan",
                      row=2, col=1, annotation_text="Oversold")
        
        fig.update_layout(
            title=f"<b>{symbol}/USDT RSI Analysis</b>",
            height=600,
            hovermode='x unified',
            template='plotly_dark',
            font=dict(size=11),
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        fig.update_yaxes(title_text="Price (USDT)", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
        fig.update_xaxes(title_text="Time", row=2, col=1)
        
        return fig
        
    except Exception as e:
        raise Exception(f"RSI chart error: {str(e)}")


def generate_volume_chart(klines_data, symbol):
    """Generate volume analysis chart"""
    try:
        df = pd.DataFrame(klines_data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'buy_volume', 'buy_quote_volume'
        ])
        
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        df['open'] = pd.to_numeric(df['open'], errors='coerce')
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.dropna()
        
        colors = ['red' if close < open_ else 'green'
                  for close, open_ in zip(df['close'], df['open'])]
        
        volume_ma = pd.Series(df['volume']).rolling(window=20).mean().values
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.12,
            row_heights=[0.6, 0.4],
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # Price
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], y=df['close'],
                mode='lines', name=f"{symbol} Price",
                line=dict(color='#1f77b4', width=2),
                hovertemplate="<b>%{x|%Y-%m-%d %H:%M}</b><br>$%{y:.2f}<extra></extra>"
            ),
            row=1, col=1
        )
        
        # Volume
        fig.add_trace(
            go.Bar(
                x=df['timestamp'], y=df['volume'],
                name='Volume',
                marker=dict(color=colors),
                hovertemplate="<b>%{x|%Y-%m-%d %H:%M}</b><br>%{y:.0f}<extra></extra>"
            ),
            row=2, col=1
        )
        
        # Volume MA
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], y=volume_ma,
                mode='lines', name='Volume MA (20)',
                line=dict(color='yellow', width=2, dash='dash'),
                hovertemplate="<b>Vol MA:</b> %{y:.0f}<extra></extra>"
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=f"<b>{symbol}/USDT Volume Analysis</b>",
            height=600,
            hovermode='x unified',
            template='plotly_dark',
            font=dict(size=11),
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        fig.update_yaxes(title_text="Price (USDT)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_xaxes(title_text="Time", row=2, col=1)
        
        return fig
        
    except Exception as e:
        raise Exception(f"Volume chart error: {str(e)}")


# ════════════════════════════════════════════════════════════════
# MAIN CHART GENERATOR FUNCTION
# ════════════════════════════════════════════════════════════════

def run_chart_generator(symbol, price_data):
    """
    Generate all charts from price data
    
    Args:
        symbol: Cryptocurrency symbol (BTC, ETH, etc.)
        price_data: Dict with 'klines' key containing OHLCV data
    
    Returns:
        Dict with chart figures
    """
    try:
        klines = price_data.get("klines", [])
        
        if not klines or len(klines) < 20:
            return {
                "success": False,
                "error": "Insufficient data for charts",
                "charts": {}
            }
        
        charts = {
            "candlestick": generate_candlestick_chart(klines, symbol),
            "trend": generate_line_chart(klines, symbol),
            "rsi": generate_rsi_chart(klines, symbol),
            "volume": generate_volume_chart(klines, symbol),
        }
        
        return {
            "success": True,
            "charts": charts,
            "symbol": symbol,
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Chart generation failed: {str(e)}",
            "charts": {}
        }
