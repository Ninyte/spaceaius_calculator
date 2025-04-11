import streamlit as st
import datetime
from io import StringIO
import pandas as pd

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
    development_df = pd.DataFrame(
        development,
        columns=["Tag", "Kapital", "Zwischensumme", "Reinvestiert"]
    ).astype({
        "Tag": "int32",
        "Kapital": "float64",
        "Zwischensumme": "float64",
        "Reinvestiert": "bool"
    })
    
    return development_df, capital, intermediate_sum

# --- Streamlit UI ---
st.set_page_config(page_title="SpaceAI Rechner", layout="centered")
st.title("🚀 SpaceAI Kapitalrechner")

# Eingabefelder
col1, col2 = st.columns(2)
initial_capital = col1.number_input("Startkapital ($)", min_value=0.0, value=950.0)
days = col2.number_input("Anzahl Tage", min_value=1, value=90)

daily_interest = st.slider("Durchschnittlicher täglicher Gewinn (%)", min_value=0.4, max_value=2.7, value=0.8, step=0.1)
reinvest = st.checkbox("Reinvestieren (je ab 50$ Zwischensumme)", value=True)

# Berechnung starten
if st.button("Berechnen", type="primary"):
    development_df, final_capital, remaining = calculate_profit(
        initial_capital, days, daily_interest, reinvest
    )

    # Ergebnisse anzeigen
    st.success(f"**Endkapital nach {days} Tagen:** {final_capital:.2f} $")
    st.info(f"**Verbleibende Zwischensumme:** {remaining:.2f} $")

    # Detailtabelle (nur erste 5 + letzte 5 Tage zeigen)
    #with st.expander("📈 Detailierte Kapitalentwicklung"):
    #    if len(development_df) > 10:
    #        st.table(pd.concat([development_df.head(5), development_df.tail(5)]))
    #    else:
    #        st.table(development_df)

    with st.expander("📈 Detailierte Kapitalentwicklung", expanded=False):  # expanded=False = Standardmäßig eingeklappt
        st.dataframe(development_df)  # Zeigt das gesamte DataFrame an
        
        # Optional: Styling für bessere Lesbarkeit
        st.caption("ℹ️ Scrollen, um alle Einträge zu sehen")

    # Download-Button für komplette Daten
    output = StringIO()
    output.write(f"Startkapital: {initial_capital} $\nTage: {days}\nZinssatz: {daily_interest} %\n\n")
    output.write("Tag | Kapital | Zwischensumme | Reinvestiert\n")
    output.write("-" * 40 + "\n")
    for _, row in development_df.iterrows():
        output.write(f"{row['Tag']} | {row['Kapital']:.2f} $ | {row['Zwischensumme']:.2f} $ | {'✅' if row['Reinvestiert'] else '❌'}\n")

    st.download_button(
        label="📥 Ergebnisse speichern",
        data=output.getvalue(),
        file_name=f"{DEFAULT_FILENAME}_{datetime.date.today().strftime('%Y-%m-%d')}.txt",
        mime="text/plain"
    )

# Sidebar mit Infos
with st.sidebar:
    # Logo mit Link über der Anleitung
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 40px;">
            <a href="https://app.spaceaius.com/#/pages/login/login?invitationCode=7765924035" target="_blank">
                <img src="https://app.spaceaius.com/static/login/title.png" width="150">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("""
    **ℹ️ Anleitung:**
    1. Startkapital in $ eingeben
    2. Laufzeit in Tagen wählen
    3. Täglichen Zinssatz anpassen
    4. Reinvestition aktivieren/deaktivieren
    5. **Eigene Gewinne generieren:** 
        - Klicke auf das SpaceAI-Logo und melde dich jetzt an!
    """)