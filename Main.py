import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, timedelta
import streamlit.components.v1 as components

# Configurazione Pagina
st.set_page_config(page_title="PillPrint Pro", layout="wide")

# --- CONNESSIONE GOOGLE SHEETS ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/106bwDrvfYDeb_mgNgorAcCQZQzwPeXk8vzp3j6hJVC8/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300)
def load_presets():
    try:
        return conn.read(spreadsheet=SPREADSHEET_URL, worksheet="presets")
    except:
        return pd.DataFrame()

def save_preset(new_row):
    existing_df = load_presets()
    updated_df = pd.concat([existing_df, pd.DataFrame([new_row])], ignore_index=True)
    conn.update(spreadsheet=SPREADSHEET_URL, worksheet="presets", data=updated_df)
    st.cache_data.clear() # Reset cache per vedere subito il nuovo preset

# --- STATO SESSIONE ---
if 'meds' not in st.session_state: st.session_state.meds = []

# --- TRADUZIONI (10 LINGUE) ---
LANGS = {
    "Italiano": {"title": "SCHEMA TERAPEUTICO", "pat": "Paziente", "date": "Data", "med": "Farmaco", "dose": "Dose", "m": "Mattina", "p": "Pomeriggio", "s": "Sera", "n": "Notte", "inst": "Istruzioni", "need": "AL BISOGNO", "max": "Max volte/die", "time": "Ora", "sig": "Firma e Timbro", "btn": "STAMPA PDF", "duration": "Durata (gg)", "end": "Fine", "save_pre": "Salva nei Preset", "use_pre": "I TUOI PRESET", "symptom": "Sintomo"},
    "English": {"title": "MEDICATION SCHEDULE", "pat": "Patient", "date": "Date", "med": "Medication", "dose": "Dose", "m": "Morning", "p": "Afternoon", "s": "Evening", "n": "Night", "inst": "Instructions", "need": "AS NEEDED", "max": "Max/day", "time": "Time", "sig": "Signature", "btn": "PRINT PDF", "duration": "Days", "end": "Ends", "save_pre": "Save to Presets", "use_pre": "YOUR PRESETS", "symptom": "Symptom"},
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
    st.header("⚙️ Settings")
    choice = st.selectbox("Lingua", list(LANGS.keys()))
    t = LANGS[choice]
    p_name = st.text_input(t["pat"], "Paziente")
    p_date = st.date_input(t["date"], date.today())
    
    st.divider()
    st.subheader(f"🚀 {t['use_pre']}")
    
    df_p = load_presets()
    if not df_p.empty:
        for _, row in df_p.iterrows():
            if st.button(f"➕ {row['preset_name']}", use_container_width=True):
                d_gg = int(row['days']) if pd.notnull(row['days']) else 0
                end_d = (date.today() + timedelta(days=d_gg)).strftime("%d/%m/%Y") if d_gg > 0 else None
                st.session_state.meds.append({
                    "nome": row['med_name'], "dose": f"{row['dose']} {row['unit']}", "forma": row['shape'],
                    "m": "X" if str(row['m']).lower() == 'true' else "", "p": "X" if str(row['p']).lower() == 'true' else "",
                    "s": "X" if str(row['s']).lower() == 'true' else "", "n": "X" if str(row['n']).lower() == 'true' else "",
                    "need": str(row['need']).lower() == 'true', "max": row['max'], "sy": row['symptom'], "hr": row['hour'], "nt": row['note'], "end": end_d
                })
                st.rerun()

    if st.button("🗑️ Reset Lista", use_container_width=True):
        st.session_state.meds = []; st.rerun()

# --- FORM AGGIUNTA ---
with st.expander("➕ Aggiungi Farmaco", expanded=True):
    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        f_n, f_d = c1.text_input(t["med"]), c2.number_input(t["duration"], 0, 365, 0)
        
        r2 = st.columns([1, 1, 2])
        f_ds, f_un = r2[0].text_input(t["dose"]), r2[1].selectbox("Unità", ["mg", "ml", "gocce", "cpr", "bustine", "UI"])
        f_sh = r2[2].radio("Forma", ["💊", "⚪", "💧", "🥄", "💉"], horizontal=True)
        
        t_cols = st.columns(4)
        v_m, v_p, v_s, v_n = t_cols[0].checkbox(t["m"]), t_cols[1].checkbox(t["p"]), t_cols[2].checkbox(t["s"]), t_cols[3].checkbox(t["n"])
        
        st.divider()
        e_cols = st.columns([1, 1, 2])
        v_an, v_mx, v_sy = e_cols[0].checkbox(t["need"]), e_cols[1].number_input(t["max"], 0, 12, 0), e_cols[2].text_input(t["symptom"])
        v_hr, v_nt = st.columns(2)[0].text_input(t["time"]), st.columns(2)[1].text_input(t["inst"])
        
        st.write("---")
        do_save = st.checkbox(t["save_pre"])
        ps_name = st.text_input("Nome per il Preset (es: Tachipirina 1000)")

        if st.form_submit_button("Aggiungi"):
            if f_n:
                dt_e = (date.today() + timedelta(days=f_d)).strftime("%d/%m/%Y") if f_d > 0 else None
                st.session_state.meds.append({"nome": f_n, "dose": f"{f_ds} {f_un}", "forma": f_sh, "m": "X" if v_m else "", "p": "X" if v_p else "", "s": "X" if v_s else "", "n": "X" if v_n else "", "need": v_an, "max": v_mx, "sy": v_sy, "hr": v_hr, "nt": v_nt, "end": dt_e})
                
                if do_save:
                    new_p = {"preset_name": ps_name if ps_name else f_n, "med_name": f_n, "dose": f_ds, "unit": f_un, "shape": f_sh, "m": v_m, "p": v_p, "s": v_s, "n": v_n, "need": v_an, "max": v_mx, "symptom": v_sy, "hour": v_hr, "note": v_nt, "days": f_d}
                    save_preset(new_p)
                st.rerun()

# --- TABELLA ---
if st.session_state.meds:
    if st.button(t["btn"], type="primary", use_container_width=True):
        components.html("<script>window.print();</script>", height=0)

    h = "<style>.tab{width:100%;border-collapse:collapse;border:2px solid black;font-family:sans-serif;color:black;}.tab th{background:#f2f2f2;border:1.5px solid black;padding:8px;font-size:11px;}.tab td{border:1.5px solid black;padding:10px;text-align:center;}.nb{background:#fff0f0;color:red;border:1px dashed red;padding:5px;font-weight:bold;}</style>"
    h += f"<div style='background:white;padding:20px;'><h2 style='text-align:center;'>{t['title']}</h2><p style='text-align:center;'><b>{t['pat']}:</b> {p_name} | <b>{t['date']}:</b> {p_date.strftime('%d/%m/%Y')}</p>"
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
        h += f"<td style='text-align:left;font-size:11px;width:25%;'>🕒 <b>{m['hr']}</b><br>{m['nt']}</td></tr>"

    h += "</tbody></table><div style='margin-top:30px;text-align:right;'>{t['sig']}: _________________</div></div>"
    st.markdown(h, unsafe_allow_html=True)
