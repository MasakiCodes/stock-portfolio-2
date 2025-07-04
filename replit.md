# Stock Portfolio Dashboard

## Overview

This is a Streamlit-based stock portfolio management dashboard that allows users to create, manage, and analyze stock portfolios. The application provides real-time stock data visualization, portfolio tracking, and performance analytics using Yahoo Finance data.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Frontend**: Streamlit web interface for user interaction
- **Data Layer**: Yahoo Finance API integration for stock data
- **Database**: Supabase PostgreSQL database with JSON file fallback
- **Visualization**: Plotly charts for stock price and portfolio visualizations
- **Persistence**: Cloud database storage with automatic local fallback
- **Caching**: In-memory caching for performance optimization

## Key Components

### 1. Main Application (app.py)
- **Purpose**: Entry point and main UI controller
- **Key Features**:
  - Streamlit page configuration and layout
  - Session state management for portfolios
  - Manager initialization with caching
  - Portfolio creation and management interface

### 2. Portfolio Manager (portfolio_manager.py)
- **Purpose**: Handles portfolio CRUD operations and persistence
- **Key Features**:
  - Dual storage: Supabase cloud database with JSON file fallback
  - Portfolio creation and management
  - Automatic migration from JSON to Supabase
  - Error handling for both database and file operations

### 3. Supabase Manager (supabase_manager.py)
- **Purpose**: Manages Supabase PostgreSQL database operations
- **Key Features**:
  - SQLAlchemy ORM for database interactions
  - Portfolio and Stock table definitions
  - Automatic table creation and migration
  - Session management and error handling
  - Graceful fallback when not configured

### 4. Stock Data Manager (stock_data.py)
- **Purpose**: Interfaces with Yahoo Finance API for stock data
- **Key Features**:
  - Real-time stock price fetching
  - Historical data retrieval
  - In-memory caching with TTL (5 minutes)
  - Multiple fallback mechanisms for price data
  - Error handling and graceful degradation

### 5. Chart Manager (charts.py)
- **Purpose**: Creates interactive visualizations for stock data
- **Key Features**:
  - Candlestick charts with volume overlays
  - Color-coded positive/negative indicators
  - Plotly integration for interactive charts
  - Customizable chart periods

## Data Flow

1. **User Interaction**: User creates portfolios and adds stocks through Streamlit UI
2. **Data Fetching**: Stock data is retrieved from Yahoo Finance API with caching
3. **Visualization**: Charts are generated using Plotly for interactive display
4. **Persistence**: Portfolio data is saved to JSON files with automatic serialization
5. **State Management**: Streamlit session state maintains application state between interactions

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **yfinance**: Yahoo Finance API wrapper for stock data
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **plotly**: Interactive visualization library

### Data Sources
- **Yahoo Finance**: Primary source for stock prices and historical data
- **Supabase**: Free PostgreSQL cloud database for portfolio persistence
- **JSON Files**: Local fallback storage when Supabase not configured

## Deployment Strategy

The application is designed for local development and can be deployed on:
- **Local Environment**: Direct Streamlit execution
- **Replit**: Cloud-based development environment
- **Streamlit Cloud**: Native Streamlit hosting platform
- **Docker**: Containerized deployment (would require Dockerfile)

### Key Considerations
- Supabase provides free 500MB PostgreSQL database with no expiration
- Automatic fallback to JSON files ensures app always works
- Seamless migration from local files to cloud database
- Caching strategy optimized for development environments

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- July 04, 2025. Initial setup
- July 04, 2025. Added PostgreSQL database integration with SQLAlchemy ORM
- July 04, 2025. Updated share increments to 0.05 and auto-fill market prices
- July 04, 2025. Implemented automatic JSON to database migration
- July 04, 2025. Integrated Supabase free cloud database with JSON fallback
- July 04, 2025. Added dual storage system for maximum reliability