import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class StockDataManager:
    def __init__(self):
        self.cache_duration = 300  # Cache for 5 minutes
        self.price_cache = {}
        self.data_cache = {}
    
    def get_current_price(self, symbol):
        """Get current price for a stock symbol"""
        try:
            # Check cache first
            cache_key = f"{symbol}_price"
            if cache_key in self.price_cache:
                cached_data, timestamp = self.price_cache[cache_key]
                if (datetime.now() - timestamp).seconds < self.cache_duration:
                    return cached_data
            
            # Fetch from yfinance
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Try different price fields
            current_price = None
            for price_field in ['regularMarketPrice', 'currentPrice', 'price', 'ask', 'bid']:
                if price_field in info and info[price_field] is not None:
                    current_price = float(info[price_field])
                    break
            
            # If info doesn't have price, try recent history
            if current_price is None:
                hist = ticker.history(period="1d")
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
            
            # Cache the result
            if current_price is not None:
                self.price_cache[cache_key] = (current_price, datetime.now())
            
            return current_price
            
        except Exception as e:
            st.error(f"Error fetching price for {symbol}: {str(e)}")
            return None
    
    def get_historical_data(self, symbol, period="1y"):
        """Get historical data for a stock symbol"""
        try:
            # Check cache first
            cache_key = f"{symbol}_{period}"
            if cache_key in self.data_cache:
                cached_data, timestamp = self.data_cache[cache_key]
                if (datetime.now() - timestamp).seconds < self.cache_duration:
                    return cached_data
            
            # Fetch from yfinance
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            # Reset index to make Date a column
            hist = hist.reset_index()
            
            # Cache the result
            self.data_cache[cache_key] = (hist, datetime.now())
            
            return hist
            
        except Exception as e:
            st.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None
    
    def get_stock_info(self, symbol):
        """Get basic information about a stock"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            stock_info = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'beta': info.get('beta', 'N/A'),
                '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52_week_low': info.get('fiftyTwoWeekLow', 'N/A')
            }
            
            return stock_info
            
        except Exception as e:
            st.error(f"Error fetching info for {symbol}: {str(e)}")
            return None
    
    def validate_symbol(self, symbol):
        """Validate if a stock symbol exists"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Check if we got valid info
            if 'regularMarketPrice' in info or 'currentPrice' in info or 'price' in info:
                return True
            
            # Try to get recent history as fallback
            hist = ticker.history(period="1d")
            return not hist.empty
            
        except Exception:
            return False
    
    def get_multiple_prices(self, symbols):
        """Get current prices for multiple symbols"""
        prices = {}
        for symbol in symbols:
            price = self.get_current_price(symbol)
            if price is not None:
                prices[symbol] = price
        return prices
    
    def calculate_portfolio_value(self, portfolio_stocks):
        """Calculate total portfolio value"""
        total_value = 0
        total_cost = 0
        
        for symbol, stock_info in portfolio_stocks.items():
            current_price = self.get_current_price(symbol)
            if current_price is not None:
                shares = stock_info['shares']
                avg_price = stock_info['avg_price']
                
                current_value = current_price * shares
                cost_basis = avg_price * shares
                
                total_value += current_value
                total_cost += cost_basis
        
        return {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_gain_loss': total_value - total_cost,
            'total_gain_loss_pct': ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
        }
    
    def get_portfolio_historical_data(self, symbols, period="1y"):
        """Get historical data for multiple symbols"""
        all_data = {}
        
        for symbol in symbols:
            data = self.get_historical_data(symbol, period)
            if data is not None:
                all_data[symbol] = data
        
        return all_data
    
    def clear_cache(self):
        """Clear all cached data"""
        self.price_cache.clear()
        self.data_cache.clear()
