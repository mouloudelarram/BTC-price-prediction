"""
Bitcoin Price Factor Analysis Tool
Fetches historical data for BTC and various factors, generates visualizations and PDF reports
"""

import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

import pandas as pd
import numpy as np
import yfinance as yf
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('btc_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Styling
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10


class FactorExtractor:
    """Extract factor names from factors.txt file"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.factors = []
    
    def extract_factors(self) -> List[str]:
        """Extract factor names from markdown file"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pattern to match bold factor names: **Factor Name**
            pattern = r'\*\*([^*]+)\*\*[^*]*?(?:\n\s*-|:)'
            matches = re.findall(pattern, content)
            
            # Clean and filter factors
            factors = []
            seen = set()
            
            for match in matches:
                # Clean up the factor name
                factor_name = match.strip()
                
                # Skip common headers and duplicates
                if (len(factor_name) > 3 and 
                    factor_name not in seen and
                    not any(skip in factor_name for skip in ['FINANCIAL', 'MARKETS', 'INDICATORS', 'FACTORS'])):
                    factors.append(factor_name)
                    seen.add(factor_name)
            
            # Add primary factors manually for reliability
            primary_factors = [
                'S&P 500',
                'NASDAQ 100',
                'Dow Jones Industrial Average',
                'Nikkei 225',
                '10-Year Treasury Yield',
                '2-Year Treasury Yield',
                'DXY (US Dollar Index)',
                'EUR/USD',
                'Gold (XAU/USD)',
                'Crude Oil (WTI)',
                'Bitcoin Halving Events',
                'Federal Funds Rate',
                'CPI (Consumer Price Index)',
                'Unemployment Rate',
                'VIX (CBOE Volatility Index)',
                'Ethereum (ETH)',
                'Stablecoin Supply',
                'Mining Hash Rate',
                'Exchange Flows',
                'Bitcoin Fear & Greed Index'
            ]
            
            # Merge and deduplicate
            all_factors = list(set(factors + primary_factors))
            self.factors = sorted(all_factors)
            
            logger.info(f"Extracted {len(self.factors)} factors from {self.file_path}")
            return self.factors
        
        except Exception as e:
            logger.error(f"Error extracting factors: {e}")
            # Return default factors if extraction fails
            return self._get_default_factors()
    
    @staticmethod
    def _get_default_factors() -> List[str]:
        """Return default factors if parsing fails"""
        return [
            'S&P 500',
            'NASDAQ 100',
            'Dow Jones Industrial Average',
            'Gold (XAU/USD)',
            'Crude Oil (WTI)',
            '10-Year Treasury Yield',
            'DXY (US Dollar Index)',
            'Ethereum (ETH)',
            'VIX (CBOE Volatility Index)',
            'Federal Funds Rate',
            'CPI (Consumer Price Index)',
        ]


class DataFetcher:
    """Fetch historical data for BTC and various factors"""
    
    # Mapping of factor names to yfinance tickers
    TICKER_MAPPING = {
        'S&P 500': '^GSPC',
        'NASDAQ 100': '^NDX',
        'Dow Jones Industrial Average': '^DJI',
        'Nikkei 225': '^N225',
        'Hang Seng': '^HSI',
        'STOXX Europe 600': '^STOXX',
        '10-Year Treasury Yield': '^TNX',
        '2-Year Treasury Yield': '^IRX',
        'DXY (US Dollar Index)': 'DXY=F',
        'EUR/USD': 'EURUSD=X',
        'GBP/USD': 'GBPUSD=X',
        'USD/JPY': 'USDJPY=X',
        'Gold (XAU/USD)': 'GC=F',
        'Crude Oil (WTI)': 'CL=F',
        'Copper': 'HG=F',
        'Ethereum (ETH)': 'ETH-USD',
        'Binance Coin (BNB)': 'BNB-USD',
        'Ripple (XRP)': 'XRP-USD',
        'VIX (CBOE Volatility Index)': '^VIX',
        'Bitcoin': 'BTC-USD',
    }
    
    def __init__(self, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """
        Initialize DataFetcher
        
        Args:
            start_date: Start date (YYYY-MM-DD), defaults to 2 years ago
            end_date: End date (YYYY-MM-DD), defaults to today
        """
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        self.start_date = start_date or (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        self.data_cache = {}
    
    def fetch_factor_data(self, factor_name: str) -> Optional[pd.DataFrame]:
        """
        Fetch historical data for a given factor
        
        Args:
            factor_name: Name of the factor
            
        Returns:
            DataFrame with Date and Close price, or None if fetch fails
        """
        try:
            ticker = self.TICKER_MAPPING.get(factor_name)
            
            if not ticker:
                logger.warning(f"No ticker mapping for {factor_name}, skipping...")
                return None
            
            logger.info(f"Fetching data for {factor_name} ({ticker})...")
            
            data = yf.download(
                ticker,
                start=self.start_date,
                end=self.end_date,
                progress=False
            )
            
            if data.empty:
                logger.warning(f"No data retrieved for {factor_name}")
                return None
            
            logger.info(f"Raw data type: {type(data)}, columns: {data.columns.tolist() if hasattr(data, 'columns') else 'Series'}")
            
            # Convert to DataFrame if it's a Series
            if isinstance(data, pd.Series):
                data = data.to_frame()
            
            # Handle MultiIndex columns from yfinance
            if isinstance(data.columns, pd.MultiIndex):
                # Flatten column names
                data.columns = data.columns.get_level_values(0)
            
            # Reset index to make Date a column
            data = data.reset_index()
            logger.info(f"After reset_index - columns: {data.columns.tolist()}")
            
            # Extract Close price column
            if 'Adj Close' in data.columns:
                result = data[['Date', 'Adj Close']].copy()
                result.rename(columns={'Adj Close': 'Close'}, inplace=True)
            elif 'Close' in data.columns:
                result = data[['Date', 'Close']].copy()
            else:
                logger.error(f"No Close/Adj Close column for {factor_name}. Available columns: {data.columns.tolist()}")
                return None
            
            result['Date'] = pd.to_datetime(result['Date'])
            result = result.sort_values('Date')
            
            # Remove duplicates and NaN values
            result = result.drop_duplicates(subset=['Date']).dropna()
            
            logger.info(f"Successfully fetched {len(result)} records for {factor_name}")
            self.data_cache[factor_name] = result
            return result
        
        except Exception as e:
            logger.error(f"Error fetching data for {factor_name}: {e}", exc_info=True)
            return None
    
    def fetch_btc_data(self) -> pd.DataFrame:
        """Fetch Bitcoin price data"""
        return self.fetch_factor_data('Bitcoin')


class DataProcessor:
    """Process and align data from multiple sources"""
    
    @staticmethod
    def align_data(btc_data: pd.DataFrame, factor_data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Align BTC and factor data on common dates
        
        Args:
            btc_data: Bitcoin price data
            factor_data: Factor data
            
        Returns:
            Tuple of aligned DataFrames
        """
        try:
            # Merge on Date
            merged = pd.merge(
                btc_data,
                factor_data,
                on='Date',
                how='inner',
                suffixes=('_BTC', '_Factor')
            )
            
            if merged.empty:
                return None, None
            
            # Forward fill missing values (max 5 days)
            merged = merged.ffill(limit=5)
            merged = merged.dropna()
            
            return merged, merged
        
        except Exception as e:
            logger.error(f"Error aligning data: {e}")
            return None, None
    
    @staticmethod
    def calculate_statistics(btc_data: pd.Series, factor_data: pd.Series) -> Dict:
        """
        Calculate correlation and basic statistics
        
        Args:
            btc_data: BTC price series
            factor_data: Factor price series
            
        Returns:
            Dictionary of statistics
        """
        try:
            # Calculate returns
            btc_returns = btc_data.pct_change().dropna()
            factor_returns = factor_data.pct_change().dropna()
            
            # Align returns
            common_idx = btc_returns.index.intersection(factor_returns.index)
            btc_ret_aligned = btc_returns[common_idx]
            factor_ret_aligned = factor_returns[common_idx]
            
            # Pearson correlation
            correlation, p_value = stats.pearsonr(btc_ret_aligned, factor_ret_aligned)
            
            # Spearman correlation
            spearman_corr, spearman_p = stats.spearmanr(btc_ret_aligned, factor_ret_aligned)
            
            stats_dict = {
                'correlation': correlation,
                'p_value': p_value,
                'spearman_correlation': spearman_corr,
                'spearman_p': spearman_p,
                'btc_mean': btc_data.mean(),
                'btc_std': btc_data.std(),
                'btc_min': btc_data.min(),
                'btc_max': btc_data.max(),
                'factor_mean': factor_data.mean(),
                'factor_std': factor_data.std(),
                'factor_min': factor_data.min(),
                'factor_max': factor_data.max(),
                'data_points': len(btc_ret_aligned)
            }
            
            return stats_dict
        
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}


class ReportGenerator:
    """Generate PDF reports with visualizations"""
    
    def __init__(self, output_dir: str = 'BTC_Factor_Reports'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.summary_data = []
    
    def create_visualization(
        self,
        btc_data: pd.DataFrame,
        factor_data: pd.DataFrame,
        factor_name: str,
        stats: Dict
    ) -> str:
        """
        Create a matplotlib figure comparing BTC and factor
        
        Args:
            btc_data: BTC price data
            factor_data: Factor price data
            factor_name: Name of the factor
            stats: Statistics dictionary
            
        Returns:
            Path to saved figure
        """
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'Bitcoin vs {factor_name} Analysis', fontsize=16, fontweight='bold')
            
            # Normalize data for comparison
            btc_normalized = (btc_data['Close_BTC'] - btc_data['Close_BTC'].min()) / (btc_data['Close_BTC'].max() - btc_data['Close_BTC'].min())
            factor_normalized = (btc_data['Close_Factor'] - btc_data['Close_Factor'].min()) / (btc_data['Close_Factor'].max() - btc_data['Close_Factor'].min())
            
            # Plot 1: Normalized Price Evolution
            ax1 = axes[0, 0]
            ax1.plot(btc_data['Date'], btc_normalized, label='BTC (Normalized)', linewidth=2, alpha=0.8)
            ax1.plot(btc_data['Date'], factor_normalized, label=f'{factor_name} (Normalized)', linewidth=2, alpha=0.8)
            ax1.set_title('Normalized Price Evolution', fontweight='bold')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Normalized Price')
            ax1.legend(loc='best')
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            
            # Plot 2: Scatter plot with correlation
            ax2 = axes[0, 1]
            ax2.scatter(btc_data['Close_Factor'], btc_data['Close_BTC'], alpha=0.5, s=20)
            
            # Add trend line
            z = np.polyfit(btc_data['Close_Factor'], btc_data['Close_BTC'], 1)
            p = np.poly1d(z)
            x_trend = np.linspace(btc_data['Close_Factor'].min(), btc_data['Close_Factor'].max(), 100)
            ax2.plot(x_trend, p(x_trend), "r-", linewidth=2, label='Trend')
            
            corr = stats.get('correlation', 0)
            ax2.set_title(f'BTC vs {factor_name}\nCorrelation: {corr:.3f}', fontweight='bold')
            ax2.set_xlabel(f'{factor_name}')
            ax2.set_ylabel('BTC Price (USD)')
            ax2.legend(loc='best')
            ax2.grid(True, alpha=0.3)
            
            # Plot 3: Rolling Correlation
            ax3 = axes[1, 0]
            rolling_corr = btc_data['Close_BTC'].rolling(window=30).corr(btc_data['Close_Factor'])
            ax3.plot(btc_data['Date'], rolling_corr, linewidth=2, color='green', alpha=0.8)
            ax3.axhline(y=0, color='red', linestyle='--', alpha=0.5)
            ax3.fill_between(btc_data['Date'], rolling_corr, 0, where=(rolling_corr >= 0), alpha=0.3, color='green', label='Positive')
            ax3.fill_between(btc_data['Date'], rolling_corr, 0, where=(rolling_corr < 0), alpha=0.3, color='red', label='Negative')
            ax3.set_title('30-Day Rolling Correlation', fontweight='bold')
            ax3.set_xlabel('Date')
            ax3.set_ylabel('Correlation Coefficient')
            ax3.legend(loc='best')
            ax3.grid(True, alpha=0.3)
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
            
            # Plot 4: Statistics Box
            ax4 = axes[1, 1]
            ax4.axis('off')
            
            stats_text = f"""
STATISTICAL SUMMARY
{'='*40}

Correlation Statistics:
  Pearson Correlation: {stats.get('correlation', np.nan):.4f}
  P-value: {stats.get('p_value', np.nan):.4e}
  Spearman Correlation: {stats.get('spearman_correlation', np.nan):.4f}
  
Data Points: {stats.get('data_points', 'N/A')}

Bitcoin Statistics:
  Mean: ${stats.get('btc_mean', np.nan):,.2f}
  Std Dev: ${stats.get('btc_std', np.nan):,.2f}
  Min: ${stats.get('btc_min', np.nan):,.2f}
  Max: ${stats.get('btc_max', np.nan):,.2f}

{factor_name} Statistics:
  Mean: {stats.get('factor_mean', np.nan):,.2f}
  Std Dev: {stats.get('factor_std', np.nan):,.2f}
  Min: {stats.get('factor_min', np.nan):,.2f}
  Max: {stats.get('factor_max', np.nan):,.2f}
"""
            
            ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes, fontsize=10,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            plt.tight_layout()
            
            # Save figure
            safe_name = re.sub(r'[^a-zA-Z0-9\-_]', '_', factor_name)
            fig_path = self.output_dir / f'chart_{safe_name}.png'
            plt.savefig(fig_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Saved visualization to {fig_path}")
            return str(fig_path)
        
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return None
    
    def create_pdf_report(
        self,
        factor_name: str,
        chart_path: str,
        stats: Dict,
        btc_data: pd.DataFrame
    ) -> str:
        """
        Create a professional PDF report
        
        Args:
            factor_name: Name of the factor
            chart_path: Path to the chart image
            stats: Statistics dictionary
            btc_data: Data with date range info
            
        Returns:
            Path to the PDF report
        """
        try:
            safe_name = re.sub(r'[^a-zA-Z0-9\-_]', '_', factor_name)
            pdf_path = self.output_dir / f'BTC_vs_{safe_name}.pdf'
            
            doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f77b4'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            elements.append(Paragraph(f'Bitcoin vs {factor_name}', title_style))
            elements.append(Spacer(1, 0.3 * inch))
            
            # Report metadata
            date_range = f"{btc_data['Date'].min().strftime('%Y-%m-%d')} to {btc_data['Date'].max().strftime('%Y-%m-%d')}"
            elements.append(Paragraph(f'<b>Analysis Period:</b> {date_range}', styles['Normal']))
            elements.append(Paragraph(f'<b>Report Generated:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', styles['Normal']))
            elements.append(Spacer(1, 0.3 * inch))
            
            # Chart
            if os.path.exists(chart_path):
                elements.append(Paragraph('<b>Analysis Charts</b>', styles['Heading2']))
                img = Image(chart_path, width=7*inch, height=5.25*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.3 * inch))
            
            elements.append(PageBreak())
            
            # Statistics Section
            elements.append(Paragraph('<b>Statistical Summary</b>', styles['Heading2']))
            
            stats_data = [
                ['Metric', 'Value'],
                ['Pearson Correlation', f"{stats.get('correlation', np.nan):.4f}"],
                ['P-value', f"{stats.get('p_value', np.nan):.4e}"],
                ['Spearman Correlation', f"{stats.get('spearman_correlation', np.nan):.4f}"],
                ['Data Points', f"{stats.get('data_points', 'N/A')}"],
                ['', ''],
                ['BTC Mean Price', f"${stats.get('btc_mean', np.nan):,.2f}"],
                ['BTC Std Dev', f"${stats.get('btc_std', np.nan):,.2f}"],
                ['BTC Min Price', f"${stats.get('btc_min', np.nan):,.2f}"],
                ['BTC Max Price', f"${stats.get('btc_max', np.nan):,.2f}"],
                ['', ''],
                [f'{factor_name} Mean', f"{stats.get('factor_mean', np.nan):,.2f}"],
                [f'{factor_name} Std Dev', f"{stats.get('factor_std', np.nan):,.2f}"],
                [f'{factor_name} Min', f"{stats.get('factor_min', np.nan):,.2f}"],
                [f'{factor_name} Max', f"{stats.get('factor_max', np.nan):,.2f}"],
            ]
            
            stats_table = Table(stats_data, colWidths=[3.5*inch, 2.5*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            elements.append(stats_table)
            elements.append(Spacer(1, 0.3 * inch))
            
            # Interpretation
            elements.append(Paragraph('<b>Interpretation</b>', styles['Heading2']))
            corr = stats.get('correlation', 0)
            
            if corr > 0.5:
                interpretation = f"Strong positive correlation ({corr:.3f}): {factor_name} and Bitcoin tend to move in the same direction."
            elif corr > 0.3:
                interpretation = f"Moderate positive correlation ({corr:.3f}): Some tendency for {factor_name} and Bitcoin to move together."
            elif corr < -0.5:
                interpretation = f"Strong negative correlation ({corr:.3f}): {factor_name} and Bitcoin tend to move in opposite directions."
            elif corr < -0.3:
                interpretation = f"Moderate negative correlation ({corr:.3f}): Some tendency for inverse movement."
            else:
                interpretation = f"Weak correlation ({corr:.3f}): Limited linear relationship between {factor_name} and Bitcoin."
            
            elements.append(Paragraph(interpretation, styles['Normal']))
            
            # Build PDF
            doc.build(elements)
            logger.info(f"Created PDF report: {pdf_path}")
            
            # Store summary data
            self.summary_data.append({
                'Factor': factor_name,
                'Correlation': stats.get('correlation', np.nan),
                'P-Value': stats.get('p_value', np.nan),
                'Data Points': stats.get('data_points', 0),
                'PDF': str(pdf_path)
            })
            
            return str(pdf_path)
        
        except Exception as e:
            logger.error(f"Error creating PDF report: {e}")
            return None
    
    def create_summary_report(self) -> str:
        """Create a summary CSV file with all factor correlations"""
        try:
            if not self.summary_data:
                logger.warning("No summary data to save")
                return None
            
            summary_df = pd.DataFrame(self.summary_data)
            summary_df = summary_df.sort_values('Correlation', ascending=False)
            
            csv_path = self.output_dir / 'BTC_Correlation_Summary.csv'
            summary_df.to_csv(csv_path, index=False)
            
            logger.info(f"Created summary report: {csv_path}")
            
            # Also create a summary PDF with rankings
            self._create_summary_pdf(summary_df)
            
            return str(csv_path)
        
        except Exception as e:
            logger.error(f"Error creating summary report: {e}")
            return None
    
    def _create_summary_pdf(self, summary_df: pd.DataFrame) -> str:
        """Create a PDF summary with correlation rankings"""
        try:
            pdf_path = self.output_dir / 'BTC_Correlation_Summary.pdf'
            doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#1f77b4'),
                spaceAfter=20,
                alignment=TA_CENTER
            )
            elements.append(Paragraph('Bitcoin Factor Correlation Summary', title_style))
            elements.append(Spacer(1, 0.2 * inch))
            
            # Summary stats
            elements.append(Paragraph(f'<b>Total Factors Analyzed:</b> {len(summary_df)}', styles['Normal']))
            elements.append(Paragraph(f'<b>Report Generated:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', styles['Normal']))
            elements.append(Spacer(1, 0.3 * inch))
            
            # Table
            table_data = [['Rank', 'Factor', 'Correlation', 'P-Value', 'Data Points']]
            
            for idx, row in summary_df.iterrows():
                table_data.append([
                    str(idx + 1),
                    row['Factor'][:30],
                    f"{row['Correlation']:.4f}",
                    f"{row['P-Value']:.2e}",
                    str(row['Data Points'])
                ])
            
            table = Table(table_data, colWidths=[0.8*inch, 2.5*inch, 1.2*inch, 1.2*inch, 1.3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            elements.append(table)
            doc.build(elements)
            
            logger.info(f"Created summary PDF: {pdf_path}")
            return str(pdf_path)
        
        except Exception as e:
            logger.error(f"Error creating summary PDF: {e}")
            return None


class BTCFactorAnalyzer:
    """Main analysis orchestrator"""
    
    def __init__(
        self,
        factors_file: str = 'factors.txt',
        output_dir: str = 'BTC_Factor_Reports',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ):
        self.factors_file = factors_file
        self.output_dir = output_dir
        self.start_date = start_date
        self.end_date = end_date
        
        self.extractor = FactorExtractor(factors_file)
        self.fetcher = DataFetcher(start_date, end_date)
        self.processor = DataProcessor()
        self.report_gen = ReportGenerator(output_dir)
    
    def run_analysis(self, max_factors: Optional[int] = None) -> Dict:
        """
        Run complete analysis pipeline
        
        Args:
            max_factors: Maximum number of factors to analyze (None = all)
            
        Returns:
            Dictionary with analysis results
        """
        logger.info("="*60)
        logger.info("Starting Bitcoin Factor Analysis")
        logger.info("="*60)
        
        # Extract factors
        factors = self.extractor.extract_factors()
        if max_factors:
            factors = factors[:max_factors]
        
        logger.info(f"Analyzing {len(factors)} factors")
        
        # Fetch BTC data
        logger.info("Fetching Bitcoin data...")
        btc_data = self.fetcher.fetch_btc_data()
        
        if btc_data is None or btc_data.empty:
            logger.error("Failed to fetch Bitcoin data")
            return {'success': False, 'error': 'Failed to fetch Bitcoin data'}
        
        logger.info(f"BTC data: {len(btc_data)} records from {btc_data['Date'].min()} to {btc_data['Date'].max()}")
        
        # Analyze each factor
        results = {'factors_analyzed': [], 'factors_failed': []}
        
        for i, factor in enumerate(factors, 1):
            logger.info(f"\n[{i}/{len(factors)}] Analyzing {factor}...")
            
            try:
                # Fetch factor data
                factor_data = self.fetcher.fetch_factor_data(factor)
                if factor_data is None or factor_data.empty:
                    logger.warning(f"Skipping {factor} - no data retrieved")
                    results['factors_failed'].append(factor)
                    continue
                
                # Align data
                aligned_data, _ = self.processor.align_data(btc_data, factor_data)
                if aligned_data is None or aligned_data.empty:
                    logger.warning(f"Skipping {factor} - no aligned data")
                    results['factors_failed'].append(factor)
                    continue
                
                # Calculate statistics
                stats = self.processor.calculate_statistics(
                    aligned_data['Close_BTC'],
                    aligned_data['Close_Factor']
                )
                
                if not stats:
                    logger.warning(f"Skipping {factor} - statistics calculation failed")
                    results['factors_failed'].append(factor)
                    continue
                
                # Create visualization
                chart_path = self.report_gen.create_visualization(
                    aligned_data,
                    factor_data,
                    factor,
                    stats
                )
                
                # Create PDF report
                pdf_path = self.report_gen.create_pdf_report(
                    factor,
                    chart_path,
                    stats,
                    aligned_data
                )
                
                results['factors_analyzed'].append({
                    'factor': factor,
                    'correlation': stats.get('correlation', np.nan),
                    'p_value': stats.get('p_value', np.nan),
                    'data_points': stats.get('data_points', 0),
                    'pdf': pdf_path
                })
                
                logger.info(f"[OK] {factor}: Correlation = {stats.get('correlation', np.nan):.4f}")
            
            except Exception as e:
                logger.error(f"Error analyzing {factor}: {e}")
                results['factors_failed'].append(factor)
        
        # Create summary report
        logger.info("\nCreating summary reports...")
        summary_csv = self.report_gen.create_summary_report()
        results['summary_csv'] = summary_csv
        results['output_dir'] = str(self.report_gen.output_dir)
        
        logger.info("="*60)
        logger.info(f"Analysis Complete!")
        logger.info(f"  Successfully analyzed: {len(results['factors_analyzed'])} factors")
        logger.info(f"  Failed: {len(results['factors_failed'])} factors")
        logger.info(f"  Output directory: {self.report_gen.output_dir}")
        logger.info("="*60)
        
        return results


def main():
    """Main entry point"""
    
    # Configuration
    factors_file = Path(__file__).parent / 'factors.txt'
    output_dir = Path(__file__).parent / 'BTC_Factor_Reports'
    
    # Run analysis
    analyzer = BTCFactorAnalyzer(
        factors_file=str(factors_file),
        output_dir=str(output_dir),
        start_date='2022-01-01',  # Last 2+ years of data
        end_date=None  # Today
    )
    
    results = analyzer.run_analysis(max_factors=15)  # Analyze top 15 factors for demo
    
    # Print results summary
    if results.get('success', True):
        print("\n" + "="*60)
        print("ANALYSIS RESULTS SUMMARY")
        print("="*60)
        print(f"\nSuccessfully analyzed factors:")
        for item in results.get('factors_analyzed', []):
            print(f"  • {item['factor']:40s} | Correlation: {item['correlation']:7.4f}")
        
        if results.get('factors_failed'):
            print(f"\nFailed to analyze:")
            for factor in results.get('factors_failed', []):
                print(f"  • {factor}")
        
        print(f"\nOutput files saved to: {results.get('output_dir')}")
        print(f"Summary report: {results.get('summary_csv')}")
        print("="*60 + "\n")


if __name__ == '__main__':
    main()
