import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import quantstats as qs
import tempfile

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
    /* Forcer la barre principale à occuper toute la largeur */
.css-1d391kg, .css-1g6gooi {
    max-width: 100% !important;
    padding-left: 1rem;
    padding-right: 1rem;
    }
    
    /* Styles spécifiques pour la barre latérale et le glossaire */
    [data-testid="stSidebar"] {
        background-color: #1E3A8A;
    }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown h4 {
        color: white !important;
    }
    /* Assurer que tous les éléments de texte dans la barre latérale sont blancs */
    [data-testid="stSidebar"] * {
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
        st.subheader(term)
        st.write(definition)

# En-tête
st.title("Olympe Financial Group - Façonnez Votre Avenir Financier")

st.markdown("""
<div class="highlight">
    <h2>Expertise Financière à Votre Service</h2>
   <p>Chez Olympe Financial Group, nous allons bien au-delà des solutions classiques. Nous nous appuyons sur un large réseau de partenariats stratégiques et collaborons avec des professionnels agréés et réglementés par l'AMF et enregistrés à l'ORIAS, pour vous fournir des conseils financiers personnalisés et en toute sécurité. 
Grâce à nos algorithmes avancés, nous analysons toutes les sociétés cotées à travers le monde pour identifier les meilleures opportunités d'investissement. Notre engagement est simple : capturer les meilleures performances et garantir des résultats concrets et durables pour votre patrimoine.</p>

""", unsafe_allow_html=True)

# Section d'analyse de portefeuille
st.header("Analyse de Portefeuille Personnalisée")
st.write("Découvrez la puissance de notre analyse financière approfondie. Commencez dès maintenant !")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Date de début", value=datetime(2019, 9, 30))
with col2:
    end_date = st.date_input("Date de fin", value=datetime(2024, 9, 30))

if st.button("Analyse du Portefeuille"):
    with st.spinner("Analyse en cours... Nous préparons votre rapport personnalisé."):
        # Télécharger les données
        portfolio_data = download_data(list(portfolio_weights.keys()), start_date, end_date)
        benchmark_data = download_data('^FCHI', start_date, end_date)  # CAC 40

        # Vérifier que les données ont été téléchargées correctement
        if portfolio_data.empty or benchmark_data.empty:
            st.error("Les données financières n'ont pas pu être téléchargées. Veuillez réessayer plus tard.")
        else:
            # Calculer les rendements
            portfolio_returns = calculate_returns(portfolio_data)
            benchmark_returns = calculate_returns(benchmark_data)

            # Calculer les rendements pondérés du portefeuille
            weights_series = pd.Series(portfolio_weights)
            weighted_returns = (portfolio_returns * weights_series).sum(axis=1)

            # Générer le rapport
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmpfile:
                    qs.reports.html(weighted_returns, 
                                    benchmark=benchmark_returns.squeeze(), 
                                    output=tmpfile.name,
                                    title="Rapport d'analyse du portefeuille Olympe Financial Group (bleu) Face au Cac40 (jaune)")
                    with open(tmpfile.name, 'r') as f:
                        report_content = f.read()

                # Afficher le rapport
                st.components.v1.html(report_content, height=1000, scrolling=True)

            except Exception as e:
                st.warning("Nous préparons un rapport simplifié pour vous offrir les meilleures insights.")

                # Créer et afficher un rapport simplifié
                fig = create_simplified_report(weighted_returns, benchmark_returns.squeeze())
                st.pyplot(fig)

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

# Nouvelle section sur les performances avancées
st.markdown("""
<div class="performance-section">
    <h2>Nos Performances de Pointe en Gestion de Risque</h2>
    <p>Découvrez comment nos algorithmes avancés ne se contentent pas seulement de choisir les meilleurs actifs, mais gèrent activement le risque pour optimiser vos rendements.</p>
</div>
""", unsafe_allow_html=True)

# Charger et afficher le deuxième rapport HTML
with open('rapport_performance (24).html', 'r') as f:
    risk_management_report = f.read()

st.components.v1.html(risk_management_report, height=1000, scrolling=True)

st.markdown("""
<div class="highlight">
    <h3>Ce que notre Gestion de Risque Avancée signifie pour vous :</h3>
    <ul>
        <li>Réduction significative de la volatilité du portefeuille</li>
        <li>Protection accrue contre les baisses de marché</li>
        <li>Optimisation du ratio rendement/risque</li>
        <li>Adaptation dynamique aux conditions changeantes du marché</li>
    </ul>
    <p>En 2022, alors que de nombreux investisseurs subissaient des pertes importantes, nos clients ont bénéficié de notre gestion de risque proactive, limitant considérablement l'impact des turbulences du marché.</p>
</div>
""", unsafe_allow_html=True)

# Témoignages
st.header("Ce Que Disent Nos Clients")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    > "Olympe Financial Group a su déployer des stratégies financières sophistiquées qui m'ont permis de maximiser mes rendements tout en maintenant un contrôle strict sur les risques. Leur expertise en analyse quantitative est un atout." - Antoine L., Gérant de Fonds
    """)
    st.markdown("""
    > "En tant que chef d'une PME, j'avais besoin d'une gestion sur mesure pour mon entreprise et mon patrimoine personnel. L'équipe d'Olympe m'a offert un service clé en main, couvrant tous les aspects juridiques, financiers et fiscaux. Un vrai partenaire de confiance." - Karine P., Directrice d'une PME
    """)
    st.markdown("""
    > "Grâce à Olympe, j'ai pu prendre des décisions éclairées en temps de marché incertain. Leur approche rigoureuse m'a permis d'éviter des pertes majeures et de saisir des opportunités rares." - Jérôme C., Consultant Indépendant
    """)
    st.markdown("""
    > "Le soutien d'Olympe Financial Group dans la gestion de mes investissements a été remarquable. Leur capacité à ajuster la stratégie en fonction des fluctuations du marché tout en assurant un rendement optimal m'a impressionné." - Isabelle R., Particulière
    """)
    st.markdown("""
    > "Olympe m'a accompagné dans la structuration de mon entreprise familiale. Leur approche patrimoniale m'a aidé à planifier efficacement la transmission de mes actifs tout en optimisant la fiscalité." - Étienne G., Entrepreneur Familial
    """)

with col2:
    st.markdown("""
    > "Ce qui distingue Olympe, c'est leur maîtrise des algorithmes d'analyse financière. En tant qu'investisseur privé, j'ai vu mes rendements nettement améliorés grâce à leur gestion quantitative et leur contrôle des risques." - Marie T., Investisseuse Privée
    """)
    st.markdown("""
    > "Olympe a non seulement optimisé la gestion de mon patrimoine, mais ils m'ont aussi aidé à structurer mes actifs pour mieux protéger ma famille. Leur expertise juridique et patrimoniale est un véritable atout." - Fabien D., Cadre Supérieur
    """)
    st.markdown("""
    > "Olympe Financial Group m'a donné une perspective nouvelle sur la gestion des risques. Ils ont su mettre en place une stratégie d'investissement solide qui a stabilisé mes rendements dans un contexte de marché turbulent." - Lucien M., Gérant de Portefeuille
    """)
    st.markdown("""
    > "En tant que particulier avec un portefeuille modeste, je pensais ne pas avoir accès à des conseils de haute qualité. Olympe a su adapter ses services à mes besoins tout en me faisant bénéficier de leur expertise en analyse financière avancée." - Clara B., Particulière
    """)
    st.markdown("""
    > "Olympe m'a accompagné dans le développement international de mon entreprise. Grâce à leur expertise combinée en gestion financière et en structuration juridique, j'ai pu franchir ce cap sereinement." - Samuel N., CEO d'une Start-up Technologique
    """)

# Appel à l'action
st.markdown("""
<div class="highlight">
    <h3>Prêt à Sécuriser Votre Avenir Financier ?</h3>
    <p>Ne laissez pas passer cette opportunité de transformer votre situation financière. Contactez-nous dès aujourd'hui pour une consultation gratuite et personnalisée.</p>
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


