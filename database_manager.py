import os
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with stocks
    stocks = relationship("Stock", back_populates="portfolio", cascade="all, delete-orphan")

class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    shares = Column(Float)
    avg_price = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Foreign key to portfolio
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    portfolio = relationship("Portfolio", back_populates="stocks")

class DatabaseManager:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        self.create_tables()
    
    def create_tables(self):
        """Create database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
        except Exception as e:
            st.error(f"Error creating database tables: {str(e)}")
    
    def get_db_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def load_portfolios(self):
        """Load portfolios from database"""
        try:
            session = self.get_db_session()
            portfolios = session.query(Portfolio).all()
            
            portfolio_data = {}
            for portfolio in portfolios:
                stocks_data = {}
                for stock in portfolio.stocks:
                    stocks_data[stock.symbol] = {
                        'shares': stock.shares,
                        'avg_price': stock.avg_price,
                        'last_updated': stock.last_updated
                    }
                
                portfolio_data[portfolio.name] = {
                    'stocks': stocks_data,
                    'created_date': portfolio.created_date
                }
            
            session.close()
            return portfolio_data
            
        except Exception as e:
            st.error(f"Error loading portfolios from database: {str(e)}")
            return {}
    
    def save_portfolio(self, portfolio_name, portfolio_data):
        """Save or update a portfolio in the database"""
        session = self.get_db_session()
        try:
            # Check if portfolio exists
            existing_portfolio = session.query(Portfolio).filter(Portfolio.name == portfolio_name).first()
            
            if existing_portfolio:
                # Update existing portfolio
                portfolio_obj = existing_portfolio
                
                # Clear existing stocks
                session.query(Stock).filter(Stock.portfolio_id == portfolio_obj.id).delete()
            else:
                # Create new portfolio
                portfolio_obj = Portfolio(
                    name=portfolio_name,
                    created_date=portfolio_data.get('created_date', datetime.utcnow())
                )
                session.add(portfolio_obj)
                session.flush()  # To get the ID
            
            # Add stocks
            for symbol, stock_data in portfolio_data.get('stocks', {}).items():
                stock_obj = Stock(
                    symbol=symbol,
                    shares=stock_data['shares'],
                    avg_price=stock_data['avg_price'],
                    portfolio_id=portfolio_obj.id
                )
                session.add(stock_obj)
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            st.error(f"Error saving portfolio to database: {str(e)}")
            return False
        finally:
            session.close()
    
    def delete_portfolio(self, portfolio_name):
        """Delete a portfolio from the database"""
        session = self.get_db_session()
        try:
            portfolio = session.query(Portfolio).filter(Portfolio.name == portfolio_name).first()
            if portfolio:
                session.delete(portfolio)
                session.commit()
                return True
            else:
                return False
                
        except Exception as e:
            session.rollback()
            st.error(f"Error deleting portfolio from database: {str(e)}")
            return False
        finally:
            session.close()
    
    def add_stock(self, portfolio_name, symbol, shares, avg_price):
        """Add or update a stock in a portfolio"""
        session = self.get_db_session()
        try:
            portfolio = session.query(Portfolio).filter(Portfolio.name == portfolio_name).first()
            if not portfolio:
                return False
            
            # Check if stock already exists
            existing_stock = session.query(Stock).filter(
                Stock.portfolio_id == portfolio.id,
                Stock.symbol == symbol
            ).first()
            
            if existing_stock:
                # Update existing stock (average the positions)
                total_shares = existing_stock.shares + shares
                total_cost = (existing_stock.shares * existing_stock.avg_price) + (shares * avg_price)
                new_avg_price = total_cost / total_shares
                
                existing_stock.shares = total_shares
                existing_stock.avg_price = new_avg_price
                # Remove the last_updated assignment as it's handled by the database
            else:
                # Create new stock
                new_stock = Stock(
                    symbol=symbol,
                    shares=shares,
                    avg_price=avg_price,
                    portfolio_id=portfolio.id
                )
                session.add(new_stock)
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            st.error(f"Error adding stock to database: {str(e)}")
            return False
        finally:
            session.close()
    
    def remove_stock(self, portfolio_name, symbol):
        """Remove a stock from a portfolio"""
        session = self.get_db_session()
        try:
            portfolio = session.query(Portfolio).filter(Portfolio.name == portfolio_name).first()
            if not portfolio:
                return False
            
            stock = session.query(Stock).filter(
                Stock.portfolio_id == portfolio.id,
                Stock.symbol == symbol
            ).first()
            
            if stock:
                session.delete(stock)
                session.commit()
                return True
            else:
                return False
                
        except Exception as e:
            session.rollback()
            st.error(f"Error removing stock from database: {str(e)}")
            return False
        finally:
            session.close()
    
    def update_stock(self, portfolio_name, symbol, shares, avg_price):
        """Update a stock position"""
        session = self.get_db_session()
        try:
            portfolio = session.query(Portfolio).filter(Portfolio.name == portfolio_name).first()
            if not portfolio:
                return False
            
            stock = session.query(Stock).filter(
                Stock.portfolio_id == portfolio.id,
                Stock.symbol == symbol
            ).first()
            
            if stock:
                stock.shares = shares
                stock.avg_price = avg_price
                # Remove the last_updated assignment as it's handled by the database
                session.commit()
                return True
            else:
                return False
                
        except Exception as e:
            session.rollback()
            st.error(f"Error updating stock in database: {str(e)}")
            return False
        finally:
            session.close()
    
    def migrate_from_json(self, json_file="portfolios.json"):
        """Migrate data from JSON file to database"""
        try:
            if os.path.exists(json_file):
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                for portfolio_name, portfolio_data in data.items():
                    # Convert date strings back to datetime objects
                    if 'created_date' in portfolio_data:
                        portfolio_data['created_date'] = datetime.fromisoformat(portfolio_data['created_date'])
                    
                    for symbol, stock_data in portfolio_data.get('stocks', {}).items():
                        if 'last_updated' in stock_data:
                            # Remove last_updated from stock_data since it's handled by database
                            del stock_data['last_updated']
                    
                    self.save_portfolio(portfolio_name, portfolio_data)
                
                # Backup and remove the JSON file
                os.rename(json_file, f"{json_file}.backup")
                st.success("Successfully migrated data from JSON to database!")
                return True
            
            return False
            
        except Exception as e:
            st.error(f"Error migrating from JSON: {str(e)}")
            return False