import streamlit as st
import datetime
from io import StringIO
import pandas as pd

# Sprachdaten
translations = {
    "de": {
        "title": "🚀 SpaceAI Rechner",
        "start_capital": "Startkapital ($)",
        "days": "Anzahl Tage",
        "interest": "Durchschnittlicher täglicher Gewinn (%)",
        "reinvest": "Reinvestieren (je ab 50$ Zwischensumme)",
        "calculate": "Berechnen",
        "final_capital": "Endkapital nach {days} Tagen:",
        "remaining": "Verbleibende Zwischensumme:",
        "details": "📈 Detailierte Kapitalentwicklung",
        "scroll": "ℹ️ Scrollen, um alle Einträge zu sehen",
        "save": "📥 Ergebnisse speichern",
        "instructions": """
        **ℹ️ Anleitung:**
        1. Startkapital in $ eingeben
        2. Laufzeit in Tagen wählen
        3. Täglichen Zinssatz anpassen
        4. Reinvestition aktivieren/deaktivieren
        5. **Eigene Gewinne generieren:** 
            - Klicke auf das SpaceAI-Logo und melde dich jetzt an!
        """
    },
    "en": {
        "title": "🚀 SpaceAI Calculator",
        "start_capital": "Initial capital ($)",
        "days": "Number of days",
        "interest": "Average daily profit (%)",
        "reinvest": "Reinvest (every $50 of accumulated profit)",
        "calculate": "Calculate",
        "final_capital": "Final capital after {days} days:",
        "remaining": "Remaining accumulated profit:",
        "details": "📈 Detailed Capital Development",
        "scroll": "ℹ️ Scroll to see all entries",
        "save": "📥 Save results",
        "instructions": """
        **ℹ️ Instructions:**
        1. Enter initial capital in $
        2. Select duration in days
        3. Adjust daily interest rate
        4. Enable/disable reinvestment
        5. **Generate your own profits:** 
            - Click the SpaceAI-logo and sign up now!
        """
    }
}

# Konstanten
INVESTMENT_THRESHOLD = 50  # Schwelle für Reinvestition
DEFAULT_FILENAME = "SpaceAI_Ergebnis"

def calculate_profit(initial_capital, days, daily_interest, reinvest):
    capital = initial_capital
    intermediate_sum = 0.0
    daily_interest /= 100  # Prozent -> Dezimal
    development = []

    for day in range(1, days + 1):
        profit = capital * daily_interest
        intermediate_sum += profit

        reinvested = False
        if reinvest and intermediate_sum >= INVESTMENT_THRESHOLD:
            steps = int(intermediate_sum // INVESTMENT_THRESHOLD)
            capital += INVESTMENT_THRESHOLD * steps
            intermediate_sum -= INVESTMENT_THRESHOLD * steps
            reinvested = True

        development.append((day, capital, intermediate_sum, reinvested))
    
    # Konvertiere die Liste in ein DataFrame mit klaren Spaltentypen
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
    
    return development_df, capital, intermediate_sum

# --- Streamlit UI ---
st.set_page_config(page_title="SpaceAI Rechner", layout="centered")

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

# Sprachauswahl in der Sidebar
with st.sidebar:
    # Spracheinstellung
    st.markdown("<p style='color: white; font-size: 16px; font-weight: normal; margin-bottom: -10px;'>Sprache / Language</p>", unsafe_allow_html=True)
    lang = st.radio(
    "Sprache / Language",  # Nicht-leeres Label für Accessibility
    ["Deutsch", "English"],
    index=0,
    label_visibility="collapsed"  # Visuell verstecken, aber für Screenreader vorhanden
    )
    st.session_state.lang = "de" if lang == "Deutsch" else "en"

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

daily_interest = st.slider(lang_data["interest"], min_value=0.4, max_value=2.7, value=0.8, step=0.1)
reinvest = st.checkbox(lang_data["reinvest"], value=True)

# Berechnung starten
if st.button(lang_data["calculate"], type="primary"):
    development_df, final_capital, remaining = calculate_profit(
        initial_capital, days, daily_interest, reinvest
    )

    # Ergebnisse anzeigen
    st.success(f"**{lang_data['final_capital'].format(days=days)}** {final_capital:.2f} $")
    st.info(f"**{lang_data['remaining']}** {remaining:.2f} $")

    with st.expander(lang_data["details"], expanded=False):
        st.dataframe(development_df)
        st.caption(lang_data["scroll"])

    # Download-Button für komplette Daten
    output = StringIO()
    output.write(f"Start capital: {initial_capital} $\nDays: {days}\nInterest rate: {daily_interest} %\n\n" if st.session_state.lang == "en" else f"Startkapital: {initial_capital} $\nTage: {days}\nZinssatz: {daily_interest} %\n\n")
    
    columns = ["Day | Capital | Accumulated | Reinvested\n" if st.session_state.lang == "en" else "Tag | Kapital | Zwischensumme | Reinvestiert\n"]
    output.write(columns[0])
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