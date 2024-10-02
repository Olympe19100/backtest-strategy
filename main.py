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
    return data.tz_localize(None)  # Normalize dates

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

# Interface utilisateur Streamlit
st.title("Olympe Financial Group - Analyse de Portefeuille")

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

    # Ajuster les poids pour correspondre aux données disponibles
    weights_series = pd.Series(portfolio_weights)
    weights_series = weights_series.reindex(portfolio_returns.columns).dropna()
    weights_series = weights_series / weights_series.sum()

    # Calculer la performance du portefeuille
    portfolio_performance = calculate_portfolio_performance(portfolio_returns, weights_series)

    # Calculer la performance du benchmark (CAC 40)
    benchmark_performance = (1 + benchmark_returns).cumprod() * 100000

    # Visualisation des performances
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(portfolio_performance.index, portfolio_performance, label='Portefeuille Olympe')
    ax.plot(benchmark_performance.index, benchmark_performance, label='CAC 40')
    ax.set_title('Comparaison des performances', fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Valeur du portefeuille (€)')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Personnalisation du style pour correspondre à la charte graphique d'Olympe
    ax.set_facecolor('#f0f0f0')  # Fond gris clair
    fig.patch.set_facecolor('#ffffff')  # Fond blanc
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    st.pyplot(fig)

    # Calculer et afficher les rendements totaux
    portfolio_total_return = (portfolio_performance.iloc[-1] / portfolio_performance.iloc[0]) - 1
    benchmark_total_return = (benchmark_performance.iloc[-1] / benchmark_performance.iloc[0]) - 1

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Performance du Portefeuille Olympe", f"{portfolio_total_return:.2%}")
    with col2:
        st.metric("Performance du CAC 40", f"{benchmark_total_return:.2%}")

    # Générer le rapport QuantStats
    with st.spinner("Génération du rapport d'analyse..."):
        qs.extend_pandas()
        report = qs.reports.html(portfolio_performance.pct_change(), benchmark=benchmark_returns, output=None)
        st.components.v1.html(report, height=600, scrolling=True)

st.markdown("""
## Pourquoi choisir Olympe Financial Group ?

Olympe Financial Group combine expertise financière et solutions personnalisées pour vous offrir le meilleur :

- **Analyse financière approfondie** : Nos experts utilisent des techniques d'analyse de pointe pour comprendre les tendances du marché et optimiser vos investissements.
- **Solutions patrimoniales sur mesure** : Nous élaborons des stratégies personnalisées adaptées à vos objectifs et votre profil de risque.
- **Gestion proactive des risques** : Notre approche innovante a permis à nos clients de limiter leurs pertes, même dans des conditions de marché difficiles.
- **Optimisation fiscale** : Nous identifions les opportunités d'optimisation fiscale pour maximiser la valeur de votre patrimoine.

Faites confiance à Olympe Financial Group pour vous guider vers un avenir financier serein et prospère.

[En savoir plus sur nos services](https://www.olympefinancialgroup.com)
""")

st.sidebar.image("https://example.com/olympe_logo.png", use_column_width=True)
st.sidebar.title("Olympe Financial Group")
st.sidebar.info("Expertise financière et solutions patrimoniales sur mesure.")
st.sidebar.button("Prendre rendez-vous")
st.sidebar.text("Contact : +33 7 81 71 44 43")
st.sidebar.text("Email : contact@olympemanagement.com")
