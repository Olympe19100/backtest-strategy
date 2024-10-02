import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import quantstats as qs
from datetime import datetime, timedelta

# Configuration de la page Streamlit
st.set_page_config(page_title="Olympe Financial Group - Analyse de Portefeuille", layout="wide")

# Fonction pour télécharger les données
@st.cache_data
def download_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    return data.tz_localize(None)

# Fonction pour calculer les rendements
def calculate_returns(prices):
    return prices.pct_change().dropna()

# Fonction pour calculer la performance du portefeuille
def calculate_portfolio_performance(returns, weights, initial_investment=100000):
    weighted_returns = returns.mul(weights, axis=1).sum(axis=1)
    cumulative_returns = (1 + weighted_returns).cumprod()
    portfolio_value = initial_investment * cumulative_returns
    return portfolio_value

# Définition du portefeuille avec les poids spécifiés
portfolio_weights = {
    'AAPL': 0.0076, 'MSFT': 0.1285, 'GOOG': 0.0168, 'AMZN': 0.0174, 'META': 0.0526,
    'NVDA': 0.1525, 'V': 0.0207, 'MA': 0.0351, 'BRK-B': 0.0053, 'JPM': 0.0147,
    'UNH': 0.2824, 'BLK': 0.0001, 'HD': 0.0215, 'T': 0.0063, 'PFE': 0.0021,
    'MRK': 0.1109, 'PEP': 0.0447, 'JNJ': 0.0172, 'TSLA': 0.0583, 'AXP': 0.0053
}

# Style personnalisé
st.markdown("""
<style>
.big-font {
    font-size:30px !important;
    font-weight: bold;
    color: #1E3A8A;
}
.metric-value {
    font-size: 24px;
    font-weight: bold;
    color: #1E3A8A;
}
.metric-label {
    font-size: 16px;
    color: #4B5563;
}
</style>
""", unsafe_allow_html=True)

# En-tête
st.markdown("<p class='big-font'>Olympe Financial Group - Analyse de Portefeuille</p>", unsafe_allow_html=True)

# Sélection de la période
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Date de début", value=datetime.now() - timedelta(days=5*365))
with col2:
    end_date = st.date_input("Date de fin", value=datetime.now())

if st.button("Analyser le portefeuille"):
    # Télécharger les données
    with st.spinner("Téléchargement des données..."):
        portfolio_data = download_data(list(portfolio_weights.keys()), start_date, end_date)
        benchmark_data = download_data('^FCHI', start_date, end_date)  # CAC 40

    # Calculer les rendements
    portfolio_returns = calculate_returns(portfolio_data)
    benchmark_returns = calculate_returns(benchmark_data)

    # Ajuster les poids
    weights_series = pd.Series(portfolio_weights).reindex(portfolio_returns.columns).dropna()
    weights_series = weights_series / weights_series.sum()

    # Calculer la performance
    portfolio_performance = calculate_portfolio_performance(portfolio_returns, weights_series)
    benchmark_performance = (1 + benchmark_returns).cumprod() * 100000

    # Visualisation des performances
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(portfolio_performance.index, portfolio_performance, label='Portefeuille Olympe', color='#1E3A8A')
    ax.plot(benchmark_performance.index, benchmark_performance, label='CAC 40', color='#9CA3AF')
    ax.set_title('Comparaison des performances', fontweight='bold', fontsize=16)
    ax.set_xlabel('Date')
    ax.set_ylabel('Valeur du portefeuille (€)')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_facecolor('#F3F4F6')
    fig.patch.set_facecolor('#FFFFFF')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    st.pyplot(fig)

    # Calculer les métriques avec QuantStats
    qs.extend_pandas()
    metrics = qs.reports.metrics(portfolio_returns, benchmark_returns, mode='full')

    # Afficher les métriques principales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<p class='metric-label'>Rendement total</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='metric-value'>{metrics['Total Return'][0]:.2%}</p>", unsafe_allow_html=True)
    with col2:
        st.markdown("<p class='metric-label'>Ratio de Sharpe</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='metric-value'>{metrics['Sharpe'][0]:.2f}</p>", unsafe_allow_html=True)
    with col3:
        st.markdown("<p class='metric-label'>Volatilité annualisée</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='metric-value'>{metrics['Volatility (ann.)'][0]:.2%}</p>", unsafe_allow_html=True)

    # Afficher d'autres métriques importantes
    st.markdown("## Métriques détaillées")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Alpha", f"{metrics['Alpha'][0]:.2%}")
        st.metric("Bêta", f"{metrics['Beta'][0]:.2f}")
        st.metric("Ratio de Sortino", f"{metrics['Sortino'][0]:.2f}")
    with col2:
        st.metric("Drawdown maximal", f"{metrics['Max Drawdown'][0]:.2%}")
        st.metric("Ratio de Calmar", f"{metrics['Calmar'][0]:.2f}")
        st.metric("Ratio d'information", f"{metrics['Information Ratio'][0]:.2f}")

st.markdown("""
## Pourquoi choisir Olympe Financial Group ?

Olympe Financial Group combine expertise financière et solutions personnalisées :

- **Analyse financière approfondie** : Techniques d'analyse de pointe pour optimiser vos investissements.
- **Solutions patrimoniales sur mesure** : Stratégies adaptées à vos objectifs et votre profil de risque.
- **Gestion proactive des risques** : Approche innovante pour limiter les pertes dans des conditions de marché difficiles.
- **Optimisation fiscale** : Maximisation de la valeur de votre patrimoine.

Faites confiance à Olympe Financial Group pour un avenir financier serein et prospère.
""")

# Sidebar
st.sidebar.image("https://example.com/olympe_logo.png", use_column_width=True)
st.sidebar.title("Olympe Financial Group")
st.sidebar.info("Expertise financière et solutions patrimoniales sur mesure.")
st.sidebar.button("Prendre rendez-vous")
st.sidebar.text("Contact : +33 7 81 71 44 43")
st.sidebar.text("Email : contact@olympemanagement.com")
