import streamlit as st
from datetime import datetime
import json
import os
from database_manager import DatabaseManager

class PortfolioManager:
    def __init__(self):
        self.portfolios_file = "portfolios.json"
        self.db_manager = DatabaseManager()
        self.load_portfolios()
    
    def load_portfolios(self):
        """Load portfolios from database"""
        try:
            # Try to migrate from JSON file if it exists
            if os.path.exists(self.portfolios_file):
                self.db_manager.migrate_from_json(self.portfolios_file)
            
            # Load from database
            portfolio_data = self.db_manager.load_portfolios()
            
            if 'portfolios' not in st.session_state:
                st.session_state.portfolios = portfolio_data
        except Exception as e:
            st.error(f"Error loading portfolios: {str(e)}")
    
    def save_portfolios(self):
        """Save portfolios to database"""
        try:
            for portfolio_name, portfolio_data in st.session_state.portfolios.items():
                self.db_manager.save_portfolio(portfolio_name, portfolio_data)
        except Exception as e:
            st.error(f"Error saving portfolios: {str(e)}")
    
    def create_portfolio(self, name):
        """Create a new portfolio"""
        if name not in st.session_state.portfolios:
            portfolio_data = {
                'stocks': {},
                'created_date': datetime.now()
            }
            st.session_state.portfolios[name] = portfolio_data
            self.db_manager.save_portfolio(name, portfolio_data)
            return True
        return False
    
    def delete_portfolio(self, name):
        """Delete a portfolio"""
        if name in st.session_state.portfolios:
            del st.session_state.portfolios[name]
            self.db_manager.delete_portfolio(name)
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
            
            self.db_manager.add_stock(portfolio_name, symbol, shares, avg_price)
            return True
        return False
    
    def remove_stock(self, portfolio_name, symbol):
        """Remove a stock from a portfolio"""
        if portfolio_name in st.session_state.portfolios:
            portfolio = st.session_state.portfolios[portfolio_name]
            if symbol in portfolio['stocks']:
                del portfolio['stocks'][symbol]
                self.db_manager.remove_stock(portfolio_name, symbol)
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
                self.db_manager.update_stock(portfolio_name, symbol, shares, avg_price)
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
