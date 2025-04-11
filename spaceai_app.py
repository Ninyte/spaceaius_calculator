import streamlit as st
import datetime
from io import StringIO

# Konstanten
INVESTMENT_THRESHOLD = 50  # Schwelle für Reinvestition
DEFAULT_FILENAME = "SpaceAI_Ergebnis"

def calculate_profit(initial_capital, days, daily_interest, reinvest):
    """Berechnet die Kapitalentwicklung (angepasst für Streamlit)"""
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

    return development, capital, intermediate_sum

# --- Streamlit UI ---
st.set_page_config(page_title="SpaceAI Rechner", layout="centered")
st.title("🚀 SpaceAI Kapitalrechner")

# Eingabefelder
col1, col2 = st.columns(2)
initial_capital = col1.number_input("Startkapital ($)", min_value=0.0, value=1000.0)
days = col2.number_input("Anzahl Tage", min_value=1, value=365)

daily_interest = st.slider("Täglicher Gewinn (%)", min_value=0.1, max_value=50.0, value=5.0, step=0.1)
reinvest = st.checkbox("Reinvestieren (ab 50 $ Zwischensumme)", value=True)

# Berechnung starten
if st.button("Berechnen", type="primary"):
    development, final_capital, remaining = calculate_profit(
        initial_capital, days, daily_interest, reinvest
    )

    # Ergebnisse anzeigen
    st.success(f"**Endkapital nach {days} Tagen:** {final_capital:.2f} $")
    st.info(f"**Verbleibende Zwischensumme:** {remaining:.2f} $")

    # Detailtabelle (nur erste 5 + letzte 5 Tage zeigen)
    with st.expander("📈 Detailierte Kapitalentwicklung"):
        if len(development) > 10:
            st.table(development[:5] + [("...", "...", "...", "...")] + development[-5:])
        else:
            st.table(development)

    # Download-Button für komplette Daten
    output = StringIO()
    output.write(f"Startkapital: {initial_capital} $\nTage: {days}\nZinssatz: {daily_interest} %\n\n")
    output.write("Tag | Kapital | Zwischensumme | Reinvestiert\n")
    output.write("-" * 40 + "\n")
    for day, capital, int_sum, reinvested in development:
        output.write(f"{day} | {capital:.2f} $ | {int_sum:.2f} $ | {'✅' if reinvested else '❌'}\n")

    st.download_button(
        label="📥 Ergebnisse speichern",
        data=output.getvalue(),
        file_name=f"{DEFAULT_FILENAME}_{datetime.date.today().strftime('%Y-%m-%d')}.txt",
        mime="text/plain"
    )

# Sidebar mit Infos
with st.sidebar:
    st.markdown("""
    **ℹ️ Anleitung:**
    1. Startkapital eingeben
    2. Laufzeit in Tagen wählen
    3. Täglichen Zinssatz anpassen
    4. Reinvestition aktivieren/deaktivieren
    """)
    st.image("https://via.placeholder.com/150", width=150)  # Platzhalter für Logo