import streamlit as st
from datetime import datetime
import json
import os
from supabase_manager import SupabaseManager

class PortfolioManager:
    def __init__(self):
        self.portfolios_file = "portfolios.json"
        self.supabase_manager = SupabaseManager()
        self.use_supabase = self.supabase_manager.is_connected()
        self.load_portfolios()
    
    def load_portfolios(self):
        """Load portfolios from Supabase or JSON file fallback"""
        try:
            if self.use_supabase:
                # Try to migrate from JSON file if it exists
                if os.path.exists(self.portfolios_file):
                    self.supabase_manager.migrate_from_json(self.portfolios_file)
                
                # Load from Supabase
                portfolio_data = self.supabase_manager.load_portfolios()
                
                if 'portfolios' not in st.session_state:
                    st.session_state.portfolios = portfolio_data
                    
                if portfolio_data:
                    st.success("✅ Connected to Supabase database!")
                    
            else:
                # Fallback to JSON file
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
                            
                st.info("📁 Using local file storage. Configure Supabase for cloud database.")
                
        except Exception as e:
            st.error(f"Error loading portfolios: {str(e)}")
    
    def save_portfolios(self):
        """Save portfolios to Supabase or JSON file fallback"""
        try:
            if self.use_supabase:
                for portfolio_name, portfolio_data in st.session_state.portfolios.items():
                    self.supabase_manager.save_portfolio(portfolio_name, portfolio_data)
            else:
                # Fallback to JSON file
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
            portfolio_data = {
                'stocks': {},
                'created_date': datetime.now()
            }
            st.session_state.portfolios[name] = portfolio_data
            
            if self.use_supabase:
                self.supabase_manager.save_portfolio(name, portfolio_data)
            else:
                self.save_portfolios()
            return True
        return False
    
    def delete_portfolio(self, name):
        """Delete a portfolio"""
        if name in st.session_state.portfolios:
            del st.session_state.portfolios[name]
            
            if self.use_supabase:
                self.supabase_manager.delete_portfolio(name)
            else:
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
            
            if self.use_supabase:
                self.supabase_manager.add_stock(portfolio_name, symbol, shares, avg_price)
            else:
                self.save_portfolios()
            return True
        return False
    
    def remove_stock(self, portfolio_name, symbol):
        """Remove a stock from a portfolio"""
        if portfolio_name in st.session_state.portfolios:
            portfolio = st.session_state.portfolios[portfolio_name]
            if symbol in portfolio['stocks']:
                del portfolio['stocks'][symbol]
                
                if self.use_supabase:
                    self.supabase_manager.remove_stock(portfolio_name, symbol)
                else:
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
                
                if self.use_supabase:
                    self.supabase_manager.update_stock(portfolio_name, symbol, shares, avg_price)
                else:
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
