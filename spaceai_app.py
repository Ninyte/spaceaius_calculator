import streamlit as st
import datetime
from io import StringIO
import pandas as pd

# Sprachdaten
translations = {
    "de": {
        "title": "Ertragssimulator",
        "start_capital": "Startkapital ($)",
        "days": "Anzahl Tage (d)",
        "interest": "Durchschnittlicher täglicher Ertrag (%)",
        "reinvest": "Reinvestieren (je 50$ angesparter Ertrag)",
        "calculate": "Berechnen",
        "final_capital": "Endkapital nach {days} Tagen:",
        "remaining": "Nicht-reinvestierter Ertrag:",
        "details": "📈 Detailierte Kapitalentwicklung",
        "scroll": "ℹ️ Scrollen, um alle Einträge zu sehen",
        "save": "📥 Ergebnisse speichern",
        "boni_stage": "Bonusstufe",
        "bonus_options": ["S0 (+0%)", "S1 (+10%)", "S2 (+15%)", "S3 (+25%)", "S4 (+35%)", "Indiv. Bonus (%)"],
        "custom_bonus_input": "Gib deinen Bonus (%) ein:",
        "instructions": """
        **ℹ️ Anleitung:**
        1. Startkapital ($) eingeben
        2. Laufzeit (d) wählen
        3. Täglichen Zinssatz (%) anpassen
        4. Wähle die entsprechende Bonusstufe
        5. Reinvestition aktivieren/deaktivieren
        6. **_Eigene Gewinne generieren:_** 
            - _Klicke auf das SpaceAI-Logo und melde dich jetzt an!_
        """
    },
    "en": {
        "title": "Yield Simulator",
        "start_capital": "Initial Capital ($)",
        "days": "Number of Days (d)",
        "interest": "Average daily Income (%)",
        "reinvest": "Reinvest (every $50 of accumulated profit)",
        "calculate": "Calculate",
        "final_capital": "Final Capital after {days} Days:",
        "remaining": "Remaining accumulated Profit:",
        "details": "📈 Detailed Capital Development",
        "scroll": "ℹ️ Scroll to see all Entries",
        "save": "📥 Save Results",
        "boni_stage": "Bonus Level",
        "bonus_options": ["S0 (+0%)", "S1 (+10%)", "S2 (+15%)", "S3 (+25%)", "S4 (+35%)", "Custom Bonus (%)"],
        "custom_bonus_input": "Enter your Bonus (%):",
        "instructions": """
        **ℹ️ Instructions:**
        1. Enter initial Capital ($)
        2. Select Duration (d)
        3. Adjust daily Income (%)
        4. Select appropiate Bonus Level
        5. Enable/Disable Reinvestment
        6. **_Generate your own Profits:_** 
            - _Click the SpaceAI-Logo and sign up!_
        """
    }
}

# Konstanten
INVESTMENT_THRESHOLD = 50  # Schwelle für Reinvestition
DEFAULT_FILENAME = "SpaceAI_Ergebnis"

def calculate_profit(initial_capital, days, daily_interest, reinvest, bonus_percentage):
    capital = initial_capital
    intermediate_sum = 0.0
    daily_interest /= 100  # Prozent in Dezimalzahl umrechnen
    development = []

    for day in range(1, days + 1):
        # Berechne den Grundgewinn und wende den Bonuszuschlag an
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
    
    columns = ["Day", "Capital", "Accumulated", "Reinvested"] if st.session_state.lang == "en" else ["Tag", "Kapital", "Zwischensumme", "Reinvestiert"]
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

# --- Streamlit UI ---
st.set_page_config(page_title="SpaceAI Simulation", layout="centered",
    menu_items={
        'About': 'https://linktr.ee/SpaceAI_oi'
    })

# Custom CSS für die Sidebar (nur die Sidebar betreffend)
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

# Spracheinstellung: Rechtsbündig oberhalb des Rechners
col_lang_left, col_lang_right = st.columns([3, 1])
with col_lang_left:
    lang = st.radio(
        "Sprachen / Language",
        ["deutsch", "english"],
        index=1, # <-- 0=de, 1=en
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state.lang = "de" if lang == "deutsch" else "en"

# Zusätzlich mittig oberhalb des Rechners: Logo mit Link
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <a href="https://app.spaceaius.com/#/pages/login/login?invitationCode=7765924035" target="_blank">
            <img src="https://app.spaceaius.com/static/login/title.png" width="150">
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# Anweisungen aus der Sidebar (unverändert in der Sidebar)
with st.sidebar:
    # Logo mit Link über der Anleitung
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 40px; margin-top: 20px;">
            <a href="https://app.spaceaius.com/#/pages/login/login?invitationCode=7765924035" target="_blank">
                <img src="https://app.spaceaius.com/static/login/title.png" width="150">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(translations[st.session_state.lang]['instructions'])

# Aktuelle Sprache
lang_data = translations[st.session_state.lang]

# Titel
st.title(lang_data["title"])

# Eingabefelder
col1, col2 = st.columns(2)
initial_capital = col1.number_input(lang_data["start_capital"], min_value=0.0, value=950.0)
days = col2.number_input(lang_data["days"], min_value=1, value=90)

daily_interest = st.slider(lang_data["interest"], min_value=0.40, max_value=2.70, value=1.32, step=0.01)

# Neuer Radiobutton-Bereich für den Bonuszuschlag unterhalb des Schiebereglers
bonus_option = st.radio(
    lang_data["boni_stage"],
    options=lang_data["bonus_options"],  # Hier wird die Übersetzung verwendet
    index=0,
    horizontal=True
)
if any(x in bonus_option for x in ["Individueller", "Custom"]):  # Sprachunabhängige Überprüfung
    custom_bonus = st.number_input(
        lang_data["custom_bonus_input"],  # Übersetzte Eingabeaufforderung
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

# Berechnung starten
if st.button(lang_data["calculate"], type="primary"):
    development_df, final_capital, remaining = calculate_profit(
        initial_capital, days, daily_interest, reinvest, bonus_percentage
    )

    # Ergebnisse anzeigen
    st.success(f"**{lang_data['final_capital'].format(days=days)}** {final_capital:.2f} $")
    st.info(f"**{lang_data['remaining']}** {remaining:.2f} $")

    with st.expander(lang_data["details"], expanded=False):
        display_columns = ["Day", "Capital", "Accumulated", "Reinvested"] if st.session_state.lang == "en" else ["Tag", "Kapital", "Zwischensumme", "Reinvestiert"]
        st.dataframe(development_df.style.format({
            display_columns[1]: "{:.2f}",
            display_columns[2]: "{:.2f}"
        }))
        st.caption(lang_data["scroll"])

    # Download-Button für komplette Daten
    output = StringIO()
    output.write(f"Start capital: {initial_capital} $\nDays: {days}\nInterest rate: {daily_interest} %\nBonus: {bonus_percentage} %\n\n" if st.session_state.lang == "en" else f"Startkapital: {initial_capital} $\nTage: {days}\nZinssatz: {daily_interest} %\nBonus: {bonus_percentage} %\n\n")
    
    columns_header = "Day | Capital | Accumulated | Reinvested\n" if st.session_state.lang == "en" else "Tag | Kapital | Zwischensumme | Reinvestiert\n"
    output.write(columns_header)
    output.write("-" * 40 + "\n")
    
    for _, row in development_df.iterrows():
        if st.session_state.lang == "en":
            output.write(f"{row['Day']} | {row['Capital']:.2f} $ | {row['Accumulated']:.2f} $ | {'✅' if row['Reinvested'] else '❌'}\n")
        else:
            output.write(f"{row['Tag']} | {row['Kapital']:.2f} $ | {row['Zwischensumme']:.2f} $ | {'✅' if row['Reinvestiert'] else '❌'}\n")

    st.download_button(
        label=lang_data["save"],
        data=output.getvalue(),
        file_name=f"{DEFAULT_FILENAME}_{datetime.date.today().strftime('%Y-%m-%d')}.txt",
        mime="text/plain"
    )
