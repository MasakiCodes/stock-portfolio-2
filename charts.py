import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from stock_data import StockDataManager

class ChartManager:
    def __init__(self):
        self.stock_data_manager = StockDataManager()
        self.color_palette = {
            'positive': '#00C851',
            'negative': '#FF4444',
            'neutral': '#33b5e5',
            'background': '#f8f9fa'
        }
    
    def create_stock_chart(self, symbol, period="1y"):
        """Create a candlestick chart for a stock"""
        try:
            data = self.stock_data_manager.get_historical_data(symbol, period)
            if data is None or data.empty:
                return None
            
            # Create candlestick chart
            fig = go.Figure()
            
            fig.add_trace(go.Candlestick(
                x=data['Date'],
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name=symbol,
                increasing_line_color=self.color_palette['positive'],
                decreasing_line_color=self.color_palette['negative']
            ))
            
            # Add volume subplot
            fig.add_trace(go.Bar(
                x=data['Date'],
                y=data['Volume'],
                name='Volume',
                yaxis='y2',
                opacity=0.3,
                marker_color=self.color_palette['neutral']
            ))
            
            # Update layout
            fig.update_layout(
                title=f'{symbol} Stock Price - {period}',
                xaxis_title='Date',
                yaxis_title='Price ($)',
                yaxis2=dict(
                    title='Volume',
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                template='plotly_white',
                height=600,
                showlegend=True,
                hovermode='x unified'
            )
            
            fig.update_xaxes(rangeslider_visible=False)
            
            return fig
            
        except Exception as e:
            print(f"Error creating stock chart for {symbol}: {str(e)}")
            return None
    
    def create_portfolio_pie_chart(self, portfolio_data):
        """Create a pie chart showing portfolio composition"""
        try:
            # Extract data for pie chart
            symbols = [item['Symbol'] for item in portfolio_data]
            values = [float(item['current_value_raw']) for item in portfolio_data]
            
            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=symbols,
                values=values,
                hole=0.3,
                textinfo='label+percent',
                textposition='outside',
                marker=dict(
                    colors=px.colors.qualitative.Set3
                )
            )])
            
            fig.update_layout(
                title='Portfolio Composition by Value',
                template='plotly_white',
                height=500,
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating portfolio pie chart: {str(e)}")
            return None
    
    def create_portfolio_performance_chart(self, symbols, stocks_info):
        """Create a line chart showing portfolio performance over time"""
        try:
            # Get historical data for all symbols
            all_data = self.stock_data_manager.get_portfolio_historical_data(symbols, "1y")
            
            if not all_data:
                return None
            
            # Find common date range
            min_date = None
            max_date = None
            
            for symbol, data in all_data.items():
                if min_date is None or data['Date'].min() > min_date:
                    min_date = data['Date'].min()
                if max_date is None or data['Date'].max() < max_date:
                    max_date = data['Date'].max()
            
            # Create a unified date range
            date_range = pd.date_range(start=min_date, end=max_date, freq='D')
            
            # Calculate portfolio value over time
            portfolio_values = []
            dates = []
            
            for date in date_range:
                if date.weekday() < 5:  # Only weekdays
                    daily_value = 0
                    valid_date = True
                    
                    for symbol, stock_info in stocks_info.items():
                        if symbol in all_data:
                            stock_data = all_data[symbol]
                            # Find the closest date
                            closest_date_idx = stock_data['Date'].sub(date).abs().idxmin()
                            
                            if abs((stock_data['Date'].iloc[closest_date_idx] - date).days) <= 7:
                                price = stock_data['Close'].iloc[closest_date_idx]
                                shares = stock_info['shares']
                                daily_value += price * shares
                            else:
                                valid_date = False
                                break
                    
                    if valid_date and daily_value > 0:
                        portfolio_values.append(daily_value)
                        dates.append(date)
            
            if not portfolio_values:
                return None
            
            # Create line chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=portfolio_values,
                mode='lines',
                name='Portfolio Value',
                line=dict(color=self.color_palette['neutral'], width=2),
                fill='tonexty'
            ))
            
            # Add percentage change
            if len(portfolio_values) > 1:
                initial_value = portfolio_values[0]
                pct_changes = [(val - initial_value) / initial_value * 100 for val in portfolio_values]
                
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=pct_changes,
                    mode='lines',
                    name='% Change',
                    yaxis='y2',
                    line=dict(color=self.color_palette['positive'], width=2, dash='dash')
                ))
            
            fig.update_layout(
                title='Portfolio Performance Over Time',
                xaxis_title='Date',
                yaxis_title='Portfolio Value ($)',
                yaxis2=dict(
                    title='Percentage Change (%)',
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                template='plotly_white',
                height=600,
                showlegend=True,
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating portfolio performance chart: {str(e)}")
            return None
    
    def create_gain_loss_chart(self, portfolio_data):
        """Create a bar chart showing gain/loss for each stock"""
        try:
            symbols = [item['Symbol'] for item in portfolio_data]
            gains_losses = [item['gain_loss_raw'] for item in portfolio_data]
            
            # Color bars based on gain/loss
            colors = [self.color_palette['positive'] if val >= 0 else self.color_palette['negative'] for val in gains_losses]
            
            fig = go.Figure(data=[go.Bar(
                x=symbols,
                y=gains_losses,
                marker_color=colors,
                text=[f"${val:.2f}" for val in gains_losses],
                textposition='auto'
            )])
            
            fig.update_layout(
                title='Gain/Loss by Stock',
                xaxis_title='Stock Symbol',
                yaxis_title='Gain/Loss ($)',
                template='plotly_white',
                height=400,
                showlegend=False
            )
            
            # Add a horizontal line at y=0
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            
            return fig
            
        except Exception as e:
            print(f"Error creating gain/loss chart: {str(e)}")
            return None
    
    def create_sector_allocation_chart(self, symbols):
        """Create a pie chart showing sector allocation"""
        try:
            sector_data = {}
            
            for symbol in symbols:
                stock_info = self.stock_data_manager.get_stock_info(symbol)
                if stock_info and stock_info['sector'] != 'N/A':
                    sector = stock_info['sector']
                    if sector in sector_data:
                        sector_data[sector] += 1
                    else:
                        sector_data[sector] = 1
            
            if not sector_data:
                return None
            
            fig = go.Figure(data=[go.Pie(
                labels=list(sector_data.keys()),
                values=list(sector_data.values()),
                hole=0.3,
                textinfo='label+percent',
                textposition='outside'
            )])
            
            fig.update_layout(
                title='Portfolio Sector Allocation',
                template='plotly_white',
                height=400,
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating sector allocation chart: {str(e)}")
            return None
    
    def create_comparison_chart(self, symbols, period="1y"):
        """Create a comparison chart showing normalized performance of multiple stocks"""
        try:
            fig = go.Figure()
            
            for symbol in symbols:
                data = self.stock_data_manager.get_historical_data(symbol, period)
                if data is not None and not data.empty:
                    # Normalize prices (starting from 100)
                    normalized_prices = (data['Close'] / data['Close'].iloc[0]) * 100
                    
                    fig.add_trace(go.Scatter(
                        x=data['Date'],
                        y=normalized_prices,
                        mode='lines',
                        name=symbol,
                        line=dict(width=2)
                    ))
            
            fig.update_layout(
                title=f'Stock Performance Comparison - {period}',
                xaxis_title='Date',
                yaxis_title='Normalized Price (Base = 100)',
                template='plotly_white',
                height=600,
                showlegend=True,
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating comparison chart: {str(e)}")
            return None
