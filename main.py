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
</style>
""", unsafe_allow_html=True)

# Ajouter le logo en haut de la page
logo = "path_to_your_logo/logo.png"  # Remplacez par le chemin d'accès à votre logo
st.image(logo, width=200)  # Ajustez la largeur selon vos besoins

# En-tête
st.title("Olympe Financial Group - Façonnez Votre Avenir Financier")

st.markdown("""
<div class="highlight">
    <h2>Expertise Financière à Votre Service</h2>
    <p>Chez Olympe Financial Group, nous comprenons que votre avenir financier est unique. Nous croyons fermement que vous méritez une approche personnalisée, conçue pour répondre à vos besoins spécifiques. C'est pourquoi notre équipe d'experts utilise des stratégies financières de pointe pour vous aider à atteindre vos objectifs. Ensemble, nous pouvons bâtir un avenir financier plus sûr et plus prospère.</p>
</div>
""", unsafe_allow_html=True)

# Section d'analyse de portefeuille
st.header("Analyse de Portefeuille Personnalisée")
st.write("Votre portefeuille mérite une attention particulière. Nous vous offrons une analyse approfondie qui vous permet de prendre des décisions éclairées, basées sur des données fiables et des stratégies performantes.")

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

    st.success("Analyse complétée avec succès ! Voici les résultats de votre portefeuille personnalisé.")

# Section "Pourquoi Nous Choisir"
st.header("Pourquoi Choisir Olympe Financial Group ?")
st.markdown("""
Vous avez travaillé dur pour accumuler votre patrimoine, et il mérite une gestion à la hauteur de vos attentes. Voici pourquoi nous sommes le partenaire idéal pour votre avenir financier :

- **Expertise Personnalisée**: Nos stratégies sont spécifiquement adaptées à votre profil et vos objectifs financiers. Vous bénéficiez d'une attention sur-mesure qui vous guide à chaque étape.
- **Gestion Rigoureuse des Risques**: Notre approche vous protège des turbulences du marché, en vous aidant à minimiser les risques tout en maximisant vos opportunités.
- **Optimisation de la Performance**: Nous utilisons des outils d'analyse avancés pour identifier les meilleures opportunités et vous permettre de dépasser vos attentes.

Nous croyons fermement qu'une gestion proactive et rigoureuse de votre portefeuille vous mènera vers des résultats exceptionnels. Ensemble, nous transformerons vos ambitions en réalisations concrètes.
""")

# Section "Performance"
st.markdown("""
<div class="performance-section">
    <h2>Performances Avancées en Gestion de Portefeuille</h2>
    <p>Grâce à des algorithmes financiers de pointe et une gestion minutieuse des risques, nos stratégies vous permettent de tirer parti des opportunités tout en minimisant les pertes. Nos clients nous font confiance pour protéger et faire croître leur patrimoine, même dans des périodes de marché difficile.</p>
</div>
""", unsafe_allow_html=True)

# Charger et afficher le rapport HTML de gestion des risques
with open('rapport_performance (24).html', 'r') as f:
    risk_management_report = f.read()

st.components.v1.html(risk_management_report, height=600, scrolling=True)

# Témoignages
st.header("Ce Que Disent Nos Clients")
st.markdown("""
Chez Olympe Financial Group, nous croyons que nos clients sont notre meilleure publicité. Voici ce qu'ils disent à propos de notre service :

- *"Grâce à Olympe Financial Group, j'ai pu optimiser mon portefeuille et atteindre mes objectifs financiers plus rapidement que je ne l'aurais imaginé."* - Sophie D., Entrepreneur.
- *"L'expertise et le professionnalisme de l'équipe Olympe ont complètement transformé ma vision de la gestion patrimoniale."* - Marc L., Cadre Supérieur.

Ces témoignages reflètent notre engagement à fournir des résultats exceptionnels. Vous aussi, faites le choix d'une gestion financière axée sur vos objectifs.
""")

# Appel à l'action
st.markdown("""
<div class="highlight">
    <h3>Prêt à Sécuriser Votre Avenir Financier ?</h3>
    <p>Ne laissez pas passer l'occasion d'optimiser vos investissements. Contactez-nous dès aujourd'hui pour une consultation gratuite et personnalisée.</p>
</div>
""", unsafe_allow_html=True)

# Information de contact
st.markdown("""
<div class="contact-info">
    <h3>Contactez Olympe Financial Group</h3>
    <p>📞 Téléphone : +33 7 81 71 44 43</p>
    <p>📧 Email : contact@olympemanagement.com</p>
    <p>Expertise financière et solutions patrimoniales sur mesure.</p>
</div>
""", unsafe_allow_html=True)

