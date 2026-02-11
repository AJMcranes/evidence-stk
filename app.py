import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Nastavení stránky
st.set_page_config(page_title="Evidence STK", layout="wide")

st.title("🚗 Firemní evidence STK")

# Připojení ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# ODKAZ NA FORMULÁŘ
ODKAZ_NA_FORMULAR = "https://forms.gle/xSDhpAeK5ZC83DEZ6"

# --- HLAVNÍ ČÁST: NAČTENÍ A ZOBRAZENÍ ---
try:
    # ttl=0 zajistí, že při každém Refresh (F5) uvidíš nová data
    # Načítáme první list tabulky (Data)
    df = conn.read(worksheet="Data", ttl=0)
    
    # Odstraníme úplně prázdné řádky, pokud v tabulce jsou
    df = df.dropna(how='all')
    
    if df is not None and not df.empty:
        # --- KONTROLA TERMÍNŮ STK ---
        # Předpokládáme pořadí sloupců: 0:Čas, 1:SPZ, 2:Vozidlo, 3:Datum STK
        # Převedeme sloupec s datem na formát, kterému Python rozumí
        datum_sloupec = df.columns[3]
        df[datum_sloupec] = pd.to_datetime(df[datum_sloupec], errors='coerce')
        
        dnes = datetime.now()
        
        # Vyfiltrujeme auta, která mají STK v aktuálním měsíci a roce
        stk_tento_mesic = df[
            (df[datum_sloupec].dt.month == dnes.month) & 
            (df[datum_sloupec].dt.year == dnes.year)
        ]
        
        if not stk_tento_mesic.empty:
            st.error(f"⚠️ **POZOR:** V tomto měsíci ({dnes.strftime('%m/%Y')}) končí STK u těchto aut:")
            for _, auto in stk_tento_mesic.iterrows():
                st.write(f"👉 **{auto[df.columns[1]]}** — {auto[df.columns[2]]}")
        else:
            st.success("✅ Pro tento měsíc jsou všechna auta v pořádku.")

        # --- ZOBRAZENÍ TABULKY ---
        st.divider()
        st.subheader("📋 Kompletní seznam vozidel")
        
        # Vytvoříme kopii pro hezké zobrazení (jen důležité sloupce a čitelný formát data)
        display_df = df.iloc[:, [1, 2, 3]].copy() # Vezme sloupce SPZ, Vozidlo, Datum STK
        display_df.columns = ['SPZ', 'Vozidlo', 'Datum příští STK']
        display_df['Datum příští STK'] = display_df['Datum příští STK'].dt.strftime('%d.%m.%Y')
        
        st.dataframe(display_df, use_container_width=True)
        
    else:
        st.warning("⚠️ Tabulka je prázdná. Přidejte první vozidlo přes formulář.")

except Exception as e:
    st.error("❌ Chyba při načítání dat.")
    st.info(f"Technický detail: {e}")

# --- TLAČÍTKA ---
st.divider()
st.subheader("➕ Akce")
col1, col2 = st.columns(2)
with col1:
    st.link_button("📝 Přidat nové vozidlo", ODKAZ_NA_FORMULAR)
with col2:
    if st.button("🔄 Aktualizovat data (Refresh)"):
        st.rerun()
