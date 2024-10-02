import streamlit as st
import yfinance as yf
import pandas as pd
import quantstats as qs
from datetime import datetime, timedelta
import tempfile

# Configuration de la page Streamlit
st.set_page_config(page_title="Olympe Financial Group - Analyse de Portefeuille", layout="wide")

# Fonction pour télécharger les données
@st.cache_data
def download_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    return data.tz_localize(None)  # Normalize dates

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

if st.button("Générer le rapport d'analyse"):
    # Télécharger les données
    with st.spinner("Téléchargement des données..."):
        portfolio_data = download_data(list(portfolio_weights.keys()), start_date, end_date)
        benchmark_data = download_data('^FCHI', start_date, end_date)  # CAC 40

    # Calculer les rendements du portefeuille
    weights = pd.Series(portfolio_weights)
    portfolio_returns = (portfolio_data * weights).sum(axis=1).pct_change().dropna()

    # Calculer les rendements du benchmark
    benchmark_returns = benchmark_data.pct_change().dropna()

    # Générer le rapport QuantStats
    with st.spinner("Génération du rapport d'analyse..."):
        qs.extend_pandas()
        
        # Créer un fichier temporaire pour le rapport
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmpfile:
            try:
                qs.reports.html(portfolio_returns, 
                                benchmark=benchmark_returns, 
                                output=tmpfile.name,
                                title="Rapport d'analyse du portefeuille Olympe")
                
                # Lire le contenu du fichier temporaire
                with open(tmpfile.name, 'r') as f:
                    report_content = f.read()
                
                # Afficher le rapport dans Streamlit
                st.components.v1.html(report_content, height=1000, scrolling=True)
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de la génération du rapport : {str(e)}")
                st.write("Aperçu des données du portefeuille :")
                st.write(portfolio_returns.head())
                st.write("Aperçu des données du benchmark :")
                st.write(benchmark_returns.head())

st.sidebar.image("https://example.com/olympe_logo.png", use_column_width=True)
st.sidebar.title("Olympe Financial Group")
st.sidebar.info("Expertise financière et solutions patrimoniales sur mesure.")
st.sidebar.button("Prendre rendez-vous")
st.sidebar.text("Contact : +33 7 81 71 44 43")
st.sidebar.text("Email : contact@olympemanagement.com")
