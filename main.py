import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pyfolio as pf

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
    start_date = st.date_input("Date de début", value=datetime(2019, 9, 30))
with col2:
    end_date = st.date_input("Date de fin", value=datetime(2024, 9, 30))

if st.button("Analyser le portefeuille"):
    # Télécharger les données
    with st.spinner("Téléchargement des données..."):
        portfolio_data = download_data(list(portfolio_weights.keys()), start_date, end_date)
        benchmark_data = download_data('^FCHI', start_date, end_date)  # CAC 40

    # Calculer les rendements
    portfolio_returns = calculate_returns(portfolio_data)
    benchmark_returns = calculate_returns(benchmark_data)

    # Calculer les rendements pondérés du portefeuille
    weights_series = pd.Series(portfolio_weights)
    weighted_returns = (portfolio_returns * weights_series).sum(axis=1)

    # Calculer les métriques avec pyfolio
    perf_stats = pf.timeseries.perf_stats(weighted_returns)
    benchmark_stats = pf.timeseries.perf_stats(benchmark_returns)

    # Visualisation des performances
    fig, ax = plt.subplots(figsize=(12, 6))
    cumulative_returns = (1 + weighted_returns).cumprod()
    cumulative_benchmark = (1 + benchmark_returns).cumprod()
    ax.plot(cumulative_returns.index, cumulative_returns, label='Portefeuille Olympe', color='#1E3A8A')
    ax.plot(cumulative_benchmark.index, cumulative_benchmark, label='CAC 40', color='#9CA3AF')
    ax.set_title('Comparaison des performances', fontweight='bold', fontsize=16)
    ax.set_xlabel('Date')
    ax.set_ylabel('Rendement cumulatif')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_facecolor('#F3F4F6')
    fig.patch.set_facecolor('#FFFFFF')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    st.pyplot(fig)

    # Afficher les métriques principales
    st.markdown("## Métriques principales")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<p class='metric-label'>Rendement annualisé</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='metric-value'>{perf_stats['Annual return']:.2%}</p>", unsafe_allow_html=True)
    with col2:
        st.markdown("<p class='metric-label'>Ratio de Sharpe</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='metric-value'>{perf_stats['Sharpe ratio']:.2f}</p>", unsafe_allow_html=True)
    with col3:
        st.markdown("<p class='metric-label'>Volatilité annualisée</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='metric-value'>{perf_stats['Annual volatility']:.2%}</p>", unsafe_allow_html=True)

    # Afficher d'autres métriques importantes
    st.markdown("## Métriques détaillées")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Max Drawdown", f"{perf_stats['Max drawdown']:.2%}")
        st.metric("Ratio de Sortino", f"{perf_stats['Sortino ratio']:.2f}")
    with col2:
        st.metric("Ratio de Calmar", f"{perf_stats['Calmar ratio']:.2f}")
        st.metric("Ratio d'information", f"{perf_stats['Information ratio']:.2f}")

    # Afficher un tableau comparatif
    st.markdown("## Comparaison avec le benchmark")
    comparison_df = pd.concat([perf_stats, benchmark_stats], axis=1)
    comparison_df.columns = ['Portefeuille Olympe', 'Benchmark (CAC 40)']
    st.table(comparison_df)

# Contenu inspiré de la plaquette commerciale
st.markdown("""
## Pourquoi choisir Olympe Financial Group ?

Olympe Financial Group combine expertise financière et solutions personnalisées pour vous offrir le meilleur :

- **Analyse financière approfondie** : Nos experts utilisent des techniques d'analyse de pointe pour comprendre les tendances du marché et optimiser vos investissements.
- **Solutions patrimoniales sur mesure** : Nous élaborons des stratégies personnalisées adaptées à vos objectifs et votre profil de risque.
- **Gestion proactive des risques** : Notre approche innovante a permis à nos clients de limiter leurs pertes, même dans des conditions de marché difficiles.
- **Optimisation fiscale** : Nous identifions les opportunités d'optimisation fiscale pour maximiser la valeur de votre patrimoine.

Faites confiance à Olympe Financial Group pour vous guider vers un avenir financier serein et prospère.
""")

# Sidebar
st.sidebar.image("https://example.com/olympe_logo.png", use_column_width=True)
st.sidebar.title("Olympe Financial Group")
st.sidebar.info("Expertise financière et solutions patrimoniales sur mesure.")
st.sidebar.button("Prendre rendez-vous")
st.sidebar.text("Contact : +33 7 81 71 44 43")
st.sidebar.text("Email : contact@olympemanagement.com")
