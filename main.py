import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import quantstats as qs
import tempfile

# Configuration de la page Streamlit
st.set_page_config(page_title="Olympe Financial Group - Analyse de Portefeuille", layout="wide")

# CSS personnalisé pour le fond blanc
st.markdown("""
<style>
    .stApp {
        background-color: white;
    }
    .stSidebar {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour télécharger les données
@st.cache_data
def download_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    return data.tz_localize(None)

# Fonction pour calculer les rendements
def calculate_returns(prices):
    return prices.pct_change().dropna()

# Fonction pour créer un rapport simplifié
def create_simplified_report(returns, benchmark):
    fig, axes = plt.subplots(2, 2, figsize=(15, 15))
    fig.patch.set_facecolor('white')  # Fond blanc pour la figure
    
    # Rendements cumulatifs
    qs.plots.returns(returns, benchmark, ax=axes[0, 0])
    axes[0, 0].set_title("Rendements cumulatifs")
    axes[0, 0].set_facecolor('white')
    
    # Drawdown
    qs.plots.drawdown(returns, ax=axes[0, 1])
    axes[0, 1].set_title("Drawdown")
    axes[0, 1].set_facecolor('white')
    
    # Distribution mensuelle
    qs.plots.monthly_returns(returns, ax=axes[1, 0])
    axes[1, 0].set_title("Distribution mensuelle des rendements")
    axes[1, 0].set_facecolor('white')
    
    # Volatilité annuelle
    qs.plots.rolling_volatility(returns, ax=axes[1, 1])
    axes[1, 1].set_title("Volatilité annuelle glissante")
    axes[1, 1].set_facecolor('white')
    
    plt.tight_layout()
    return fig

# Définition du portefeuille avec les poids spécifiés
portfolio_weights = {
    'AAPL': 0.0076, 'MSFT': 0.1285, 'GOOG': 0.0168, 'AMZN': 0.0174, 'META': 0.0526,
    'NVDA': 0.1525, 'V': 0.0207, 'MA': 0.0351, 'BRK-B': 0.0053, 'JPM': 0.0147,
    'UNH': 0.2824, 'BLK': 0.0001, 'HD': 0.0215, 'T': 0.0063, 'PFE': 0.0021,
    'MRK': 0.1109, 'PEP': 0.0447, 'JNJ': 0.0172, 'TSLA': 0.0583, 'AXP': 0.0053
}

# En-tête
st.title("Olympe Financial Group - Analyse de Portefeuille")

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

    # Vérifier que les données sont dans le bon format
    if not isinstance(weighted_returns.index, pd.DatetimeIndex):
        st.error("Les données de rendement ne sont pas dans le format attendu. Veuillez vérifier vos données.")
    else:
        # Générer le rapport
        with st.spinner("Génération du rapport d'analyse..."):
            qs.extend_pandas()
            
            try:
                # Essayer d'utiliser qs.reports.html()
                with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmpfile:
                    qs.reports.html(weighted_returns, 
                                    benchmark=benchmark_returns.squeeze(), 
                                    output=tmpfile.name,
                                    title="Rapport d'analyse du portefeuille Olympe")
                    
                    with open(tmpfile.name, 'r') as f:
                        report_content = f.read()
                
                st.components.v1.html(report_content, height=600, scrolling=True)
            
            except Exception as e:
                st.warning(f"Impossible de générer le rapport complet. Création d'un rapport simplifié. Erreur: {str(e)}")
                
                # Créer et afficher un rapport simplifié
                fig = create_simplified_report(weighted_returns, benchmark_returns.squeeze())
                st.pyplot(fig)

            # Afficher quelques métriques clés
            metrics = qs.reports.metrics(weighted_returns, benchmark_returns.squeeze(), mode='full')
            
            st.subheader("Métriques clés")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rendement total", f"{metrics['Total Return'][0]:.2%}")
            with col2:
                st.metric("Ratio de Sharpe", f"{metrics['Sharpe'][0]:.2f}")
            with col3:
                st.metric("Max Drawdown", f"{metrics['Max Drawdown'][0]:.2%}")

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
