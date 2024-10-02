import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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

    # Calcul manuel des métriques
    def calculate_metrics(returns, benchmark_returns):
        # Rendement cumulatif
        cumulative_return = (returns + 1).prod() - 1
        
        # CAGR
        years = (returns.index[-1] - returns.index[0]).days / 365.25
        cagr = (1 + cumulative_return) ** (1 / years) - 1
        
        # Volatilité annualisée
        volatility = returns.std() * np.sqrt(252)
        
        # Ratio de Sharpe (en supposant un taux sans risque de 0)
        sharpe_ratio = (returns.mean() * 252) / volatility
        
        # Drawdown maximal
        cum_returns = (1 + returns).cumprod()
        max_drawdown = (cum_returns / cum_returns.cummax() - 1).min()
        
        # Alpha et Beta
        covariance = returns.cov(benchmark_returns)
        variance = benchmark_returns.var()
        beta = covariance / variance
        alpha = (returns.mean() - beta * benchmark_returns.mean()) * 252
        
        # Ratio de Sortino (en supposant un taux sans risque de 0)
        downside_returns = returns[returns < 0]
        sortino_ratio = (returns.mean() * 252) / (downside_returns.std() * np.sqrt(252))
        
        # Ratio de Calmar
        calmar_ratio = cagr / abs(max_drawdown)
        
        # Ratio d'information
        tracking_error = (returns - benchmark_returns).std() * np.sqrt(252)
        information_ratio = (returns.mean() - benchmark_returns.mean()) * 252 / tracking_error
        
        # Autres métriques
        time_in_market = len(returns[returns != 0]) / len(returns) * 100
        best_day = returns.max()
        worst_day = returns.min()
        best_month = returns.resample('M').sum().max()
        worst_month = returns.resample('M').sum().min()
        win_days_pct = (returns > 0).sum() / len(returns) * 100
        
        return {
            'Start Period': returns.index[0].strftime('%Y-%m-%d'),
            'End Period': returns.index[-1].strftime('%Y-%m-%d'),
            'Time in Market': time_in_market,
            'Cumulative Return': cumulative_return,
            'CAGR﹪': cagr,
            'Sharpe': sharpe_ratio,
            'Sortino': sortino_ratio,
            'Max Drawdown': max_drawdown,
            'Volatility (ann.)': volatility,
            'Alpha': alpha,
            'Beta': beta,
            'Information Ratio': information_ratio,
            'Calmar': calmar_ratio,
            'Best Day': best_day,
            'Worst Day': worst_day,
            'Best Month': best_month,
            'Worst Month': worst_month,
            'Win Days %': win_days_pct
        }

    # Calculer les métriques
    portfolio_metrics = calculate_metrics(portfolio_returns.sum(axis=1), benchmark_returns)
    benchmark_metrics = calculate_metrics(benchmark_returns, benchmark_returns)

    # Afficher les métriques principales
    st.markdown("## Métriques principales")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<p class='metric-label'>Rendement cumulatif</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='metric-value'>{portfolio_metrics['Cumulative Return']:.2%}</p>", unsafe_allow_html=True)
    with col2:
        st.markdown("<p class='metric-label'>CAGR</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='metric-value'>{portfolio_metrics['CAGR﹪']:.2%}</p>", unsafe_allow_html=True)
    with col3:
        st.markdown("<p class='metric-label'>Ratio de Sharpe</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='metric-value'>{portfolio_metrics['Sharpe']:.2f}</p>", unsafe_allow_html=True)

    # Afficher d'autres métriques importantes
    st.markdown("## Métriques détaillées")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Volatilité annualisée", f"{portfolio_metrics['Volatility (ann.)']:.2%}")
        st.metric("Max Drawdown", f"{portfolio_metrics['Max Drawdown']:.2%}")
        st.metric("Ratio de Sortino", f"{portfolio_metrics['Sortino']:.2f}")
    with col2:
        st.metric("Alpha", f"{portfolio_metrics['Alpha']:.2%}")
        st.metric("Beta", f"{portfolio_metrics['Beta']:.2f}")
        st.metric("Ratio d'information", f"{portfolio_metrics['Information Ratio']:.2f}")

    # Afficher un tableau comparatif
    st.markdown("## Comparaison avec le benchmark")
    comparison_df = pd.DataFrame({
        'Métrique': portfolio_metrics.keys(),
        'Portefeuille Olympe': portfolio_metrics.values(),
        'Benchmark (CAC 40)': benchmark_metrics.values()
    })
    st.table(comparison_df.set_index('Métrique'))

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
