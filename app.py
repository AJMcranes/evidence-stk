import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Firemní STK hlídač", layout="centered")

st.title("🚗 Firemní evidence STK")
st.info("Data jsou synchronizována s Google Tabulkou.")

# Připojení ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Načtení dat
df = conn.read()

# --- UPOZORNĚNÍ ---
st.subheader("🔔 Aktuální termíny")
dnes = datetime.now()
df['Datum_STK'] = pd.to_datetime(df['Datum_STK'])

# Hledáme STK v tomto měsíci
blizka_stk = df[
    (df['Datum_STK'].dt.month == dnes.month) & 
    (df['Datum_STK'].dt.year == dnes.year)
]

if not blizka_stk.empty:
    for _, auto in blizka_stk.iterrows():
        st.warning(f"⚠️ VOZIDLO {auto['SPZ']} ({auto['Vozidlo']}) má termín v tomto měsíci!")
else:
    st.success("Tento měsíc žádná vozidla nemusí na kontrolu.")

# --- PŘIDÁVÁNÍ ---
with st.expander("➕ Přidat nové vozidlo"):
    with st.form("stk_form"):
        spz = st.text_input("SPZ")
        model = st.text_input("Název vozidla")
        datum = st.date_input("Datum příští STK")
        submit = st.form_submit_button("Uložit do systému")
        
        if submit:
            # Tady se kód postará o zápis do Google Tabulky
            new_row = pd.DataFrame([{"SPZ": spz, "Vozidlo": model, "Datum_STK": datum.strftime('%Y-%m-%d')}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("Uloženo! Tabulka se aktualizuje.")
            st.rerun()

# --- PŘEHLED ---
st.subheader("📋 Kompletní seznam")
st.dataframe(df)
