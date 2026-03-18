import streamlit as st
import pandas as pd
import os

# Datei-Einstellungen
DB_FILE = "mein_vorrat.csv"

# Hilfsfunktionen zum Laden und Speichern
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE).to_dict('records')
    return []

def save_data(data):
    pd.DataFrame(data).to_csv(DB_FILE, index=False)

# Initialisierung
if 'inventory' not in st.session_state:
    st.session_state.inventory = load_data()

st.title("🍎 Mein smarter Vorrat")

# --- TEIL 1: Eingabe ---
with st.expander("➕ Neues Produkt hinzufügen"):
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Name (z.B. Milch)")
        col_a, col_b = st.columns(2)
        qty = col_a.number_input("Menge", min_value=0, value=1)
        unit = col_b.selectbox("Einheit", ["Stk", "g", "kg", "L", "Pkg"])
        limit = st.number_input("Mindestmenge", min_value=0, value=1)
        
        if st.form_submit_button("Hinzufügen"):
            if name:
                st.session_state.inventory.append({
                    "Produkt": name, "Menge": qty, 
                    "Einheit": unit, "Limit": limit
                })
                save_data(st.session_state.inventory)
                st.rerun()

# --- TEIL 2: Liste & Steuerung ---
st.subheader("Aktueller Bestand")

for i, item in enumerate(st.session_state.inventory):
    # Container für saubere Optik
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        
        with c1:
            # Optische Warnung bei niedrigem Bestand
            if item['Menge'] <= item['Limit']:
                st.error(f"**{item['Produkt']}**")
            else:
                st.write(f"**{item['Produkt']}**")
            st.caption(f"{item['Menge']} {item['Einheit']} im Haus")

        with c2:
            if st.button("➖", key=f"min_{i}"):
                if st.session_state.inventory[i]['Menge'] > 0:
                    st.session_state.inventory[i]['Menge'] -= 1
                    save_data(st.session_state.inventory)
                    st.rerun()
        
        with c3:
            if st.button("➕", key=f"plus_{i}"):
                st.session_state.inventory[i]['Menge'] += 1
                save_data(st.session_state.inventory)
                st.rerun()

        with c4:
            if st.button("🗑️", key=f"del_{i}"):
                st.session_state.inventory.pop(i)
                save_data(st.session_state.inventory)
                st.rerun()

# --- TEIL 3: Einkaufsliste ---
st.divider()
shopping_list = [i['Produkt'] for i in st.session_state.inventory if i['Menge'] <= i['Limit']]

if shopping_list:
    st.subheader("🛒 Dringend kaufen:")
    for shop_item in shopping_list:
        st.write(f"- {shop_item}")
