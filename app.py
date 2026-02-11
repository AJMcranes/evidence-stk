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
    # Načteme PRVNÍ list tabulky (bez uvedení názvu, aby nebyla chyba 400)
    df = conn.read(ttl=0)
    
    # Odstraníme úplně prázdné řádky
    df = df.dropna(how='all')
    
    if df is not None and not df.empty:
        # Přejmenujeme sloupce pro vnitřní potřebu (0:Čas, 1:SPZ, 2:Vozidlo, 3:Datum STK)
        # Použijeme iloc, aby nás nezajímalo, jak se sloupce jmenují v tabulce
        df.columns = [f"col_{i}" for i in range(len(df.columns))]
        
        # Převod sloupce s datem (index 3)
        df['col_3'] = pd.to_datetime(df['col_3'], dayfirst=True, errors='coerce')
        
        dnes = datetime.now()
        
        # --- KONTROLA TERMÍNŮ STK ---
        stk_tento_mesic = df[
            (df['col_3'].dt.month == dnes.month) & 
            (df['col_3'].dt.year == dnes.year)
        ]
        
        if not stk_tento_mesic.empty:
            st.error(f"⚠️ **POZOR:** V tomto měsíci ({dnes.strftime('%m/%Y')}) končí STK u těchto aut:")
            for _, auto in stk_tento_mesic.iterrows():
                st.write(f"👉 **{auto['col_1']}** — {auto['col_2']}")
        else:
            st.success("✅ Pro tento měsíc jsou všechna auta v pořádku.")

        # --- ZOBRAZENÍ TABULKY ---
        st.divider()
        st.subheader("📋 Kompletní seznam vozidel")
        
        display_df = df.iloc[:, [1, 2, 3]].copy()
        display_df.columns = ['SPZ', 'Vozidlo', 'Datum příští STK']
        display_df['Datum příští STK'] = display_df['Datum příští STK'].dt.strftime('%d.%m.%Y')
        
        st.dataframe(display_df, use_container_width=True)
        
    else:
        st.warning("⚠️ Tabulka je prázdná nebo nebyla nalezena data.")

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
