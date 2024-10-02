import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import quantstats as qs
import tempfile
from scipy.stats import norm
import backtrader as bt

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

# Fonction pour télécharger les données
@st.cache_data
def download_data(tickers, start_date, end_date):
    data = yf.download(tickers + ['^FCHI'], start=start_date, end=end_date)['Adj Close']
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

# Fonction pour la simulation de Monte Carlo
def monte_carlo_simulation(returns, initial_investment, num_simulations, num_months):
    monthly_returns = returns.resample('M').sum()
    mean_return = monthly_returns.mean()
    std_return = monthly_returns.std()
    
    simulations = np.random.normal(mean_return, std_return, (num_simulations, num_months))
    simulated_returns = np.cumprod(1 + simulations, axis=1)
    simulated_values = initial_investment * simulated_returns
    
    return simulated_values

# Fonction pour calculer les probabilités avec une chaîne de Markov
def markov_chain_probabilities(returns, num_states=5, horizon=60):
    states = pd.qcut(returns, num_states, labels=False)
    transition_matrix = pd.crosstab(states[:-1], states[1:], normalize='index')
    initial_probabilities = states.value_counts(normalize=True).sort_index()
    current_probabilities = initial_probabilities
    for _ in range(horizon):
        current_probabilities = current_probabilities.dot(transition_matrix)
    return current_probabilities

# Stratégie de trading pour le backtesting
class SmaCrossStrategy(bt.Strategy):
    params = (('fast', 10), ('slow', 30))

    def __init__(self):
        sma_fast = bt.indicators.SMA(period=self.params.fast)
        sma_slow = bt.indicators.SMA(period=self.params.slow)
        self.crossover = bt.indicators.CrossOver(sma_fast, sma_slow)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        elif self.crossover < 0:
            self.close()

# Fonction pour exécuter le backtesting
def run_backtest(data, initial_cash=100000.0):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(SmaCrossStrategy)
    
    feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(feed)
    
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=0.001)
    
    cerebro.run()
    
    final_portfolio_value = cerebro.broker.getvalue()
    return final_portfolio_value

# Définition du portefeuille avec les poids spécifiés
portfolio_weights = {
    'AAPL': 0.0076, 'MSFT': 0.1285, 'GOOG': 0.0168, 'AMZN': 0.0174, 'META': 0.0526,
    'NVDA': 0.1525, 'V': 0.0207, 'MA': 0.0351, 'BRK-B': 0.0053, 'JPM': 0.0147,
    'UNH': 0.2824, 'BLK': 0.0001, 'HD': 0.0215, 'T': 0.0063, 'PFE': 0.0021,
    'MRK': 0.1109, 'PEP': 0.0447, 'JNJ': 0.0172, 'TSLA': 0.0583, 'AXP': 0.0053
}

# En-tête
st.title("Olympe Financial Group - Votre Partenaire pour un Avenir Financier Brillant")

st.markdown("""
<div class="highlight">
    <h2>Découvrez le Pouvoir de l'Analyse Financière Globale</h2>
    <p>Chez Olympe Financial Group, nous faisons ce que personne d'autre ne fait : nous analysons quotidiennement chaque société cotée en bourse dans le monde. Oui, vous avez bien lu - chaque société, chaque jour !</p>
    <p>Imaginez avoir accès à cette puissance d'analyse pour votre portefeuille. C'est exactement ce que nous vous offrons !</p>
</div>
""", unsafe_allow_html=True)

# Section d'analyse de portefeuille
st.header("Votre Portefeuille, Notre Priorité")
st.write("Prêt à voir la magie opérer sur vos investissements ? C'est parti !")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Date de début", value=datetime(2019, 9, 30))
with col2:
    end_date = st.date_input("Date de fin", value=datetime(2024, 9, 30))

initial_investment = st.number_input("Montant initial de l'investissement (€)", min_value=1000, value=100000, step=1000)

if st.button("Révélez le Potentiel de Mon Portefeuille"):
    with st.spinner("Analyse en cours... Nous préparons votre rapport personnalisé."):
        # Télécharger les données
        all_data = download_data(list(portfolio_weights.keys()), start_date, end_date)
        portfolio_data = all_data.drop('^FCHI', axis=1)
        benchmark_data = all_data['^FCHI']

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
                                benchmark=benchmark_returns, 
                                output=tmpfile.name,
                                title="Rapport d'analyse du portefeuille Olympe")
                
                with open(tmpfile.name, 'r') as f:
                    report_content = f.read()
            
            st.components.v1.html(report_content, height=600, scrolling=True)
        
        except Exception as e:
            st.warning("Nous préparons un rapport simplifié pour vous offrir les meilleures insights.")
            fig = create_simplified_report(weighted_returns, benchmark_returns)
            st.pyplot(fig)

        # Simulation de Monte Carlo
        num_simulations = 1000
        num_months = 60  # 5 ans
        simulated_values = monte_carlo_simulation(weighted_returns, initial_investment, num_simulations, num_months)

        st.subheader("Simulation de Monte Carlo sur 5 ans")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(simulated_values.T, alpha=0.1, color='blue')
        ax.plot(simulated_values.mean(axis=0), color='red', linewidth=2, label='Moyenne')
        ax.fill_between(range(num_months), 
                        np.percentile(simulated_values, 10, axis=0),
                        np.percentile(simulated_values, 90, axis=0),
                        alpha=0.2, color='blue', label='Intervalle de confiance 80%')
        ax.set_xlabel('Mois')
        ax.set_ylabel('Valeur du portefeuille (€)')
        ax.set_title(f'Simulation de Monte Carlo pour un investissement initial de {initial_investment:,}€')
        ax.legend()
        st.pyplot(fig)

        # Statistiques de la simulation
        final_values = simulated_values[:, -1]
        st.write(f"Valeur moyenne estimée après 5 ans: {final_values.mean():,.2f}€")
        st.write(f"Valeur médiane estimée après 5 ans: {np.median(final_values):,.2f}€")
        st.write(f"10e percentile: {np.percentile(final_values, 10):,.2f}€")
        st.write(f"90e percentile: {np.percentile(final_values, 90):,.2f}€")

        # Analyse des probabilités par chaîne de Markov
        st.subheader("Analyse des Probabilités par Chaîne de Markov")
        markov_probs = markov_chain_probabilities(weighted_returns)
        fig, ax = plt.subplots(figsize=(10, 6))
        markov_probs.plot(kind='bar', ax=ax)
        ax.set_title("Probabilités des États de Rendement après 5 ans")
        ax.set_xlabel("État de Rendement")
        ax.set_ylabel("Probabilité")
        st.pyplot(fig)

        st.write("Interprétation des États de Rendement:")
        st.write("- État 0: Rendements les plus faibles")
        st.write("- État 4: Rendements les plus élevés")
        st.write(f"Probabilité d'obtenir des rendements élevés (État 3 ou 4): {markov_probs.iloc[-2:].sum():.2%}")

        # Backtesting
        st.subheader("Résultats du Backtesting")
        backtest_result = run_backtest(portfolio_data, initial_investment)
        st.write(f"Valeur finale du portefeuille après backtesting: {backtest_result:,.2f}€")
        performance = (backtest_result - initial_investment) / initial_investment
        st.write(f"Performance de la stratégie: {performance:.2%}")

    st.success("Fantastique ! Voici ce que notre analyse révèle sur votre portefeuille. Préparez-vous à être impressionné !")

# Section "Pourquoi Nous Choisir"
st.header("Pourquoi Olympe Financial Group est Votre Meilleur Choix")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    - **Analyse Mondiale Inégalée** : Nous scrutons chaque action, chaque jour, pour vous offrir les meilleures opportunités.
    - **Stratégies Sur Mesure** : Votre succès est unique, tout comme nos solutions pour vous.
    """)
with col2:
    st.markdown("""
    - **Protection Intelligente** : Nos algorithmes veillent sur votre argent 24/7, même quand vous dormez.
    - **Optimisation Fiscale Astucieuse** : Gardez plus d'argent dans vos poches, légalement et intelligemment.
    """)

# Section sur les performances avancées
st.markdown("""
<div class="performance-section">
    <h2>Notre Secret : La Gestion de Risque à la Pointe de la Technologie</h2>
    <p>Vous vous demandez comment nous transformons des données en or ? Laissez-nous vous montrer comment notre technologie travaille dur pour votre argent.</p>
</div>
""", unsafe_allow_html=True)

# Charger et afficher le rapport de performance
with open('rapport_performance (24).html', 'r') as f:
    risk_management_report = f.read()

st.components.v1.html(risk_management_report, height=600, scrolling=True)

st.markdown("""
st.markdown("""
<div class="highlight">
    <h3>Ce Que Notre Technologie Signifie Pour Vous :</h3>
    <ul>
        <li>Dormez sur vos deux oreilles : nous réduisons les montagnes russes financières</li>
        <li>Un bouclier contre les tempêtes du marché : votre argent est protégé</li>
        <li>Le meilleur des deux mondes : plus de gains, moins de risques</li>
        <li>Toujours un coup d'avance : nous nous adaptons plus vite que le marché change</li>
    </ul>
    <p>En 2022, quand d'autres perdaient gros, nos clients souriaient. Pourquoi ? Notre technologie avait prévu la tempête et protégé leur argent.</p>
</div>
""", unsafe_allow_html=True)

# Témoignages
st.header("Ce Que Nos Clients Heureux Racontent")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    > "Avec Olympe, mon argent travaille plus intelligemment. Je n'ai jamais été aussi serein financièrement." - Sophie D., Entrepreneur
    """)
with col2:
    st.markdown("""
    > "Ces gens sont des magiciens de la finance ! Mon portefeuille n'a jamais été aussi performant." - Marc L., Cadre Supérieur
    """)

# Appel à l'action
st.markdown("""
<div class="highlight">
    <h3>Prêt à Rejoindre le Club des Investisseurs Gagnants ?</h3>
    <p>Ne laissez pas votre argent dormir. Chez Olympe, nous le faisons danser au rythme des marchés mondiaux. Contactez-nous maintenant et voyez la différence par vous-même !</p>
</div>
""", unsafe_allow_html=True)

# Information de contact
st.markdown("""
<div class="contact-info">
    <h3>Parlons de Votre Avenir Financier</h3>
    <p>📞 Un coup de fil pour un avenir brillant : +33 7 81 71 44 43</p>
    <p>📧 Un email pour des opportunités infinies : contact@olympemanagement.com</p>
    <p>Olympe Financial Group : Où Votre Argent Devient Un Super-Héros</p>
</div>
""", unsafe_allow_html=True)

if st.button("Je Veux Mon Plan Financier Personnalisé"):
    st.success("Excellente décision ! Nous avons hâte de vous montrer comment nous pouvons faire briller votre avenir financier. Attendez-vous à un appel de notre équipe d'experts très bientôt !")

# Pied de page
st.markdown("""
---
<p style='text-align: center; color: gray;'>© 2024 Olympe Financial Group. Tous droits réservés.</p>
""", unsafe_allow_html=True)

