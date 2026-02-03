import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Firemní STK hlídač", layout="centered")

st.title("🚗 Firemní evidence STK")

# Připojení ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Načtení dat s ošetřením chyb
try:
    df = conn.read()
    # Pokud je tabulka úplně prázdná, vytvoříme základní sloupce
    if df.empty or 'Datum_STK' not in df.columns:
        df = pd.DataFrame(columns=['SPZ', 'Vozidlo', 'Datum_STK'])
except Exception:
    df = pd.DataFrame(columns=['SPZ', 'Vozidlo', 'Datum_STK'])

# Převod datumu na formát, kterému Python rozumí
df['Datum_STK'] = pd.to_datetime(df['Datum_STK'], errors='coerce')

# --- UPOZORNĚNÍ ---
st.subheader("🔔 Aktuální termíny")
dnes = datetime.now()

# Filtrujeme auta, co mají STK tento měsíc a rok
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
    with st.form("stk_form", clear_on_submit=True):
        spz = st.text_input("SPZ")
        model = st.text_input("Název vozidla")
        datum = st.date_input("Datum příští STK")
        submit = st.form_submit_button("Uložit do systému")
        
        if submit and spz:
            new_row = pd.DataFrame([{"SPZ": spz, "Vozidlo": model, "Datum_STK": datum.strftime('%Y-%m-%d')}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("Uloženo! Stránka se za chvíli aktualizuje.")
            st.rerun()

# --- PŘEHLED ---
st.subheader("📋 Kompletní seznam")
# Formátujeme datum pro lidské oko v tabulce
display_df = df.copy()
display_df['Datum_STK'] = display_df['Datum_STK'].dt.strftime('%d.%m.%Y')
st.dataframe(display_df, use_container_width=True)
