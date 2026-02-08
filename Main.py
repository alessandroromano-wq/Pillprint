import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, timedelta
import json

# Configurazione Pagina
st.set_page_config(page_title="PillPrint Pro", layout="wide")

# --- CONNESSIONE GOOGLE SHEETS ---
# URL del tuo file specifico
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/106bwDrvfYDeb_mgNgorAcCQZQzwPeXk8vzp3j6hJVC8/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_presets():
    try:
        # Carica i dati dal foglio 'presets'
        df = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="presets", ttl="0")
        return df
    except Exception as e:
        st.error(f"Errore caricamento preset: {e}")
        return pd.DataFrame()

def save_preset_to_sheets(new_row):
    try:
        existing_df = load_presets()
        # Se il foglio è vuoto o ha solo intestazioni
        if existing_df.empty:
            updated_df = pd.DataFrame([new_row])
        else:
            updated_df = pd.concat([existing_df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Scrive l'intero dataframe aggiornato sul foglio
        conn.update(spreadsheet=SPREADSHEET_URL, worksheet="presets", data=updated_df)
        st.cache_data.clear() # Forza il ricaricamento dei dati
        return True
    except Exception as e:
        st.error(f"Errore nel salvataggio: {e}")
        return False

# --- STATO SESSIONE ---
if 'meds' not in st.session_state: st.session_state.meds = []

# --- TRADUZIONI (10 LINGUE) ---
LANGS = {
    "Italiano": {
        "title": "SCHEMA TERAPEUTICO", "pat": "Paziente", "date": "Data", "med": "Farmaco", "dose": "Dose",
        "m": "Mattina", "p": "Pomeriggio", "s": "Sera", "n": "Notte", "inst": "Istruzioni", 
        "need": "AL BISOGNO", "max": "Max volte/die", "time": "Ora", "sig": "Firma e Timbro", 
        "btn": "STAMPA PDF", "duration": "Durata (gg)", "end": "Fine", "save_pre": "Salva Preset", "use_pre": "I TUOI PRESET",
        "symptom": "Sintomo (es. febbre)"
    },
    "English": {"title": "MEDICATION SCHEDULE", "pat": "Patient", "date": "Date", "med": "Medication", "dose": "Dose", "m": "Morning", "p": "Afternoon", "s": "Evening", "n": "Night", "inst": "Instructions", "need": "AS NEEDED", "max": "Max/day", "time": "Time", "sig": "Signature", "btn": "PRINT PDF", "duration": "Days", "end": "Ends", "save_pre": "Save Preset", "use_pre": "YOUR PRESETS", "symptom": "Symptom"},
    "Română": {"title": "SCHEMA TERAPEUTICĂ", "pat": "Pacient", "date": "Data", "med": "Medicament", "dose": "Doză", "m": "Dimineața", "p": "După-amiaza", "s": "Seara", "n": "Noaptea", "inst": "Instrucțiuni", "need": "LA NEVOIE", "max": "Max ori/zi", "time": "Ora", "sig": "Parafă", "btn": "IMPRIMĂ PDF", "duration": "Zile", "end": "Sfârșit", "save_pre": "Salvează", "use_pre": "PRESETĂRI", "symptom": "Simptom"},
    "العربية": {"title": "جدول العلاج", "pat": "المريض", "date": "التاريخ", "med": "الدواء", "dose": "الجرعة", "m": "صباحاً", "p": "بعد الظهر", "s": "مساًء", "n": "ليلاً", "inst": "تعليمات", "need": "عند الحاجة", "max": "أقصى عدد", "time": "الوقت", "sig": "التوقيع", "btn": "طباعة", "duration": "المدة", "end": "النهاية", "save_pre": "حفظ", "use_pre": "الإعدادات", "symptom": "الأعراض"},
    "Shqip": {"title": "SKEMA TERAPEUTIKE", "pat": "Pacienti", "date": "Data", "med": "Barërat", "dose": "Doza", "m": "Mëngjes", "p": "Pasdite", "s": "Mbrëmje", "n": "Natë", "inst": "Udhëzime", "need": "SIPAS NEVOJËS", "max": "Max herë", "time": "Ora", "sig": "Firma", "btn": "PRINT", "duration": "Ditë", "end": "Mbarimi", "save_pre": "Ruaj", "use_pre": "PRESETET", "symptom": "Simptoma"},
    "Español": {"title": "ESQUEMA TERAPÉUTICO", "pat": "Paciente", "date": "Fecha", "med": "Medicamento", "dose": "Dosis", "m": "Mañana", "p": "Tarde", "s": "Noche", "n": "Madrugada", "inst": "Instrucciones", "need": "SI ES NECESARIO", "max": "Max/día", "time": "Hora", "sig": "Firma", "btn": "IMPRIMIR", "duration": "Días", "end": "Fin", "save_pre": "Guardar", "use_pre": "MIS PRESETS", "symptom": "Síntoma"},
    "中文": {"title": "治疗方案", "pat": "患者", "date": "日期", "med": "药物", "dose": "剂量", "m": "早上", "p": "下午", "s": "晚上", "n": "夜间", "inst": "指示", "need": "必要时", "max": "每日最多", "time": "时间", "sig": "签名", "btn": "打印", "duration": "天数", "end": "结束", "save_pre": "保存", "use_pre": "预设", "symptom": "症状"},
    "Українська": {"title": "СХЕМА ЛІКУВАННЯ", "pat": "Пацієнт", "date": "Дата", "med": "Препарат", "dose": "Доза", "m": "Ранок", "p": "День", "s": "Вечір", "n": "Ніч", "inst": "Інструкції", "need": "ЗА ПОТРЕБИ", "max": "Макс/день", "time": "Час", "sig": "Підпис", "btn": "ДРУК", "duration": "Днів", "end": "Кінець", "save_pre": "Зберегти", "use_pre": "ПРЕСЕТИ", "symptom": "Симптом"},
    "Français": {"title": "SCHÉMA THÉRAPEUTIQUE", "pat": "Patient", "date": "Date", "med": "Médicament", "dose": "Dosage", "m": "Matin", "p": "Après-midi", "s": "Soir", "n": "Nuit", "inst": "Instructions", "need": "AU BESOIN", "max": "Max/jour", "time": "Heure", "sig": "Signature", "btn": "IMPRIMER", "duration": "Jours", "end": "Fin", "save_pre": "Enregistrer", "use_pre": "VOS PRESETS", "symptom": "Symptôme"},
    "Deutsch": {"title": "THERAPIEPLAN", "pat": "Patient", "date": "Datum", "med": "Medikament", "dose": "Dosis", "m": "Morgens", "p": "Mittags", "s": "Abends", "n": "Nachts", "inst": "Anweisungen", "need": "BEI BEDARF", "max": "Max/Tag", "time": "Uhr", "sig": "Unterschrift", "btn": "DRUCKEN", "duration": "Tage", "end": "Ende", "save_pre": "Speichern", "use_pre": "PRESETS", "symptom": "Symptom"}
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Impostazioni")
    choice = st.selectbox("Lingua / Language", list(LANGS.keys()))
    t = LANGS[choice]
    p_name = st.text_input(t["pat"], "Paziente")
    p_date = st.date_input(t["date"], date.today())
    
    st.divider()
    st.subheader(f"🚀 {t['use_pre']}")
    
    # Caricamento Preset da Sheets
    df_presets = load_presets()
    if not df_presets.empty:
        for index, row in df_presets.iterrows():
            col_a, col_b = st.columns([4, 1])
            if col_a.button(f"➕ {row['preset_name']}", use_container_width=True):
                end_date = (date.today() + timedelta(days=int(row['days']))).strftime("%d/%m/%Y") if row['days'] > 0 else None
                st.session_state.meds.append({
                    "nome": row['med_name'], "dose": f"{row['dose']} {row['unit']}", "forma": row['shape'],
                    "m": "X" if row['m'] else "", "p": "X" if row['p'] else "", "s": "X" if row['s'] else "", "n": "X" if row['n'] else "",
                    "need": bool(row['need']), "max": int(row['max']), "sy": row['symptom'], "hr": row['hour'], "nt": row['note'], "end": end_date
                })
                st.rerun()
    
    if st.button("🗑️ Reset Lista", use_container_width=True):
        st.session_state.meds = []; st.rerun()

# --- FORM AGGIUNTA ---
with st.expander("➕ Aggiungi Farmaco", expanded=True):
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
        
        st.write("---")
        save_pre = st.checkbox(t["save_pre"])
        ps_n = st.text_input("Nome Preset (es: Tachipirina Dolore)")

        if st.form_submit_button("Aggiungi"):
            if f_n:
                dt_e = (date.today() + timedelta(days=f_d)).strftime("%d/%m/%Y") if f_d > 0 else None
                # Aggiunta a sessione locale
                st.session_state.meds.append({"nome": f_n, "dose": f"{f_ds} {f_un}", "forma": f_sh, "m": "X" if v_m else "", "p": "X" if v_p else "", "s": "X" if v_s else "", "n": "X" if v_n else "", "need": v_an, "max": v_mx, "sy": v_sy, "hr": v_hr, "nt": v_nt, "end": dt_e})
                
                # Salvataggio su Google Sheets
                if save_pre:
                    final_p_name = ps_n.strip() if ps_n.strip() else f"{f_n} {f_ds}{f_un}"
                    new_preset = {
                        "preset_name": final_p_name, "med_name": f_n, "dose": f_ds, "unit": f_un, "shape": f_sh,
                        "m": v_m, "p": v_p, "s": v_s, "n": v_n, "need": v_an, "max": v_mx, "symptom": v_sy,
                        "hour": v_hr, "note": v_nt, "days": f_d
                    }
                    save_preset_to_sheets(new_preset)
                st.rerun()

# --- TABELLA FINALE ---
if st.session_state.meds:
    if st.button(t["btn"], type="primary", use_container_width=True):
        components.html("<script>window.print();</script>", height=0)

    h = "<style>.tab{width:100%;border-collapse:collapse;border:2px solid black;font-family:sans-serif;color:black;}.tab th{background:#f2f2f2;border:1px solid black;padding:8px;font-size:11px;}.tab td{border:1px solid black;padding:10px;text-align:center;}.nb{background:#fff0f0;color:red;border:1px dashed red;padding:5px;font-weight:bold;}</style>"
    h += f"<div style='background:white;padding:20px;'><h2 style='text-align:center;'>{t['title']}</h2>"
    h += f"<p style='text-align:center;'><b>{t['pat']}:</b> {p_name} | <b>{t['date']}:</b> {p_date.strftime('%d/%m/%Y')}</p>"
    h += f"<table class='tab'><thead><tr><th>{t['med']}</th><th>{t['m']}☀️</th><th>{t['p']}🌤️</th><th>{t['s']}🌅</th><th>{t['n']}🌙</th><th>{t['inst']}</th></tr></thead><tbody>"

    for m in st.session_state.meds:
        fine = f"<br><small style='color:red;'>⌛{t['end']}: {m['end']}</small>" if m['end'] else ""
        h += "<tr>"
        h += f"<td style='text-align:left;width:25%;'><span style='font-size:25px;'>{m['forma']}</span> <b>{m['nome']}</b><br><small>{m['dose']}</small>{fine}</td>"
        
        if m['need']:
            txt = f"{t['need']}"
            if m['max'] > 0: txt += f" (max {m['max']} v/die)"
            if m['sy']: txt += f"<br><i>{m['sy']}</i>"
            h += f"<td colspan='4'><div class='nb'>{txt}</div></td>"
        else:
            h += f"<td>{m['m']}</td><td>{m['p']}</td><td>{m['s']}</td><td>{m['n']}</td>"

        notes = ""
        if m['hr']: notes += f"🕒 <b>{m['hr']}</b><br>"
        if m['nt']: notes += m['nt']
        h += f"<td style='text-align:left;font-size:11px;width:25%;'>{notes}</td></tr>"

    h += f"</tbody></table></div>"
    st.markdown(h, unsafe_allow_html=True)
