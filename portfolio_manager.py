import streamlit as st
from datetime import datetime
import json
import os

class PortfolioManager:
    def __init__(self):
        self.portfolios_file = "portfolios.json"
        self.load_portfolios()
    
    def load_portfolios(self):
        """Load portfolios from file if exists"""
        try:
            if os.path.exists(self.portfolios_file):
                with open(self.portfolios_file, 'r') as f:
                    data = json.load(f)
                    # Convert date strings back to datetime objects
                    for portfolio_name, portfolio_data in data.items():
                        if 'created_date' in portfolio_data:
                            portfolio_data['created_date'] = datetime.fromisoformat(portfolio_data['created_date'])
                        for symbol, stock_data in portfolio_data.get('stocks', {}).items():
                            if 'last_updated' in stock_data:
                                stock_data['last_updated'] = datetime.fromisoformat(stock_data['last_updated'])
                    
                    if 'portfolios' not in st.session_state:
                        st.session_state.portfolios = data
        except Exception as e:
            st.error(f"Error loading portfolios: {str(e)}")
    
    def save_portfolios(self):
        """Save portfolios to file"""
        try:
            data = st.session_state.portfolios.copy()
            # Convert datetime objects to strings for JSON serialization
            for portfolio_name, portfolio_data in data.items():
                if 'created_date' in portfolio_data:
                    portfolio_data['created_date'] = portfolio_data['created_date'].isoformat()
                for symbol, stock_data in portfolio_data.get('stocks', {}).items():
                    if 'last_updated' in stock_data:
                        stock_data['last_updated'] = stock_data['last_updated'].isoformat()
            
            with open(self.portfolios_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            st.error(f"Error saving portfolios: {str(e)}")
    
    def create_portfolio(self, name):
        """Create a new portfolio"""
        if name not in st.session_state.portfolios:
            st.session_state.portfolios[name] = {
                'stocks': {},
                'created_date': datetime.now()
            }
            self.save_portfolios()
            return True
        return False
    
    def delete_portfolio(self, name):
        """Delete a portfolio"""
        if name in st.session_state.portfolios:
            del st.session_state.portfolios[name]
            self.save_portfolios()
            return True
        return False
    
    def add_stock(self, portfolio_name, symbol, shares, avg_price):
        """Add or update a stock in a portfolio"""
        if portfolio_name in st.session_state.portfolios:
            portfolio = st.session_state.portfolios[portfolio_name]
            
            if symbol in portfolio['stocks']:
                # Update existing position
                existing = portfolio['stocks'][symbol]
                total_shares = existing['shares'] + shares
                total_cost = (existing['shares'] * existing['avg_price']) + (shares * avg_price)
                new_avg_price = total_cost / total_shares
                
                portfolio['stocks'][symbol] = {
                    'shares': total_shares,
                    'avg_price': new_avg_price,
                    'last_updated': datetime.now()
                }
            else:
                # Add new position
                portfolio['stocks'][symbol] = {
                    'shares': shares,
                    'avg_price': avg_price,
                    'last_updated': datetime.now()
                }
            
            self.save_portfolios()
            return True
        return False
    
    def remove_stock(self, portfolio_name, symbol):
        """Remove a stock from a portfolio"""
        if portfolio_name in st.session_state.portfolios:
            portfolio = st.session_state.portfolios[portfolio_name]
            if symbol in portfolio['stocks']:
                del portfolio['stocks'][symbol]
                self.save_portfolios()
                return True
        return False
    
    def update_stock(self, portfolio_name, symbol, shares, avg_price):
        """Update a stock position"""
        if portfolio_name in st.session_state.portfolios:
            portfolio = st.session_state.portfolios[portfolio_name]
            if symbol in portfolio['stocks']:
                portfolio['stocks'][symbol] = {
                    'shares': shares,
                    'avg_price': avg_price,
                    'last_updated': datetime.now()
                }
                self.save_portfolios()
                return True
        return False
    
    def get_portfolio_summary(self, portfolio_name):
        """Get summary statistics for a portfolio"""
        if portfolio_name not in st.session_state.portfolios:
            return None
        
        portfolio = st.session_state.portfolios[portfolio_name]
        stocks = portfolio['stocks']
        
        summary = {
            'total_stocks': len(stocks),
            'created_date': portfolio['created_date'],
            'stocks': list(stocks.keys())
        }
        
        return summary
