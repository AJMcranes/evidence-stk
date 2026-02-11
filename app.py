import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Nastavení stránky
st.set_page_config(page_title="Evidence STK a YouTube", layout="wide")

st.title("📊 Centrální evidence")

# Připojení ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# ODKAZ NA FORMULÁŘ (Ten svůj tam nechej)
ODKAZ_NA_FORMULAR = "https://forms.gle/xSDhpAeK5ZC83DEZ6"

# --- HLAVNÍ ČÁST: NAČTENÍ A ZOBRAZENÍ ---
try:
    # ttl=0 zajistí, že při každém Refresh (F5) uvidíš nová data
    # POZOR: Tady musí být název listu přesně podle tabulky!
    df = conn.read(ttl=0)
    
    if df is not None and not df.empty:
        st.success("✅ Data úspěšně načtena z Google Sheets")
        
        # Zobrazení tabulky
        st.subheader("📋 Aktuální záznamy v tabulce")
        st.dataframe(df, use_container_width=True)
        
        # Malý bonus: Pokud už tam máš sloupec s penězi, tady ho uvidíš
        st.info("💡 Pokud v tabulce vidíš svá data, spojení funguje perfektně!")
        
    else:
        st.warning("⚠️ Tabulka byla nalezena, ale zdá se, že v ní nejsou žádná data. Zkus vyplnit formulář.")

except Exception as e:
    st.error("❌ Aplikace se nemůže spojit s konkrétním listem v tabulce.")
    st.write(f"Zkontroluj, zda se list v Google tabulce jmenuje přesně: **Form_Responses**")
    st.info(f"Technická chyba pro kontrolu: {e}")

# --- TLAČÍTKA ---
st.divider()
st.subheader("➕ Akce")
col1, col2 = st.columns(2)
with col1:
    st.link_button("📝 Otevřít formulář (Přidat auto/příjem)", ODKAZ_NA_FORMULAR)
with col2:
    if st.button("🔄 Aktualizovat data (Refresh)"):
        st.rerun()
