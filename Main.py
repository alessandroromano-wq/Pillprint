import streamlit as st
from datetime import date, timedelta
import csv
import requests
from io import StringIO
import streamlit.components.v1 as components

st.set_page_config(page_title="PillPrint Pro", layout="wide")

# --- CONFIGURAZIONE GOOGLE SHEETS (VERSIONE EXPORT) ---
SHEET_ID = "106bwDrvfYDeb_mgNgorAcCQZQzwPeXk8vzp3j6hJVC8"
# URL ottimizzato per esportazione CSV diretta senza autenticazione pesante
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=300) # Cache di 5 minuti
def load_presets_fast():
    try:
        response = requests.get(URL)
        response.raise_for_status() # Controlla se ci sono errori HTTP
        f = StringIO(response.text)
        reader = csv.DictReader(f)
        data = list(reader)
        return data
    except Exception as e:
        st.error(f"Errore di connessione a Google Sheets: {e}")
        return []

# --- STATO SESSIONE ---
if 'meds' not in st.session_state: st.session_state.meds = []

# --- TRADUZIONI ---
LANGS = {
    "Italiano": {"title": "SCHEMA TERAPEUTICO", "pat": "Paziente", "date": "Data", "med": "Farmaco", "dose": "Dose", "m": "Mattina", "p": "Pomeriggio", "s": "Sera", "n": "Notte", "inst": "Istruzioni", "need": "AL BISOGNO", "max": "Max volte/die", "time": "Ora", "sig": "Firma e Timbro", "btn": "STAMPA PDF", "duration": "Durata (gg)", "end": "Fine", "save_pre": "Salva Preset", "use_pre": "I TUOI PRESET", "symptom": "Sintomo"},
    "English": {"title": "MEDICATION SCHEDULE", "pat": "Patient", "date": "Date", "med": "Medication", "dose": "Dose", "m": "Morning", "p": "Afternoon", "s": "Evening", "n": "Night", "inst": "Instructions", "need": "AS NEEDED", "max": "Max/day", "time": "Time", "sig": "Signature", "btn": "PRINT PDF", "duration": "Days", "end": "Ends", "save_pre": "Save Preset", "use_pre": "YOUR PRESETS", "symptom": "Symptom"}
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    choice = st.selectbox("Lingua", list(LANGS.keys()))
    t = LANGS[choice]
    p_name = st.text_input(t["pat"], "Paziente")
    p_date = st.date_input(t["date"], date.today())
    
    st.divider()
    if st.button("🔄 Aggiorna Preset"):
        st.cache_data.clear()
        st.rerun()

    st.subheader(f"🚀 {t['use_pre']}")
    presets = load_presets_fast()
    
    if presets:
        for row in presets:
            # Controllo che la riga non sia vuota e abbia il nome del preset
            p_name_label = row.get('preset_name') or row.get('name')
            if p_name_label:
                if st.button(f"➕ {p_name_label}", use_container_width=True):
                    # Logica conversione dati dal CSV (stringhe -> booleani/int)
                    d_gg = int(row.get('days', 0)) if row.get('days') else 0
                    end_d = (date.today() + timedelta(days=d_gg)).strftime("%d/%m/%Y") if d_gg > 0 else None
                    
                    st.session_state.meds.append({
                        "nome": row.get('med_name', 'Farmaco'),
                        "dose": f"{row.get('dose', '')} {row.get('unit', '')}",
                        "forma": row.get('shape', '💊'),
                        "m": "X" if str(row.get('m')).lower() in ['true', '1', 'x'] else "",
                        "p": "X" if str(row.get('p')).lower() in ['true', '1', 'x'] else "",
                        "s": "X" if str(row.get('s')).lower() in ['true', '1', 'x'] else "",
                        "n": "X" if str(row.get('n')).lower() in ['true', '1', 'x'] else "",
                        "need": str(row.get('need')).lower() in ['true', '1', 'x'],
                        "max": row.get('max', 0),
                        "sy": row.get('symptom', ''),
                        "hr": row.get('hour', ''),
                        "nt": row.get('note', ''),
                        "end": end_d
                    })
                    st.rerun()
    
    if st.button("🗑️ Reset Lista", use_container_width=True):
        st.session_state.meds = []; st.rerun()

# --- INTERFACCIA PRINCIPALE ---
with st.expander("➕ Aggiungi Farmaco Manualmente", expanded=not st.session_state.meds):
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        f_n = c1.text_input(t["med"])
        f_d = c2.number_input(t["duration"], 0, 365, 0)
        
        r2 = st.columns([1, 1, 2])
        f_ds, f_un = r2[0].text_input(t["dose"]), r2[1].selectbox("Unità", ["mg", "ml", "gocce", "cpr", "bustine", "UI"])
        f_sh = r2[2].radio("Forma", ["💊", "⚪", "💧", "🥄", "💉"], horizontal=True)
        
        st.write(f"**Orari**")
        t_cols = st.columns(4)
        v_m, v_p, v_s, v_n = t_cols[0].checkbox(t["m"]), t_cols[1].checkbox(t["p"]), t_cols[2].checkbox(t["s"]), t_cols[3].checkbox(t["n"])
        
        st.divider()
        e_cols = st.columns([1, 1, 2])
        v_an, v_mx, v_sy = e_cols[0].checkbox(t["need"]), e_cols[1].number_input(t["max"], 0, 12, 0), e_cols[2].text_input(t["symptom"])
        v_hr, v_nt = st.columns(2)[0].text_input(t["time"]), st.columns(2)[1].text_input(t["inst"])
        
        if st.form_submit_button("Aggiungi alla lista"):
            if f_n:
                dt_e = (date.today() + timedelta(days=f_d)).strftime("%d/%m/%Y") if f_d > 0 else None
                st.session_state.meds.append({"nome": f_n, "dose": f"{f_ds} {f_un}", "forma": f_sh, "m": "X" if v_m else "", "p": "X" if v_p else "", "s": "X" if v_s else "", "n": "X" if v_n else "", "need": v_an, "max": v_mx, "sy": v_sy, "hr": v_hr, "nt": v_nt, "end": dt_e})
                st.rerun()

# --- GENERAZIONE TABELLA ---
if st.session_state.meds:
    if st.button(t["btn"], type="primary", use_container_width=True):
        components.html("<script>window.print();</script>", height=0)

    h = "<style>.tab{width:100%;border-collapse:collapse;border:2px solid black;font-family:sans-serif;color:black;}.tab th{background:#f2f2f2;border:1px solid black;padding:8px;font-size:11px;}.tab td{border:1px solid black;padding:10px;text-align:center;}.nb{background:#fff0f0;color:red;border:1px dashed red;padding:5px;font-weight:bold;}</style>"
    h += f"<div style='background:white;padding:20px;'><h2 style='text-align:center;margin:0;'>{t['title']}</h2>"
    h += f"<p style='text-align:center;'><b>{t['pat']}:</b> {p_name} | <b>{t['date']}:</b> {p_date.strftime('%d/%m/%Y')}</p>"
    h += f"<table class='tab'><thead><tr><th>{t['med']}</th><th>{t['m']}☀️</th><th>{t['p']}🌤️</th><th>{t['s']}🌅</th><th>{t['n']}🌙</th><th>{t['inst']}</th></tr></thead><tbody>"

    for m in st.session_state.meds:
        fine = f"<br><small style='color:red;'>⌛{t['end']}: {m['end']}</small>" if m['end'] else ""
        h += "<tr>"
        h += f"<td style='text-align:left;width:25%;'><span style='font-size:25px;'>{m['forma']}</span> <b>{m['nome']}</b><br><small>{m['dose']}</small>{fine}</td>"
        
        if m['need']:
            txt = f"{t['need']}"
            if int(m['max']) > 0: txt += f" (max {m['max']} v/die)"
            if m['sy']: txt += f"<br><i>{m['sy']}</i>"
            h += f"<td colspan='4'><div class='nb'>{txt}</div></td>"
        else:
            h += f"<td>{m['m']}</td><td>{m['p']}</td><td>{m['s']}</td><td>{m['n']}</td>"

        notes = ""
        if m['hr']: notes += f"🕒 <b>{m['hr']}</b><br>"
        if m['nt']: notes += m['nt']
        h += f"<td style='text-align:left;font-size:11px;width:25%;'>{notes}</td></tr>"

    h += "</tbody></table></div>"
    st.markdown(h, unsafe_allow_html=True)
