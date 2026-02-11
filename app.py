import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- KONFIGURACE ---
# !!! SEM VLOŽ ODKAZ NA SVŮJ GOOGLE FORMULÁŘ !!!
ODKAZ_NA_FORMULAR = "https://forms.gle/fbfP7nSosXRdyEQBA"

st.set_page_config(page_title="Firemní STK hlídač", layout="centered")

st.title("🚗 Firemní evidence STK")

# Připojení ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Načtení dat z listu "Odpovědi formuláře 1" (vytvoří ho Google Form automaticky)
try:
    # Pokud jsi formulář už propojil, list se jmenuje takto:
    df = conn.read(worksheet="Odpovědi formuláře 1")
    
    # Přejmenování sloupců z formuláře na krátké názvy pro kód
    # Předpokládám pořadí: Časové razítko, SPZ, Vozidlo, Datum STK
    df.columns = ['Cas', 'SPZ', 'Vozidlo', 'Datum_STK']
except Exception:
    st.info("Zatím nejsou k dispozici žádná data z formuláře.")
    df = pd.DataFrame(columns=['Cas', 'SPZ', 'Vozidlo', 'Datum_STK'])

# Převod datumu na formát, kterému Python rozumí
df['Datum_STK'] = pd.to_datetime(df['Datum_STK'], errors='coerce')

# --- UPOZORNĚNÍ ---
st.subheader("🔔 Upozornění na tento měsíc")
dnes = datetime.now()

# Filtrujeme auta, co mají STK tento měsíc a rok
blizka_stk = df[
    (df['Datum_STK'].dt.month == dnes.month) & 
    (df['Datum_STK'].dt.year == dnes.year)
]

if not blizka_stk.empty:
    for _, auto in blizka_stk.iterrows():
        st.warning(f"⚠️ VOZIDLO **{auto['SPZ']}** ({auto['Vozidlo']}) má termín STK v tomto měsíci!")
else:
    st.success("Tento měsíc jsou všechna vozidla v pořádku.")

# --- PŘIDÁVÁNÍ (Tlačítko na formulář) ---
st.markdown("---")
st.subheader("➕ Nový záznam")
st.write("Pro přidání auta nebo příjmu klikněte na tlačítko a vyplňte formulář:")
st.link_button("Otevřít formulář pro zadání", ODKAZ_NA_FORMULAR)

# --- PŘEHLED ---
st.markdown("---")
st.subheader("📋 Kompletní seznam vozidel")

# Úprava tabulky pro hezké zobrazení
if not df.empty:
    display_df = df.copy()
    # Zobrazíme jen důležité sloupce a zformátujeme datum
    display_df = display_df[['SPZ', 'Vozidlo', 'Datum_STK']]
    display_df['Datum_STK'] = display_df['Datum_STK'].dt.strftime('%d.%m.%Y')
    st.dataframe(display_df, use_container_width=True)
