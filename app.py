from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from portfolio_manager import PortfolioManager
from stock_data import StockDataManager
from charts import ChartManager

# Configure page
st.set_page_config(
    page_title="Stock Portfolio Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize managers
@st.cache_resource
def get_managers():
    portfolio_manager = PortfolioManager()
    stock_data_manager = StockDataManager()
    chart_manager = ChartManager()
    return portfolio_manager, stock_data_manager, chart_manager

portfolio_manager, stock_data_manager, chart_manager = get_managers()

# Initialize session state
if 'portfolios' not in st.session_state:
    st.session_state.portfolios = {}
if 'current_portfolio' not in st.session_state:
    st.session_state.current_portfolio = None
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

def main():
    st.title("📈 Stock Portfolio Dashboard")
    
    # Show database connection status
    if hasattr(portfolio_manager, 'use_supabase') and portfolio_manager.use_supabase:
        st.success("🟢 Connected to Supabase Database")
    else:
        with st.expander("💡 Upgrade to Cloud Database (Optional)", expanded=False):
            st.markdown("""
            **Currently using local file storage.** 
            
            For better reliability and cloud storage, you can connect to Supabase (free):
            
            1. Create account at [supabase.com](https://supabase.com)
            2. Create a new project  
            3. Copy your database URL from Settings → Database
            4. Add it as `SUPABASE_URL` in Replit Secrets
            5. Restart the app
            
            **Benefits:** 500MB free storage, automatic backups, works forever
            """)
    
    # Sidebar for portfolio management
    with st.sidebar:
        st.header("Portfolio Management")
        
        # Create new portfolio
        st.subheader("Create New Portfolio")
        new_portfolio_name = st.text_input("Portfolio Name", key="new_portfolio")
        if st.button("Create Portfolio") and new_portfolio_name:
            if new_portfolio_name not in st.session_state.portfolios:
                st.session_state.portfolios[new_portfolio_name] = {
                    'stocks': {},
                    'created_date': datetime.now()
                }
                st.success(f"Portfolio '{new_portfolio_name}' created!")
                st.rerun()
            else:
                st.error("Portfolio name already exists!")
        
        # Select portfolio
        if st.session_state.portfolios:
            st.subheader("Select Portfolio")
            portfolio_names = list(st.session_state.portfolios.keys())
            selected_portfolio = st.selectbox(
                "Choose Portfolio",
                portfolio_names,
                index=0 if st.session_state.current_portfolio is None else 
                      portfolio_names.index(st.session_state.current_portfolio) if st.session_state.current_portfolio in portfolio_names else 0
            )
            st.session_state.current_portfolio = selected_portfolio
            
            # Delete portfolio
            if st.button("Delete Selected Portfolio", type="secondary"):
                if len(st.session_state.portfolios) > 1:
                    del st.session_state.portfolios[selected_portfolio]
                    st.session_state.current_portfolio = list(st.session_state.portfolios.keys())[0]
                    st.success(f"Portfolio '{selected_portfolio}' deleted!")
                    st.rerun()
                else:
                    st.error("Cannot delete the last portfolio!")
        
        # Auto-refresh toggle
        st.subheader("Settings")
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
        if st.button("Refresh Now"):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
        
        # Show last refresh time
        st.caption(f"Last refresh: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
    
    # Main content area
    if not st.session_state.portfolios:
        st.info("Create your first portfolio to get started!")
        return
    
    current_portfolio = st.session_state.current_portfolio
    if current_portfolio is None:
        return
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Portfolio Overview", "📈 Individual Stocks", "➕ Add Stocks", "⚙️ Manage Stocks"])
    
    with tab1:
        show_portfolio_overview(current_portfolio)
    
    with tab2:
        show_individual_stocks(current_portfolio)
    
    with tab3:
        add_stocks_interface(current_portfolio)
    
    with tab4:
        manage_stocks_interface(current_portfolio)
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(30)
        st.session_state.last_refresh = datetime.now()
        st.rerun()

def show_portfolio_overview(portfolio_name):
    st.header(f"Portfolio: {portfolio_name}")
    
    portfolio = st.session_state.portfolios[portfolio_name]
    stocks = portfolio['stocks']
    
    if not stocks:
        st.info("No stocks in this portfolio. Add some stocks to see your portfolio performance!")
        return
    
    # Get current prices for all stocks
    with st.spinner("Loading portfolio data..."):
        portfolio_data = []
        total_value = 0
        total_cost = 0
        
        for symbol, stock_info in stocks.items():
            try:
                current_price = stock_data_manager.get_current_price(symbol)
                if current_price is not None:
                    shares = stock_info['shares']
                    avg_price = stock_info['avg_price']
                    current_value = current_price * shares
                    cost_basis = avg_price * shares
                    gain_loss = current_value - cost_basis
                    gain_loss_pct = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
                    
                    portfolio_data.append({
                        'Symbol': symbol,
                        'Shares': shares,
                        'Avg Price': f"${avg_price:.2f}",
                        'Current Price': f"${current_price:.2f}",
                        'Current Value': f"${current_value:.2f}",
                        'Cost Basis': f"${cost_basis:.2f}",
                        'Gain/Loss': f"${gain_loss:.2f}",
                        'Gain/Loss %': f"{gain_loss_pct:.2f}%",
                        'gain_loss_raw': gain_loss,
                        'current_value_raw': current_value
                    })
                    
                    total_value += current_value
                    total_cost += cost_basis
            except Exception as e:
                st.error(f"Error fetching data for {symbol}: {str(e)}")
    
    if portfolio_data:
        # Portfolio summary metrics
        total_gain_loss = total_value - total_cost
        total_gain_loss_pct = (total_gain_loss / total_cost) * 100 if total_cost > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Value", f"${total_value:.2f}")
        with col2:
            st.metric("Total Cost", f"${total_cost:.2f}")
        with col3:
            st.metric("Total Gain/Loss", f"${total_gain_loss:.2f}", 
                     delta=f"{total_gain_loss_pct:.2f}%")
        with col4:
            st.metric("Number of Stocks", len(portfolio_data))
        
        # Portfolio composition chart
        st.subheader("Portfolio Composition")
        fig_pie = chart_manager.create_portfolio_pie_chart(portfolio_data)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Portfolio performance table
        st.subheader("Holdings Details")
        df = pd.DataFrame(portfolio_data)
        
        # Color-code the gain/loss columns
        def style_gain_loss(val):
            if isinstance(val, str) and ('$' in val or '%' in val):
                number = float(val.replace('$', '').replace('%', ''))
                if number > 0:
                    return 'color: green'
                elif number < 0:
                    return 'color: red'
            return ''
        
        styled_df = df.drop(['gain_loss_raw', 'current_value_raw'], axis=1).style.map(
            style_gain_loss, subset=['Gain/Loss', 'Gain/Loss %']
        )
        st.dataframe(styled_df, use_container_width=True)
        
        # Portfolio performance over time
        st.subheader("Portfolio Performance Over Time")
        symbols = list(stocks.keys())
        if symbols:
            try:
                fig_portfolio = chart_manager.create_portfolio_performance_chart(symbols, stocks)
                st.plotly_chart(fig_portfolio, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating portfolio performance chart: {str(e)}")

def show_individual_stocks(portfolio_name):
    st.header("Individual Stock Analysis")
    
    portfolio = st.session_state.portfolios[portfolio_name]
    stocks = portfolio['stocks']
    
    if not stocks:
        st.info("No stocks in this portfolio. Add some stocks to see individual analysis!")
        return
    
    # Stock selector
    selected_stock = st.selectbox("Select Stock", list(stocks.keys()))
    
    if selected_stock:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Stock info
            stock_info = stocks[selected_stock]
            try:
                current_price = stock_data_manager.get_current_price(selected_stock)
                if current_price is not None:
                    shares = stock_info['shares']
                    avg_price = stock_info['avg_price']
                    current_value = current_price * shares
                    cost_basis = avg_price * shares
                    gain_loss = current_value - cost_basis
                    gain_loss_pct = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
                    
                    st.subheader(f"{selected_stock} Details")
                    st.metric("Current Price", f"${current_price:.2f}")
                    st.metric("Shares Owned", f"{shares:.2f}")
                    st.metric("Average Price", f"${avg_price:.2f}")
                    st.metric("Current Value", f"${current_value:.2f}")
                    st.metric("Gain/Loss", f"${gain_loss:.2f}", 
                             delta=f"{gain_loss_pct:.2f}%")
                else:
                    st.error(f"Unable to fetch current price for {selected_stock}")
            except Exception as e:
                st.error(f"Error fetching data for {selected_stock}: {str(e)}")
        
        with col2:
            # Time period selector
            period = st.selectbox("Time Period", 
                                ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
                                index=3)
        
        # Stock chart
        try:
            fig_stock = chart_manager.create_stock_chart(selected_stock, period)
            st.plotly_chart(fig_stock, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating chart for {selected_stock}: {str(e)}")

def add_stocks_interface(portfolio_name):
    st.header("Add Stocks to Portfolio")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Stock search and add
        st.subheader("Search and Add Stock")
        stock_symbol = st.text_input("Stock Symbol (e.g., AAPL, MSFT)", key="add_stock_symbol").upper()
        shares = st.number_input("Number of Shares", min_value=0.05, step=0.05, value=0.05, key="add_shares")
        
        # Get current market price for default average price
        default_price = 0.01
        if stock_symbol:
            try:
                current_price = stock_data_manager.get_current_price(stock_symbol)
                if current_price is not None:
                    default_price = current_price
            except:
                pass
        
        avg_price = st.number_input("Average Purchase Price ($)", min_value=0.01, step=0.01, value=default_price, key="add_avg_price")
        
        if st.button("Add Stock") and stock_symbol and shares > 0 and avg_price > 0:
            # Validate stock symbol
            try:
                current_price = stock_data_manager.get_current_price(stock_symbol)
                if current_price is not None:
                    portfolio = st.session_state.portfolios[portfolio_name]
                    
                    if stock_symbol in portfolio['stocks']:
                        # Update existing position
                        existing = portfolio['stocks'][stock_symbol]
                        total_shares = existing['shares'] + shares
                        total_cost = (existing['shares'] * existing['avg_price']) + (shares * avg_price)
                        new_avg_price = total_cost / total_shares
                        
                        portfolio['stocks'][stock_symbol] = {
                            'shares': total_shares,
                            'avg_price': new_avg_price,
                            'last_updated': datetime.now()
                        }
                        st.success(f"Updated {stock_symbol} position!")
                    else:
                        # Add new position
                        portfolio['stocks'][stock_symbol] = {
                            'shares': shares,
                            'avg_price': avg_price,
                            'last_updated': datetime.now()
                        }
                        st.success(f"Added {stock_symbol} to portfolio!")
                    
                    st.rerun()
                else:
                    st.error(f"Invalid stock symbol: {stock_symbol}")
            except Exception as e:
                st.error(f"Error adding stock: {str(e)}")
    
    with col2:
        # Stock preview
        if stock_symbol:
            st.subheader(f"Preview: {stock_symbol}")
            try:
                current_price = stock_data_manager.get_current_price(stock_symbol)
                if current_price is not None:
                    st.metric("Current Price", f"${current_price:.2f}")
                    if shares > 0:
                        total_value = current_price * shares
                        st.metric("Current Value", f"${total_value:.2f}")
                    if avg_price > 0 and shares > 0:
                        cost_basis = avg_price * shares
                        gain_loss = (current_price - avg_price) * shares
                        gain_loss_pct = ((current_price - avg_price) / avg_price) * 100
                        st.metric("Estimated Gain/Loss", f"${gain_loss:.2f}", 
                                 delta=f"{gain_loss_pct:.2f}%")
                else:
                    st.warning("Enter a valid stock symbol to see preview")
            except Exception as e:
                st.error(f"Error fetching preview: {str(e)}")

def manage_stocks_interface(portfolio_name):
    st.header("Manage Stocks")
    
    portfolio = st.session_state.portfolios[portfolio_name]
    stocks = portfolio['stocks']
    
    if not stocks:
        st.info("No stocks in this portfolio to manage.")
        return
    
    # Stock management table
    st.subheader("Current Holdings")
    
    for symbol, stock_info in stocks.items():
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        
        with col1:
            st.write(f"**{symbol}**")
        
        with col2:
            # Edit shares
            new_shares = st.number_input(
                f"Shares", 
                value=stock_info['shares'], 
                min_value=0.05, 
                step=0.05, 
                key=f"shares_{symbol}"
            )
        
        with col3:
            # Edit average price
            new_avg_price = st.number_input(
                f"Avg Price", 
                value=stock_info['avg_price'], 
                min_value=0.01, 
                step=0.01, 
                key=f"avg_price_{symbol}"
            )
        
        with col4:
            # Update button
            if st.button(f"Update", key=f"update_{symbol}"):
                portfolio['stocks'][symbol] = {
                    'shares': new_shares,
                    'avg_price': new_avg_price,
                    'last_updated': datetime.now()
                }
                st.success(f"Updated {symbol}!")
                st.rerun()
        
        with col5:
            # Remove button
            if st.button(f"Remove", key=f"remove_{symbol}", type="secondary"):
                del portfolio['stocks'][symbol]
                st.success(f"Removed {symbol}!")
                st.rerun()
        
        st.divider()

if __name__ == "__main__":
    main()
