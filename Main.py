import streamlit as st
import streamlit.components.v1 as components
from datetime import date, timedelta
import json
import os

st.set_page_config(page_title="PillPrint Pro", layout="wide")

# --- DATABASE PRESET ---
PRESETS_FILE = "doctor_presets.json"
def load_presets():
    if os.path.exists(PRESETS_FILE):
        try:
            with open(PRESETS_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_presets(presets):
    with open(PRESETS_FILE, "w") as f: json.dump(presets, f)

if 'meds' not in st.session_state: st.session_state.meds = []
if 'presets' not in st.session_state: st.session_state.presets = load_presets()

# --- TRADUZIONI COMPLETE (10 LINGUE) ---
LANGS = {
    "Italiano": {
        "title": "SCHEMA TERAPEUTICO", "pat": "Paziente", "date": "Data", "med": "Farmaco", "dose": "Dose",
        "m": "Mattina", "p": "Pomeriggio", "s": "Sera", "n": "Notte", "inst": "Istruzioni", 
        "need": "AL BISOGNO", "max": "Max volte/die", "time": "Ora", "sig": "Firma e Timbro", 
        "btn": "STAMPA PDF", "duration": "Durata (gg)", "end": "Fine", "save_pre": "Salva Preset", "use_pre": "I TUOI PRESET",
        "symptom": "Sintomo (es. febbre)"
    },
    "English": {
        "title": "MEDICATION SCHEDULE", "pat": "Patient", "date": "Date", "med": "Medication", "dose": "Dose",
        "m": "Morning", "p": "Afternoon", "s": "Evening", "n": "Night", "inst": "Instructions", 
        "need": "AS NEEDED", "max": "Max/day", "time": "Time", "sig": "Signature & Stamp", 
        "btn": "PRINT PDF", "duration": "Duration (days)", "end": "Ends", "save_pre": "Save Preset", "use_pre": "YOUR PRESETS",
        "symptom": "Symptom (e.g. fever)"
    },
    "Română": {
        "title": "SCHEMA TERAPEUTICĂ", "pat": "Pacient", "date": "Data", "med": "Medicament", "dose": "Doză",
        "m": "Dimineața", "p": "După-amiaza", "s": "Seara", "n": "Noaptea", "inst": "Instrucțiuni", 
        "need": "LA NEVOIE", "max": "Max ori/zi", "time": "Ora", "sig": "Semnătura și Parafa", 
        "btn": "IMPRIMĂ PDF", "duration": "Durată (zile)", "end": "Sfârșit", "save_pre": "Salvează Preset", "use_pre": "PRESETĂRILE TALE",
        "symptom": "Simptom (ex. febră)"
    },
    "العربية (Arabic)": {
        "title": "جدول العلاج", "pat": "المريض", "date": "التاريخ", "med": "الدواء", "dose": "الجرعة",
        "m": "صباحاً", "p": "بعد الظهر", "s": "مساًء", "n": "ليلاً", "inst": "تعليمات", 
        "need": "عند الحاجة", "max": "أقصى عدد/يوم", "time": "الوقت", "sig": "التوقيع والختم", 
        "btn": "طباعة PDF", "duration": "المدة (أيام)", "end": "النهاية", "save_pre": "حفظ الإعداد", "use_pre": "إعداداتك",
        "symptom": "الأعراض (مثلاً حمى)"
    },
    "Shqip (Albanian)": {
        "title": "SKEMA TERAPEUTIKE", "pat": "Pacienti", "date": "Data", "med": "Barërat", "dose": "Doza",
        "m": "Mëngjes", "p": "Pasdite", "s": "Mbrëmje", "n": "Natë", "inst": "Udhëzime", 
        "need": "SIPAS NEVOJËS", "max": "Max herë/ditë", "time": "Ora", "sig": "Firma dhe Vula", 
        "btn": "PRINT PDF", "duration": "Kohëzgjatja (ditë)", "end": "Mbarimi", "save_pre": "Ruaj Preset", "use_pre": "PRESETET TUAJA",
        "symptom": "Simptoma (p.sh. ethe)"
    },
    "Español": {
        "title": "ESQUEMA TERAPÉUTICO", "pat": "Paciente", "date": "Fecha", "med": "Medicamento", "dose": "Dosis",
        "m": "Mañana", "p": "Tarde", "s": "Noche", "n": "Madrugada", "inst": "Instrucciones", 
        "need": "SI ES NECESARIO", "max": "Max veces/día", "time": "Hora", "sig": "Firma y Sello", 
        "btn": "IMPRIMIR PDF", "duration": "Duración (días)", "end": "Fin", "save_pre": "Guardar Preset", "use_pre": "TUS PRESETS",
        "symptom": "Síntoma (ej. fiebre)"
    },
    "中文 (Chinese)": {
        "title": "治疗方案", "pat": "患者", "date": "日期", "med": "药物", "dose": "剂量",
        "m": "早上", "p": "下午", "s": "晚上", "n": "夜间", "inst": "指示", 
        "need": "必要时服用", "max": "每日最多次数", "time": "时间", "sig": "签名及盖章", 
        "btn": "打印 PDF", "duration": "时长 (天)", "end": "结束日期", "save_pre": "保存预设", "use_pre": "您的预设",
        "symptom": "症状 (如发烧)"
    },
    "Українська": {
        "title": "СХЕМА ЛІКУВАННЯ", "pat": "Пацієнт", "date": "Дата", "med": "Препарат", "dose": "Доза",
        "m": "Ранок", "p": "День", "s": "Вечір", "n": "Ніч", "inst": "Інструкції", 
        "need": "ЗА ПОТРЕБИ", "max": "Макс. разів/день", "time": "Час", "sig": "Підпис та печатка", 
        "btn": "ДРУКУВАТИ PDF", "duration": "Тривалість (днів)", "end": "Кінець", "save_pre": "Зберегти пресет", "use_pre": "ВАШІ ПРЕСЕТИ",
        "symptom": "Симптом (напр. лихоманка)"
    },
    "Français": {
        "title": "SCHÉMA THÉRAPEUTIQUE", "pat": "Patient", "date": "Date", "med": "Médicament", "dose": "Dosage",
        "m": "Matin", "p": "Après-midi", "s": "Soir", "n": "Nuit", "inst": "Instructions", 
        "need": "AU BESOIN", "max": "Max fois/jour", "time": "Heure", "sig": "Signature et Tampon", 
        "btn": "IMPRIMER PDF", "duration": "Durée (jours)", "end": "Fin", "save_pre": "Enregistrer Preset", "use_pre": "VOS PRESETS",
        "symptom": "Symptôme (ex. fièvre)"
    },
    "Deutsch": {
        "title": "THERAPIEPLAN", "pat": "Patient", "date": "Datum", "med": "Medikament", "dose": "Dosierung",
        "m": "Morgens", "p": "Mittags", "s": "Abends", "n": "Nachts", "inst": "Anweisungen", 
        "need": "BEI BEDARF", "max": "Max. pro Tag", "time": "Uhrzeit", "sig": "Unterschrift & Stempel", 
        "btn": "PDF DRUCKEN", "duration": "Dauer (Tage)", "end": "Ende", "save_pre": "Preset speichern", "use_pre": "IHRE PRESETS",
        "symptom": "Symptom (z.B. Fieber)"
    }
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    choice = st.selectbox("Lingua / Language", list(LANGS.keys()))
    t = LANGS[choice]
    p_name = st.text_input(t["pat"], "Paziente")
    p_date = st.date_input(t["date"], date.today())
    
    st.divider()
    st.subheader(f"🚀 {t['use_pre']}")
    if st.session_state.presets:
        for k in list(st.session_state.presets.keys()):
            cols = st.columns([4, 1])
            if cols[0].button(f"➕ {k}", key=f"add_{k}", use_container_width=True):
                d = st.session_state.presets[k]
                e = (date.today() + timedelta(days=d.get('days', 0))).strftime("%d/%m/%Y") if d.get('days', 0) > 0 else None
                st.session_state.meds.append({
                    "nome": d['n'], "dose": f"{d['d']} {d['u']}", "forma": d['f'], 
                    "m": "X" if d['m'] else "", "p": "X" if d['p'] else "", "s": "X" if d['s'] else "", "n": "X" if d['n_v'] else "", 
                    "need": d['an'], "max": d['mx'], "hour": d['hr'], "note": d['nt'], "end": e, "symptom": d.get('sy', "")
                })
                st.rerun()
            if cols[1].button("🗑️", key=f"del_{k}"):
                del st.session_state.presets[k]
                save_presets(st.session_state.presets); st.rerun()
    
    if st.button("🗑️ Reset", use_container_width=True):
        st.session_state.meds = []; st.rerun()

# --- FORM AGGIUNTA ---
with st.expander("➕ Aggiungi Farmaco", expanded=True):
    with st.form("f1", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        f_n = c1.text_input(t["med"])
        f_d = c2.number_input(t["duration"], 0, 365, 0)
        r2 = st.columns([1, 1, 2])
        f_ds, f_un = r2[0].text_input(t["dose"]), r2[1].selectbox("Unità", ["mg", "ml", "gocce", "cpr", "bustine", "UI"])
        f_sh = r2[2].radio("Forma", ["💊", "⚪", "💧", "🥄", "💉"], horizontal=True)
        
        st.write(f"**{t['m']}/{t['p']}/{t['s']}**")
        t_cols = st.columns(4)
        v_m, v_p, v_s, v_n = t_cols[0].checkbox(t["m"]), t_cols[1].checkbox(t["p"]), t_cols[2].checkbox(t["s"]), t_cols[3].checkbox(t["n"])
        
        st.divider()
        e_cols = st.columns([1, 1, 2])
        v_an = e_cols[0].checkbox(t["need"])
        v_mx = e_cols[1].number_input(t["max"], 0, 12, 0)
        v_sy = e_cols[2].text_input(t["symptom"])
        
        v_hr = st.text_input(t["time"], placeholder="es. 08:00")
        v_nt = st.text_input(t["inst"])
        
        sv = st.checkbox(t["save_pre"])
        ps_n = st.text_input("Nome Preset (Opzionale)")
        
        if st.form_submit_button("Aggiungi"):
            if f_n:
                dt_e = (date.today() + timedelta(days=f_d)).strftime("%d/%m/%Y") if f_d > 0 else None
                final_p = ps_n.strip() if ps_n.strip() else f"{f_n} {f_ds}{f_un}"
                st.session_state.meds.append({
                    "nome": f_n, "dose": f"{f_ds} {f_un}", "forma": f_sh, 
                    "m": "X" if v_m else "", "p": "X" if v_p else "", "s": "X" if v_s else "", "n": "X" if v_n else "", 
                    "need": v_an, "max": v_mx, "hour": v_hr, "note": v_nt, "end": dt_e, "symptom": v_sy
                })
                if sv:
                    st.session_state.presets[final_p] = {"n": f_n, "d": f_ds, "u": f_un, "f": f_sh, "m": v_m, "p": v_p, "s": v_s, "n_v": v_n, "an": v_an, "mx": v_mx, "hr": v_hr, "nt": v_nt, "days": f_d, "sy": v_sy}
                    save_presets(st.session_state.presets)
                st.rerun()

# --- COSTRUZIONE TABELLA ---
if st.session_state.meds:
    if st.button(t["btn"], type="primary", use_container_width=True):
        components.html("<script>window.print();</script>", height=0)

    h = "<style>.tab{width:100%;border-collapse:collapse;border:2px solid black;font-family:sans-serif;color:black;}.tab th{background:#f2f2f2;border:1px solid black;padding:8px;font-size:11px;}.tab td{border:1px solid black;padding:10px;text-align:center;}.need-box{background:#fff0f0;color:red;border:1px dashed red;padding:5px;font-size:13px;font-weight:bold;text-align:center;}</style>"
    h += f"<div style='background:white;padding:20px;'><h2 style='text-align:center;margin:0;'>{t['title']}</h2>"
    h += f"<p style='text-align:center;'><b>{t['pat']}:</b> {p_name} | <b>{t['date']}:</b> {p_date.strftime('%d/%m/%Y')}</p>"
    h += f"<table class='tab'><thead><tr><th>{t['med']}</th><th>{t['m']}☀️</th><th>{t['p']}🌤️</th><th>{t['s']}🌅</th><th>{t['n']}🌙</th><th>{t['inst']}</th></tr></thead><tbody>"

    for m in st.session_state.meds:
        fine = f"<br><small style='color:red;'>⌛ {t['end']}: {m['end']}</small>" if m['end'] else ""
        h += "<tr>"
        h += f"<td style='text-align:left;width:25%;'><span style='font-size:25px;'>{m['forma']}</span> <b>{m['nome']}</b><br><small>{m['dose']}</small>{fine}</td>"
        
        if m['need']:
            txt_need = f"{t['need']}"
            if m['max'] > 0: txt_need += f" (max {m['max']} {t['max'].split(' ')[1]})"
            if m['symptom']: txt_need += f"<br><span style='font-weight:normal; font-style:italic;'>{m['symptom']}</span>"
            h += f"<td colspan='4' style='background:#fffcfc;'><div class='need-box'>{txt_need}</div></td>"
        else:
            h += f"<td>{m['m']}</td><td>{m['p']}</td><td>{m['s']}</td><td>{m['n']}</td>"

        notes = ""
        if m['hour']: notes += f"🕒 <b>{m['hour']}</b><br>"
        if m['note']: notes += m['note']
        h += f"<td style='text-align:left;font-size:11px;width:25%;'>{notes}</td></tr>"

    h += f"</tbody></table><div style='margin-top:40px;text-align:right;'>{t['sig']}: _________________</div></div>"
    st.markdown(h, unsafe_allow_html=True)
