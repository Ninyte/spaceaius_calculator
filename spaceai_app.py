import streamlit as st
import datetime
from io import StringIO
import pandas as pd

# Sproglige data
translations = {
    "da": {
        "title": "Afkastsimulator",
        "title_help": "Simulerer kapitaludvikling baseret på dagligt afkast og bonustillæg.",
        "start_capital": "Startkapital ($)",
        "days": "Antal dage (d)",
        "interest": "Gennemsnitligt dagligt afkast (%)",
        "interest_help": "Den forudindstillede procentdel afspejler det beregnede gennemsnitlige afkast.",
        "reinvest": "Geninvester (når akkumuleret afkast > 50 $)",
        "calculate": "Beregn",
        "final_capital": "Slutkapital efter {days} dage:",
        "remaining": "Yderligere resterende akkumuleret afkast:",
        "details": "📈 Detaljeret kapitaludvikling",
        "scroll": "ℹ️ Scroll for at se alle indlæg",
        "save": "📥 Gem resultater",
        "boni_stage": "Bonusniveau",
        "bonus_options": ["S0 (+0%)", "S1 (+10%)", "S2 (+15%)", "S3 (+25%)", "S4 (+35%)", "Tilpasset bonus (%)"],
        "custom_bonus_input": "Indtast din bonus (%):",
        "total_profit": "Samlet fortjeneste",
        "capital_growth": "Kapitalvækst",
        "non_reinvested": "heraf ikke-geninvesteret",
        "filename": "SpaceAI_Resultat",
        "net_profit": "Nettofortjeneste",
        "instructions": """
        **ℹ️ Instruktioner:**
        1. Indtast startkapital ($)
        2. Vælg varighed (d)
        3. Juster dagligt afkast (%)
        4. Vælg passende bonusniveau
        5. Aktiver/deaktiver geninvestering
        6. **_Generer din egen indkomst:_**
            - _Klik på SpaceAI-logoet og tilmeld dig!_
        """
    }
}

# Konstanter
INVESTMENT_THRESHOLD = 50  # Grænse for geninvestering
DEFAULT_FILENAME = "SpaceAI_Resultat"

# Constants for pool thresholds
POOL1_MIN = 50
POOL1_MAX = 950
POOL2_MIN = 1000
POOL2_MAX = 9000
POOL3_MIN = 10000
POOL3_MAX = 90000

def calculate_pool_profit(initial_capital, days, daily_interest, reinvest, bonus_percentage, pool_min, pool_max):
    """Calculate profit for a specific pool."""
    capital = min(initial_capital, pool_max)  # Capital allocated to this pool
    intermediate_sum = 0.0
    daily_interest /= 100  # Convert percentage to decimal
    development = []

    for day in range(1, days + 1):
        # Calculate daily profit and apply bonus
        profit = round(capital * daily_interest, 2)
        profit = round(profit * (1 + bonus_percentage / 100), 2)
        intermediate_sum = round(intermediate_sum + profit, 2)

        reinvested = False
        if reinvest and intermediate_sum >= INVESTMENT_THRESHOLD:
            steps = int(intermediate_sum // INVESTMENT_THRESHOLD)
            capital = round(capital + INVESTMENT_THRESHOLD * steps, 2)
            intermediate_sum = round(intermediate_sum - INVESTMENT_THRESHOLD * steps, 2)
            reinvested = True

        development.append((day, capital, intermediate_sum, reinvested))

    columns = ["Dag", "Kapital", "Akkumuleret", "Geninvesteret"]
    development_df = pd.DataFrame(
        development,
        columns=columns
    ).astype({
        columns[0]: "int32",
        columns[1]: "float64",
        columns[2]: "float64",
        columns[3]: "bool"
    })

    return development_df, round(capital, 2), round(intermediate_sum, 2)

def calculate_pool_profit_with_assets(initial_capital, days, daily_interest, reinvest, bonus_percentage):
    """Calculate profit across multiple pools with asset management."""
    # Startkapital investeres i den størst mulige pulje inden for grænserne
    pool3_capital = int(min(initial_capital, POOL3_MAX)) if initial_capital >= POOL3_MIN else 0
    remaining_capital = int(max(0, initial_capital - pool3_capital))

    pool2_capital = int(min(remaining_capital, POOL2_MAX)) if remaining_capital >= POOL2_MIN else 0
    remaining_capital = int(max(0, remaining_capital - pool2_capital))

    pool1_capital = int(min(remaining_capital, POOL1_MAX)) if remaining_capital >= POOL1_MIN else 0
    assets = int(max(0, remaining_capital - pool1_capital))

    intermediate_sum = 0
    daily_interest /= 100  # Konverter procent til decimaltal
    development = []

    # Startdage for hver pulje
    pool1_start_day = 1 if pool1_capital > 0 else None
    pool2_start_day = 1 if pool2_capital > 0 else None
    pool3_start_day = 1 if pool3_capital > 0 else None

    for day in range(1, days + 1):
        # Beregn afkast for Pulje 3 (starter dagen efter investering)
        if pool3_capital > 0 and day > (pool3_start_day or 0):
            profit = int(round(pool3_capital * daily_interest))
            profit = int(round(profit * (1 + bonus_percentage / 100)))
            intermediate_sum += profit

        # Beregn afkast for Pulje 2 (starter dagen efter investering)
        if pool2_capital > 0 and day > (pool2_start_day or 0):
            profit = int(round(pool2_capital * daily_interest))
            profit = int(round(profit * (1 + bonus_percentage / 100)))
            intermediate_sum += profit

        # Beregn afkast for Pulje 1 (starter dagen efter investering)
        if pool1_capital > 0 and day > (pool1_start_day or 0):
            profit = int(round(pool1_capital * daily_interest))
            profit = int(round(profit * (1 + bonus_percentage / 100)))
            intermediate_sum += profit

        # Flyt kapital fra Pulje 1 til Pulje 2, hvis Pulje 1 er fuld, og der er nok i Akkumuleret
        if pool1_capital == POOL1_MAX and intermediate_sum >= 50:
            intermediate_sum += pool1_capital  # Flyt Pulje 1 til Akkumuleret
            pool1_capital = 0
            if intermediate_sum >= POOL2_MIN:  # Reinvester i Pulje 2
                pool2_capital += intermediate_sum
                intermediate_sum = 0
                pool2_start_day = day + 1  # Reinvestering i Pulje 2 starter dagen efter

        # Reinvestering (uden prioritering, men med minimumsgrænser)
        if reinvest and intermediate_sum >= INVESTMENT_THRESHOLD:
            if intermediate_sum >= POOL3_MIN and pool3_capital < POOL3_MAX:
                reinvest_amount = int(min(POOL3_MAX - pool3_capital, intermediate_sum))
                pool3_capital += reinvest_amount
                intermediate_sum -= reinvest_amount
                pool3_start_day = day + 1  # Reinvestering i Pulje 3 starter dagen efter
            elif intermediate_sum >= POOL2_MIN and pool2_capital < POOL2_MAX:
                reinvest_amount = int(min(POOL2_MAX - pool2_capital, intermediate_sum))
                pool2_capital += reinvest_amount
                intermediate_sum -= reinvest_amount
                pool2_start_day = day + 1  # Reinvestering i Pulje 2 starter dagen efter
            elif intermediate_sum >= POOL1_MIN and pool1_capital < POOL1_MAX:
                reinvest_amount = int(min(POOL1_MAX - pool1_capital, intermediate_sum))
                pool1_capital += reinvest_amount
                intermediate_sum -= reinvest_amount
                pool1_start_day = day + 1  # Reinvestering i Pulje 1 starter dagen efter

        # Flyt overskydende kapital fra Pulje 1 til Assets
        if pool1_capital > POOL1_MAX:
            excess = pool1_capital - POOL1_MAX
            assets += excess
            pool1_capital = POOL1_MAX

        # Registrer daglig udvikling
        development.append((day, pool1_capital, pool2_capital, pool3_capital, assets, intermediate_sum))

    # Opret DataFrame for udvikling
    columns = ["Dag", "Pulje 1", "Pulje 2", "Pulje 3", "Assets", "Akkumuleret"]
    development_df = pd.DataFrame(
        development,
        columns=columns
    ).astype({
        columns[0]: "int32",
        columns[1]: "float64",
        columns[2]: "float64",
        columns[3]: "float64",
        columns[4]: "float64",
        columns[5]: "float64"
    })

    return development_df, pool1_capital, pool2_capital, pool3_capital, assets, intermediate_sum

# --- Streamlit UI ---
st.set_page_config(page_title="SpaceAI Simulation", layout="centered",
    menu_items={
        'About': 'https://linktr.ee/SpaceAI_oi'
    })

# Brugerdefineret CSS til sidebjælken (kun sidebjælken)
st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #333333;
    }
    [data-testid=stSidebar] * {
        color: white;
    }
    [data-testid=stSidebar] .stRadio label {
        color: white !important;
    }
    [data-testid=stSidebar] .stMarkdown p,
    [data-testid=stSidebar] .stMarkdown li,
    [data-testid=stSidebar] .stMarkdown strong {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Sprogindstilling: Højrestillet over beregneren
col_lang_left, col_lang_right = st.columns([3, 1])
with col_lang_left:
    lang = st.radio(
        "Sprog",
        ["dansk"],
        index=0, # <-- Kun dansk
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state.lang = "da"

# Yderligere centreret over beregneren: Logo med link
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://app.spaceaius.com/static/login/title.png" width="150">
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# Instruktioner fra sidebjælken (uændret i sidebjælken)
with st.sidebar:
    # Logo med link over instruktionerne
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 40px; margin-top: 20px;">
                <img src="https://app.spaceaius.com/static/login/title.png" width="150">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(translations[st.session_state.lang]['instructions'])

# Aktuelt sprog
lang_data = translations[st.session_state.lang]

# Titel som overskrift (med hjælpeikon):
st.header(
    lang_data["title"],
    help=lang_data["title_help"]  # Værktøjstip her
)

# Inputfelter
col1, col2 = st.columns(2)
initial_capital = col1.number_input(lang_data["start_capital"], min_value=0.0, value=950.0)
days = col2.number_input(lang_data["days"], min_value=1, value=90)


# Slider med justeret hjælpeparameter
daily_interest = st.slider(
    lang_data["interest"],
    min_value=0.40,
    max_value=2.70,
    value=1.32,
    step=0.01,
    help=lang_data["interest_help"]  # Her kommer værktøjstippet
)

# Nyt radiobutton-område for bonustillægget under skyderen
bonus_option = st.radio(
    lang_data["boni_stage"],
    options=lang_data["bonus_options"],  # Her bruges oversættelsen
    index=0,
    horizontal=True
)
if any(x in bonus_option for x in ["Tilpasset", "Custom"]):  # Sproguafhængig kontrol
    custom_bonus = st.number_input(
        lang_data["custom_bonus_input"],  # Oversat inputprompt
        min_value=0,
        max_value=100,
        step=5,
        value=0
    )
    bonus_percentage = custom_bonus
elif bonus_option.startswith("S0"):
    bonus_percentage = 0
elif bonus_option.startswith("S1"):
    bonus_percentage = 10
elif bonus_option.startswith("S2"):
    bonus_percentage = 15
elif bonus_option.startswith("S3"):
    bonus_percentage = 25
elif bonus_option.startswith("S4"):
    bonus_percentage = 35

reinvest = st.checkbox(lang_data["reinvest"], value=True)

# Start calculation
if st.button(lang_data["calculate"], type="primary"):
    # Calculate across all pools
    development_df, pool1_final, pool2_final, pool3_final, assets, total_accumulated = calculate_pool_profit_with_assets(
        initial_capital, days, daily_interest, reinvest, bonus_percentage
    )

    # Display results
    st.subheader("Resultater")
    st.info(f"**Pulje 1 Slutkapital:** {pool1_final:.2f} $")
    st.info(f"**Pulje 2 Slutkapital:** {pool2_final:.2f} $")
    st.info(f"**Pulje 3 Slutkapital:** {pool3_final:.2f} $")
    st.info(f"**Assets:** {assets:.2f} $")
    st.success(f"**Samlet Akkumuleret:** {total_accumulated:.2f} $")

    # Display detailed development
    with st.expander(lang_data["details"], expanded=False):
        st.dataframe(development_df.style.format({"Pulje 1": "{:.2f}", "Pulje 2": "{:.2f}", "Pulje 3": "{:.2f}", "Assets": "{:.2f}", "Akkumuleret": "{:.2f}"}))

    # Total summary
    total_final_capital = pool1_final + pool2_final + pool3_final
    net_profit = total_final_capital - initial_capital + total_accumulated
    st.success(f"**{lang_data['net_profit']}:** {net_profit:.2f} $")
