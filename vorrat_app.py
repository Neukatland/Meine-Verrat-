import streamlit as st
import pandas as pd
import os

# Datei-Einstellungen
DB_FILE = "vorrat_final.csv"

def daten_laden():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Artikel", "Menge", "Einheit", "Ort", "Warnmenge"])

def daten_speichern(df):
    df.to_csv(DB_FILE, index=False)

st.set_page_config(page_title="Mein Vorrat", page_icon="🍎")
st.title("🍎 Mein smarter Vorrat")

df = daten_laden()

# Navigation (Tabs)
tab1, tab2 = st.tabs(["📦 Bestand", "🛒 Einkaufsliste"])

with tab1:
    # 1. Eingabe-Bereich
    with st.expander("➕ Neues Produkt hinzufügen"):
        name = st.text_input("Name (z.B. Milch)")
        col1, col2 = st.columns(2)
        with col1:
            menge = st.number_input("Aktuelle Menge", min_value=0, step=1, value=1)
        with col2:
            einheit = st.selectbox("Einheit", ["Stk", "0,5L Flasche", "1,5L Flasche", "Pkg", "g", "kg", "L"])
        
        warnmenge = st.number_input("Warnen ab Menge:", min_value=0, step=1, value=2)
        ort = st.selectbox("Lagerort", ["Kühlschrank", "Küchenschrank", "Keller", "Gefrierfach"])
        
        if st.button("Speichern"):
            if name:
                neue_zeile = pd.DataFrame([{"Artikel": name, "Menge": menge, "Einheit": einheit, "Ort": ort, "Warnmenge": warnmenge}])
                df = pd.concat([df, neue_zeile], ignore_index=True)
                daten_speichern(df)
                st.success(f"{name} gespeichert!")
                st.rerun()

    st.divider()

    # 2. Anzeige des Bestands
    if not df.empty:
        for index, row in df.iterrows():
            ist_kritisch = row['Menge'] <= row['Warnmenge']
            with st.container():
                if ist_kritisch:
                    st.error(f"⚠️ **{row['Artikel']}** ({row['Menge']} {row['Einheit']} im {row['Ort']})")
                else:
                    st.success(f"✅ **{row['Artikel']}**: {row['Menge']} {row['Einheit']} ({row['Ort']})")
                
                c1, c2, c3 = st.columns([1,1,4])
                if c1.button("−", key=f"m_{index}"):
                    if df.at[index, 'Menge'] > 0:
                        df.at[index, 'Menge'] -= 1
                        daten_speichern(df)
                        st.rerun()
                if c2.button("+", key=f"p_{index}"):
                    df.at[index, 'Menge'] += 1
                    daten_speichern(df)
                    st.rerun()
                if c3.button("🗑️", key=f"d_{index}"):
                    df = df.drop(index)
                    daten_speichern(df)
                    st.rerun()
                st.divider()
    else:
        st.info("Noch keine Vorräte eingetragen.")

with tab2:
    st.subheader("🛒 Was du bald kaufen musst")
    # Filtere alle Artikel, die nachgekauft werden müssen
    nachkauf_liste = df[df['Menge'] <= df['Warnmenge']]
    
    if not nachkauf_liste.empty:
        for _, row in nachkauf_liste.iterrows():
            st.warning(f"👉 **{row['Artikel']}** (Aktuell: {row['Menge']} {row['Einheit']})")
        
        if st.button("Als Text für WhatsApp kopieren"):
            einkauf_text = "Einkaufsliste:\n" + "\n".join([f"- {r['Artikel']}" for _, r in nachkauf_liste.iterrows()])
            st.code(einkauf_text)
    else:
        st.balloons()
        st.success("Alles auf Vorrat! Du musst aktuell nichts einkaufen.")
