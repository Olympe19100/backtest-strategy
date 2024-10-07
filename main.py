import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import quantstats as qs
import tempfile

# Configuration de la page Streamlit
st.set_page_config(page_title="Olympe Financial Group - Votre Avenir Financier", layout="wide")

# CSS personnalisé pour un design plus élégant
st.markdown("""
<style>
    .stApp {
        background-color: white;
        color: black;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .stButton>button {
        color: white;
        background-color: #1E3A8A;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #2E4A9A;
    }
    .highlight {
        background-color: #F0F4FF;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .contact-info {
        background-color: #F0F4FF;
        padding: 15px;
        border-radius: 5px;
        margin-top: 20px;
    }
    .performance-section {
        background-color: #E6F0FF;
        padding: 20px;
        border-radius: 5px;
        margin-top: 30px;
        margin-bottom: 30px;
    }
    /* Changer la couleur du texte dans la barre latérale en blanc */
    .css-1d391kg {
        color: white;
    }
    /* Changer la couleur du glossaire en blanc */
    .css-1v3fvcr {
        color: white;
    }
</style>
""", unsafe_allow_html=True)

logo = "Olympe Financial group.svg"  # Remplacez par le chemin d'accès à votre logo
st.image(logo, width=200)  

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
    fig.patch.set_facecolor('white')
    
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

# Glossaire des indicateurs
glossary = {
    "Risk-Free Rate (Taux sans risque)": "Le taux de rendement d'un investissement considéré comme sans risque, généralement basé sur les obligations d'État.",
    "Time in Market (Temps sur le marché)": "Pourcentage du temps pendant lequel le portefeuille est investi sur le marché.",
    "Cumulative Return (Rendement cumulé)": "Le rendement total du portefeuille sur la période considérée, exprimé en pourcentage.",
    "CAGR % (Taux de croissance annuel composé)": "Le taux de rendement annuel moyen sur la période, prenant en compte la capitalisation des gains.",
    "Sharpe Ratio": "Mesure du rendement excédentaire par unité de risque (volatilité totale).",
    "Probabilistic Sharpe Ratio": "Probabilité que le Sharpe Ratio réel soit supérieur à zéro, basé sur les données historiques.",
    "Smart Sharpe": "Version ajustée du Sharpe Ratio tenant compte de la non-normalité des rendements.",
    "Sortino Ratio": "Semblable au Sharpe Ratio, mais ne prend en compte que la volatilité des rendements négatifs.",
    "Smart Sortino": "Version ajustée du Sortino Ratio tenant compte de la distribution réelle des rendements.",
    "Omega Ratio": "Rapport entre les gains attendus et les pertes attendues au-delà d'un certain seuil.",
    "Max Drawdown (Perte maximale)": "La plus grande perte cumulative subie par le portefeuille.",
    "Longest DD Days (Durée la plus longue de perte)": "Nombre maximal de jours consécutifs en drawdown.",
    "Volatility (annuelle)": "Mesure de la dispersion ou de la variabilité des rendements annuels.",
    "R² (Coefficient de détermination)": "Proportion de la variance des rendements expliquée par le benchmark.",
    "Information Ratio": "Rendement excédentaire du portefeuille par rapport au benchmark, ajusté par sa volatilité.",
    "Calmar Ratio": "Ratio du CAGR sur la perte maximale, mesurant le rendement ajusté du risque.",
    "Skew (Asymétrie)": "Mesure de la symétrie de la distribution des rendements.",
    "Kurtosis (Aplatissement)": "Mesure de la 'queue' de la distribution des rendements.",
    "Expected Daily/Monthly/Yearly Return": "Rendement moyen attendu quotidien, mensuel ou annuel.",
    "Kelly Criterion": "Pourcentage optimal du capital à investir pour maximiser la croissance logarithmique.",
    "Risk of Ruin (Risque de ruine)": "Probabilité que le portefeuille perde tout son capital.",
    "Daily Value-at-Risk (VaR quotidien)": "Pire perte attendue sur une journée donnée avec un certain niveau de confiance.",
    "Expected Shortfall (cVaR)": "Perte moyenne attendue au-delà du VaR.",
    "Max Consecutive Wins/Losses": "Nombre maximal de jours consécutifs avec gains ou pertes.",
    "Gain/Pain Ratio": "Ratio du gain total par rapport à la perte totale sur la période.",
    "Payoff Ratio": "Ratio du gain moyen des trades gagnants par rapport à la perte moyenne des trades perdants.",
    "Profit Factor": "Somme des gains divisée par la somme des pertes.",
    "Common Sense Ratio": "Ratio du gain net sur le maximum drawdown.",
    "CPC Index": "Cumulative Profit to Capital index, mesure l'efficacité du capital investi.",
    "Tail Ratio": "Ratio de la moyenne des gains extrêmes sur les pertes extrêmes.",
    "Outlier Win/Loss Ratio": "Impact des gains ou pertes extrêmes sur la performance globale.",
    "MTD (Month-to-Date)": "Performance depuis le début du mois jusqu'à la date actuelle.",
    "3M, 6M, YTD, 1Y, 3Y (annuel), 5Y (annuel), 10Y (annuel), All-time (annuel)": "Performances sur différentes périodes.",
    "Best/Worst Day/Month/Year": "Meilleures et pires performances sur une journée, un mois ou une année.",
    "Avg. Drawdown": "Drawdown moyen subi par le portefeuille.",
    "Avg. Drawdown Days": "Durée moyenne des périodes de drawdown.",
    "Recovery Factor": "Ratio du gain cumulé sur la perte maximale.",
    "Ulcer Index": "Mesure combinant la profondeur et la durée des drawdowns.",
    "Serenity Index": "Ratio du CAGR sur l'Ulcer Index.",
    "Avg. Up/Down Month": "Gain ou perte moyen pendant les mois positifs ou négatifs.",
    "Win Days/Month/Quarter/Year": "Pourcentage de périodes avec gain.",
    "Beta": "Sensibilité du portefeuille par rapport au benchmark.",
    "Alpha": "Rendement excédentaire du portefeuille par rapport au bêta.",
    "Correlation": "Corrélation entre les rendements du portefeuille et du benchmark.",
    "Treynor Ratio": "Rendement excédentaire par unité de risque systématique (bêta).",
    "EOY Returns vs Benchmark": "Rendements annuels par rapport au benchmark.",
    "Worst 10 Drawdowns": "Les 10 pires drawdowns du portefeuille."
}

# Afficher le glossaire dans la barre latérale
with st.sidebar:
    st.header("Glossaire des Indicateurs")
    for term, definition in glossary.items():
        st.markdown(f"**{term}**")
        st.markdown(f"<p style='color:white;'>{definition}</p>", unsafe_allow_html=True)


