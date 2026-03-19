import streamlit as st
import pandas as pd
import os

# Datei-Einstellungen
DB_FILE = "mein_vorrat.csv"

def daten_laden():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Artikel", "Menge", "Einheit", "Ort", "Mindestmenge"])

def daten_speichern(df):
    df.to_csv(DB_FILE, index=False)

st.set_page_config(page_title="Mein smarter Vorrat", page_icon="🍎")
st.title("🍎 Mein smarter Vorrat")

df = daten_laden()

# 1. Eingabe-Bereich
with st.expander("➕ Neues Produkt hinzufügen", expanded=False):
    name = st.text_input("Name (z.B. Milch)")
    
    col1, col2 = st.columns(2)
    with col1:
        menge = st.number_input("Aktuelle Menge", min_value=0, step=1)
    with col2:
        einheit = st.selectbox("Einheit", ["Stk", "0,5L Flasche", "0,75L Flasche", "1,0L Flasche", "1,5L Flasche", "Pkg", "g", "kg", "L"])
    
    # NEU: Hier stellst du ein, ab wann gewarnt wird
    mindestmenge = st.number_input("Warnen, wenn Menge kleiner oder gleich:", min_value=0, value=2, step=1)
    
    ort = st.selectbox("Wo wird es aufbewahrt?", ["Kühlschrank", "Küchenschrank", "Keller", "Gefrierfach", "Vorratskammer"])
    
    if st.button("Speichern"):
        if name:
            neue_zeile = pd.DataFrame([{"Artikel": name, "Menge": menge, "Einheit": einheit, "Ort": ort, "Mindestmenge": mindestmenge}])
            df = pd.concat([df, neue_zeile], ignore_index=True)
            daten_speichern(df)
            st.success(f"{name} wurde gespeichert!")
            st.rerun()

st.divider()

# 2. Anzeige des Bestands
st.subheader("📦 Aktueller Bestand")

if not df.empty:
    for index, row in df.iterrows():
        # Prüfen, ob nachgekauft werden muss
        muss_nachkaufen = row['Menge'] <= row['Mindestmenge']
        
        with st.container():
            # Wenn zu wenig da ist, machen wir eine rote Warnung
            if muss_nachkaufen:
                st.error(f"⚠️ **{row['Artikel']}** nachkaufen! (Nur noch {row['Menge']} {row['Einheit']} im {row['Ort']})")
            else:
                st.write(f"✅ **{row['Artikel']}**: {row['Menge']} {row['Einheit']} ({row['Ort']})")
            
            c1, c2, c3 = st.columns([1,1,5])
            if c1.button("−", key=f"min_{index}"):
                if df.at[index, 'Menge'] > 0:
                    df.at[index, 'Menge'] -= 1
                    daten_speichern(df)
                    st.rerun()
            if c2.button("+", key=f"plu_{index}"):
                df.at[index, 'Menge'] += 1
                daten_speichern(df)
                st.rerun()
            if c3.button("🗑️", key=f"del_{index}"):
                df = df.drop(index)
                daten_speichern(df)
                st.rerun()
            st.divider()
else:
    st.info("Dein Vorrat ist aktuell leer.")
