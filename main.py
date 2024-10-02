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
    .stSidebar {
        background-color: #f0f2f6;
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
    .metric-card {
        background-color: #F0F4FF;
        padding: 15px;
        border-radius: 5px;
        text-align: center;
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

# En-tête
st.title("Olympe Financial Group - Façonnez Votre Avenir Financier")

st.markdown("""
<div class="highlight">
    <h2>Expertise Financière à Votre Service</h2>
    <p>Chez Olympe Financial Group, nous combinons expertise financière de pointe et solutions personnalisées pour vous offrir le meilleur. Notre engagement envers l'excellence se traduit par des résultats tangibles et durables pour votre patrimoine.</p>
</div>
""", unsafe_allow_html=True)

# Section d'analyse de portefeuille
st.header("Analyse de Portefeuille Personnalisée")
st.write("Découvrez la puissance de notre analyse financière approfondie. Commencez dès maintenant !")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Date de début", value=datetime(2019, 9, 30))
with col2:
    end_date = st.date_input("Date de fin", value=datetime(2024, 9, 30))

if st.button("Analyser Mon Portefeuille"):
    with st.spinner("Analyse en cours... Nous préparons votre rapport personnalisé."):
        # Télécharger les données
        portfolio_data = download_data(list(portfolio_weights.keys()), start_date, end_date)
        benchmark_data = download_data('^FCHI', start_date, end_date)  # CAC 40

        # Calculer les rendements
        portfolio_returns = calculate_returns(portfolio_data)
        benchmark_returns = calculate_returns(benchmark_data)

        # Calculer les rendements pondérés du portefeuille
        weights_series = pd.Series(portfolio_weights)
        weighted_returns = (portfolio_returns * weights_series).sum(axis=1)

        # Générer le rapport
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
            st.warning("Nous préparons un rapport simplifié pour vous offrir les meilleures insights.")
            
            # Créer et afficher un rapport simplifié
            fig = create_simplified_report(weighted_returns, benchmark_returns.squeeze())
            st.pyplot(fig)

        # Afficher quelques métriques clés
        metrics = qs.reports.metrics(weighted_returns, benchmark_returns.squeeze(), mode='full')
        
        st.subheader("Vos Métriques Clés")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{metrics['Total Return'][0]:.2%}</p>
                <p class="metric-label">Rendement Total</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{metrics['Sharpe'][0]:.2f}</p>
                <p class="metric-label">Ratio de Sharpe</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{metrics['Max Drawdown'][0]:.2%}</p>
                <p class="metric-label">Drawdown Maximum</p>
            </div>
            """, unsafe_allow_html=True)

    st.success("Analyse complétée avec succès ! Voici les résultats de votre portefeuille personnalisé.")

# Section "Pourquoi Nous Choisir"
st.header("Pourquoi Choisir Olympe Financial Group ?")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    - **Expertise Financière Approfondie**: Nos experts utilisent des techniques d'analyse de pointe pour optimiser vos investissements.
    - **Solutions Patrimoniales Sur Mesure**: Stratégies personnalisées adaptées à vos objectifs et votre profil de risque.
    """)
with col2:
    st.markdown("""
    - **Gestion Proactive des Risques**: Notre approche innovante a permis à nos clients de limiter leurs pertes, même dans des conditions de marché difficiles.
    - **Optimisation Fiscale**: Nous identifions les opportunités pour maximiser la valeur de votre patrimoine.
    """)

# Appel à l'action
st.markdown("""
<div class="highlight">
    <h3>Prêt à Sécuriser Votre Avenir Financier ?</h3>
    <p>Ne laissez pas passer cette opportunité de transformer votre situation financière. Contactez-nous dès aujourd'hui pour une consultation gratuite et personnalisée.</p>
    <p>📞 +33 7 81 71 44 43 | 📧 contact@olympemanagement.com</p>
</div>
""", unsafe_allow_html=True)

# Témoignages (fictifs pour l'exemple)
st.header("Ce Que Disent Nos Clients")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    > "Grâce à Olympe Financial Group, j'ai pu optimiser mon portefeuille et atteindre mes objectifs financiers plus rapidement que je ne l'aurais imaginé." - Sophie D., Entrepreneur
    """)
with col2:
    st.markdown("""
    > "L'expertise et le professionnalisme de l'équipe Olympe ont complètement transformé ma vision de la gestion patrimoniale." - Marc L., Cadre Supérieur
    """)

# Sidebar
st.sidebar.image("https://example.com/olympe_logo.png", use_column_width=True)
st.sidebar.title("Olympe Financial Group")
st.sidebar.info("Expertise financière et solutions patrimoniales sur mesure.")
if st.sidebar.button("Demander une Consultation"):
    st.sidebar.success("Merci de votre intérêt ! Nous vous contacterons sous peu.")
st.sidebar.markdown("---")
st.sidebar.text("Contact : +33 7 81 71 44 43")
st.sidebar.text("Email : contact@olympemanagement.com")
