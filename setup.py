from setuptools import setup, find_packages

setup(
    name='finance_backtest',
    version='1.0.0',
    description='Tools for finance backtesting using data from yfinance or investing.com',
    author='tomchiutw',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'yfinance>=0.2.40',
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'matplotlib>=3.7.0',
        'openpyxl>=3.1.0',
        'pyyaml>=6.0',
        'pyarrow>=14.0.0',
        'plotly>=5.18.0',
        'jinja2>=3.1.0',
    ],
    extras_require={
        'dev': ['pytest>=7.4.0'],
    },
)
