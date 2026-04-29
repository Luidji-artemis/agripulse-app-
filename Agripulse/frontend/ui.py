"""
AgriPulse — Intelligence Agricole Camerounaise
Interface finale responsive, boutons Nouvelle analyse / Réinitialiser, toasts
Version corrigée : reset par simple rafraîchissement
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os, random
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
import analytics as an
import recommendations as rec

# ═══════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=600)
def get_marches_par_produit_et_region(produit: str, region: str):
    df = an.load_data()
    if df.empty:
        return []
    region_col = None
    for col in df.columns:
        if 'region' in col.lower() or col == 'région':
            region_col = col
            break
    if region_col is None:
        return []
    df = df.rename(columns={region_col: 'region'})
    mask = (df['produit'] == produit) & (df['region'] == region)
    marches = df.loc[mask, 'marche'].dropna().unique()
    return sorted(marches) if len(marches) > 0 else []

# Fonctions de réinitialisation simplifiées : rafraîchissement uniquement
def reset_analyse_fields():
    # On lève un drapeau
    st.session_state["_reset_analyse"] = True
    st.toast("🔄 Rafraîchissement…", icon="🔄")
    st.rerun()

def reset_terrain_fields():
    st.session_state["_reset_terrain"] = True
    st.toast("🧹 Rafraîchissement…", icon="🧹")
    st.rerun()
# ═══════════════════════════════════════════════════════════════════════
# CSS RESPONSIVE + STYLES (identique à ton code existant)
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
            @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css');
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700;14..32,800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg:       #f8fafc;
  --bg2:      #ffffff;
  --bg3:      #f1f5f9;
  --brd:      #e2e8f0;
  --brd2:     #cbd5e1;
  --txt:      #0f172a;
  --txt2:     #1e293b;
  --txt3:     #334155;
  --grn:      #16a34a;
  --grn2:     #15803d;
  --grn-bg:   #f0fdf4;
  --grn-lt:   #dcfce7;
  --amb:      #d97706;
  --amb-bg:   #fffbeb;
  --blu:      #2563eb;
  --blu-bg:   #eff6ff;
  --red:      #dc2626;
  --red-bg:   #fef2f2;
  --sh-sm:    0 1px 2px rgba(0,0,0,0.05);
  --sh-md:    0 4px 12px rgba(0,0,0,0.08);
  --sh-lg:    0 8px 30px rgba(0,0,0,0.12);
  --r:        12px;
  --rs:       8px;
  --transition: all 0.25s cubic-bezier(0.2, 0.9, 0.4, 1.1);
}

/* Base */
html, body, [class*="css"] {
  font-family: 'Inter', sans-serif !important;
  background: var(--bg) !important;
  color: var(--txt) !important;
  font-size: 16px !important;
  line-height: 1.65 !important;
}
.stApp { background: var(--bg) !important; }
.block-container {
  padding: 1rem 1.5rem 2rem !important;
  max-width: 100% !important;
}
#MainMenu, footer, header { visibility: hidden; }

/* Ticker */
.tkr-wrap{ background:#0f172a; overflow:hidden; white-space:nowrap; padding:9px 0; border-radius:0 0 10px 10px; margin-bottom:12px; }
.tkr-track{ display:inline-block; animation:tkr 55s linear infinite; }
.tkr-track:hover{ animation-play-state:paused; }
@keyframes tkr{ 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
.tkr-item{ display:inline-block; padding:0 28px; font-family:'JetBrains Mono',monospace; font-size:13px; color:#e2e8f0; }
.tkr-item .tp{ color:#4ade80; font-weight:600; }
.tkr-item .tv{ color:#fbbf24; }
.tkr-item .tr{ color:#94a3b8; font-size:11px; }
.tkr-sep{ color:#334155; padding:0 4px; }

/* Header */
.ap-hdr{ background:#fff; border-bottom:3px solid var(--grn); padding:14px 24px 12px;
  display:flex; align-items:center; justify-content:space-between;
  box-shadow:var(--sh-sm); margin-bottom:12px; border-radius:0 0 12px 12px; }
.ap-hdr h1{ font-size:1.8rem; font-weight:800; color:var(--grn); margin:0; letter-spacing:-0.02em; }
.ap-hdr .sub{ color:var(--txt3); font-size:11px; letter-spacing:1.5px; font-family:'JetBrains Mono',monospace; text-transform:uppercase; margin-top:4px; }
.live-badge{ background:var(--grn); color:#fff; padding:5px 14px; border-radius:30px;
  font-size:12px; font-weight:700; letter-spacing:0.5px;
  animation:bp 2s ease-in-out infinite; }
@keyframes bp{ 0%,100%{box-shadow:0 0 0 0 rgba(22,163,74,0.4)} 50%{box-shadow:0 0 0 6px rgba(22,163,74,0)} }

/* Info bar */
.info-bar{ background:var(--grn-bg); border-left:4px solid var(--grn); border-radius:8px;
  padding:10px 16px; font-size:13px; color:var(--txt2); margin-bottom:20px; }

/* Cartes génériques */
.card{ background:var(--bg2); border:1px solid var(--brd); border-radius:var(--r);
  padding:20px; margin-bottom:20px; box-shadow:var(--sh-sm);
  transition:var(--transition); animation:cin .35s ease forwards; }
.card:hover{ box-shadow:var(--sh-md); transform:translateY(-2px); }
@keyframes cin{ from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
.c-grn{ border-left:4px solid var(--grn); background:var(--grn-bg); }
.c-amb{ border-left:4px solid var(--amb); background:var(--amb-bg); }
.c-blu{ border-left:4px solid var(--blu); background:var(--blu-bg); }
.c-red{ border-left:4px solid var(--red); background:var(--red-bg); }

/* Typographie */
.h-sec{ font-size:13px; font-weight:700; text-transform:uppercase; letter-spacing:1px;
  color:var(--txt2); padding:6px 0 8px; border-bottom:2px solid var(--brd); margin-bottom:16px; }
.h-crd{ font-size:15px; font-weight:700; color:var(--txt); margin:0 0 8px 0; }
.nbig{ font-family:'JetBrains Mono',monospace; font-size:2rem; font-weight:700; color:var(--txt); line-height:1.2; }
.nmid{ font-family:'JetBrains Mono',monospace; font-size:1.35rem; font-weight:600; color:var(--grn); }
.nsm{  font-family:'JetBrains Mono',monospace; font-size:1rem; font-weight:500; color:var(--txt2); }
.lxs{  font-size:11px; font-weight:600; color:var(--txt3); text-transform:uppercase; letter-spacing:0.5px; }
.btxt{ font-size:14px; color:var(--txt2); line-height:1.7; }
.badge-grn{ font-size:10px; font-weight:600; padding:2px 8px; border-radius:20px;
  background:var(--grn-lt); color:var(--grn2); display:inline-block; margin-left:8px; }

/* Widgets */
.stSelectbox div[data-baseweb="select"] > div,
.stSelectbox div[data-baseweb="select"] input,
.stSelectbox span[data-baseweb="select"] span {
  color: var(--txt) !important;
  background-color: var(--bg2) !important;
}
div[role="listbox"] div[role="option"] span {
  color: var(--txt) !important;
  background-color: var(--bg2) !important;
}
div[role="listbox"] div[role="option"]:hover span {
  background-color: var(--bg3) !important;
}
.stNumberInput input, .stTextArea textarea, .stDateInput input {
  color: var(--txt) !important;
  background-color: var(--bg2) !important;
}
.stSelectbox label, .stNumberInput label, .stTextArea label, .stDateInput label {
  font-size:14px !important; font-weight:600 !important; color: var(--txt2) !important; margin-bottom:4px !important;
}
.stSelectbox > div > div, .stNumberInput > div > div, .stTextArea > div > textarea, .stDateInput > div > div {
  border-radius:var(--rs) !important;
  border:1px solid var(--brd2) !important;
  font-size:15px !important;
  background:var(--bg2) !important;
  transition:var(--transition) !important;
}
.stSelectbox > div > div:focus-within, .stNumberInput > div > div:focus-within,
.stTextArea > div > textarea:focus, .stDateInput > div > div:focus-within {
  border-color:var(--grn) !important;
  box-shadow:0 0 0 3px rgba(22,163,74,0.2) !important;
}
.block-container .stSelectbox, .block-container .stNumberInput, .block-container .stTextArea, .block-container .stDateInput {
  margin-bottom: 12px !important;
}

/* Messages */
.stAlert {
  background-color: var(--bg2) !important;
  border-left: 4px solid var(--grn) !important;
  color: var(--txt) !important;
  font-weight: 700 !important;
}
.stAlert .stAlertContent {
  color: var(--txt) !important;
  font-weight: 700 !important;
}
.stSuccess {
  background-color: #e6f7e6 !important;
  border: 1px solid #16a34a !important;
  color: #0f172a !important;
  font-weight: 700 !important;
}
.stSuccess .stAlertContent {
  color: #0f172a !important;
  font-weight: 700 !important;
}
.stWarning, .stInfo, .stError {
  color: var(--txt) !important;
  font-weight: 700 !important;
}

/* Date verrouillée */
.locked-date {
  background: #f0fdf4;
  border: 1px solid #dcfce7;
  border-radius: 8px;
  padding: 10px;
  margin-top: 4px;
  color: #0f172a !important;
  font-weight: 700 !important;
  font-size: 15px;
  font-family: 'JetBrains Mono', monospace;
}
.locked-date strong {
  color: #0f172a !important;
  font-weight: 800 !important;
}

/* Boutons */
.stButton > button {
  background:linear-gradient(135deg, var(--grn), var(--grn2)) !important;
  color:#fff !important;
  border:none !important;
  border-radius:var(--rs) !important;
  font-family:'Inter',sans-serif !important;
  font-weight:700 !important;
  font-size:14px !important;
  width:100% !important;
  padding:12px !important;
  box-shadow:0 2px 8px rgba(22,163,74,0.3) !important;
  transition:var(--transition) !important;
}
.stButton > button:hover {
  transform:translateY(-2px) !important;
  box-shadow:0 8px 20px rgba(22,163,74,0.4) !important;
}
.stButton > button:active { transform:translateY(0) !important; }

/* Onglets plus dynamiques */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px !important;
    background: #e2e8f0 !important;   /* fond de la barre légèrement plus marqué */
    border-radius: 12px !important;
    padding: 5px !important;
    border: 1px solid #cbd5e1 !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 700 !important;      /* texte plus épais */
    padding: 8px 18px !important;
    color: #1e293b !important;        /* couleur foncée pour contraste */
    background: transparent;
    transition: all 0.25s ease !important;
    border: 1px solid transparent !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: #ffffff !important;
    border-color: #16a34a !important;
    color: #16a34a !important;
    box-shadow: 0 2px 8px rgba(22,163,74,0.15) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #16a34a, #15803d) !important;
    color: #ffffff !important;
    border: 1px solid #16a34a !important;
    box-shadow: 0 4px 12px rgba(22,163,74,0.4) !important;
    font-weight: 800 !important;
    transform: translateY(-1px);
}

/* Métriques */
[data-testid="stMetric"] {
  background:var(--bg2) !important;
  border:1px solid var(--brd) !important;
  border-radius:var(--rs) !important;
  padding:12px 14px !important;
  box-shadow:var(--sh-sm) !important;
}
[data-testid="stMetricLabel"] {
  font-size:11px !important;
  font-weight:700 !important;
  color:var(--txt2) !important;
  text-transform:uppercase !important;
  letter-spacing:0.5px !important;
}
[data-testid="stMetricValue"] {
  font-family:'JetBrains Mono',monospace !important;
  font-size:1.15rem !important;
  font-weight:700 !important;
  color:var(--txt) !important;
}
[data-testid="stMetricDelta"] {
  color: var(--grn) !important;
  font-weight:600 !important;
}

/* Recommendation card */
.rcard{ background:var(--bg2); border:1px solid var(--brd); border-radius:var(--r);
  padding:16px 18px; margin-bottom:14px; box-shadow:var(--sh-sm); transition:var(--transition); }
.rcard:hover{ box-shadow:var(--sh-md); transform:translateY(-1px); }
.rcard h4{ font-size:14px; font-weight:700; margin:0 0 8px 0; color:var(--txt); }
.rcard p{ font-size:14px; color:var(--txt2); line-height:1.65; margin:0; }

/* Footer */
.ft-bar{ text-align:center; padding:16px; border-top:1px solid var(--brd); margin-top:24px;
  font-size:12px; color:var(--txt3); font-family:'JetBrains Mono',monospace; }
.ft-bar strong{ color:var(--grn); }

/* Scrollbar */
::-webkit-scrollbar{ width:6px; height:6px; }
::-webkit-scrollbar-track{ background:var(--bg3); border-radius:4px; }
::-webkit-scrollbar-thumb{ background:var(--brd2); border-radius:4px; }
::-webkit-scrollbar-thumb:hover{ background:var(--txt3); }

/* RESPONSIVE : MOBILE */
@media (max-width: 768px) {
  .block-container { padding: 0.5rem 0.8rem 1rem !important; }
  .ap-hdr { flex-direction: column; align-items: flex-start; gap: 6px; }
  .ap-hdr h1 { font-size: 1.4rem; }
  .nbig { font-size: 1.6rem; }
  .h-sec { font-size: 12px; }
  .card { padding: 14px; }
  .stTabs [data-baseweb="tab"] { font-size: 11px; padding: 4px 8px; }
  section.main > div { display: flex; flex-direction: column; }
  .stColumn { width: 100% !important; margin-bottom: 20px; }
}
</style>
           
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════
for k, v in {"analyse_done": False, "result": None, "reco": None, "info_idx": 0,
             "region_analyse": None, "region_terrain": None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════════
# RÉINITIALISATION DES CHAMPS (exécutée AVANT les widgets)
# ═══════════════════════════════════════════════════════════════════════
if st.session_state.get("_reset_analyse"):
    # On supprime toutes les clés liées aux champs de l'analyse
    for key in ["ana_cat", "ana_produit", "ana_region", "ana_marche", "ana_prix"]:
        st.session_state.pop(key, None)
    st.session_state.analyse_done = False
    st.session_state.result = None
    st.session_state.reco = None
    st.session_state.pop("produit_choix", None)
    st.session_state.pop("region_choix", None)
    # On enlève le drapeau
    st.session_state["_reset_analyse"] = False
    # Premier rechargement pour effacer
    st.rerun()

if st.session_state.get("_reset_terrain"):
    for key in ["terrain_cat", "terrain_produit", "terrain_region", "terrain_marche", "terrain_prix", "terrain_comm", "terrain_marche_vide"]:
        st.session_state.pop(key, None)
    st.session_state["_reset_terrain"] = False
    st.rerun()


# ═══════════════════════════════════════════════════════════════════════
# TICKER
# ═══════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=30)
def get_ticker(n=22):
    import random
    df = an.load_data()
    if df.empty:
        return []
    region_col = None
    for col in df.columns:
        if 'region' in col.lower() or col == 'région':
            region_col = col
            break
    if region_col is None:
        smp = df.sample(min(22, len(df)))
        items = []
        for _, r in smp.iterrows():
            items.append({
                "produit": r.get("produit", "N/A"),
                "prix": int(r.get("prix_fcfa", 0)),
                "unite": r.get("unite", "kg"),
                "region": "Cameroun"
            })
        random.shuffle(items)
        return items[:n]
    df = df.rename(columns={region_col: 'region'})
    if "date" in df.columns:
        lat = df[df["date"] == df["date"].max()]
    else:
        lat = df.copy()
    try:
        smp = lat.groupby("region").apply(lambda g: g.sample(min(3, len(g)))).reset_index(drop=True)
        items = [{"produit": r["produit"], "prix": int(r["prix_fcfa"]),
                  "unite": r.get("unite", ""), "region": r["region"]} 
                 for _, r in smp.iterrows()]
    except:
        smp = lat.sample(min(22, len(lat)))
        items = [{"produit": r.get("produit", "N/A"), "prix": int(r.get("prix_fcfa", 0)),
                  "unite": r.get("unite", "kg"), "region": r.get(region_col, "Cameroun")} 
                 for _, r in smp.iterrows()]
    random.shuffle(items)
    return items[:n]

def build_ticker(items):
    parts = "".join(
        f'<span class="tkr-item"><span class="tp">{i["produit"]}</span> '
        f'<span class="tv">{i["prix"]:,} FCFA/{i["unite"]}</span> '
        f'<span class="tr">· {i["region"]}</span></span>'
        f'<span class="tkr-sep">|</span>'
        for i in items
    )
    return f'<div class="tkr-wrap"><div class="tkr-track">{parts}{parts}</div></div>'

# ═══════════════════════════════════════════════════════════════════════
# MESSAGES DÉFILANTS
# ═══════════════════════════════════════════════════════════════════════
INFO_MSGS = [
    "<i class='fas fa-seedling'></i> Saison de récolte maïs : prix bas de juin à septembre — stockez si possible",
    "<i class='fas fa-chart-line'></i> Tomate : prix au pic en décembre-janvier (saison sèche, moins d'offre)",
    "<i class='fas fa-truck'></i> Douala → Yaoundé : ~3 500 FCFA/sac 50 kg — intégrez ce coût dans votre prix",
    "<i class='fas fa-lightbulb'></i> Groupez vos ventes avec d'autres producteurs pour négocier le transport",
    "<i class='fas fa-sun'></i> Oignon Grand-Nord : prix bas après récolte nov-jan, hausse dès mars",
    "<i class='fas fa-chart-bar'></i> Nos modèles analysent 94 080 relevés de prix (2019-2024)",
    "<i class='fas fa-map'></i> Littoral (Douala) offre les prix les plus élevés pour les produits transformés",
    "<i class='fas fa-fish'></i> Tilapia frais : moins cher d'avril à juin (période de pêche intensive)",
    "<i class='fas fa-seedling'></i> Plantain : prix 2× plus bas en saison des pluies (mars-mai) vs saison sèche",
    "<i class='fas fa-arrow-trend-down'></i> Stockage = levier clé — un oignon stocké 6 semaines peut valoir 40% de plus",
]
# ═══════════════════════════════════════════════════════════════════════
# HEADER + TICKER + INFO
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="ap-hdr">
  <div>
   <h1><i class="fas fa-seedling"></i> AgriPulse || Analyse des tendances agricoles   </h1>
    <div class="sub">Intelligence Agricole Camerounaise · Tableau de Bord Prédictif</div>
</div>
  <span class="live-badge">● SYSTÈME LIVE</span>
</div>
""", unsafe_allow_html=True)

st.markdown(build_ticker(get_ticker()), unsafe_allow_html=True)

info_msg = INFO_MSGS[st.session_state.info_idx % len(INFO_MSGS)]
st.markdown(f'<div class="info-bar"><i class="fas fa-info-circle"></i> {info_msg}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# LAYOUT 3 COLONNES (inversé : onglets à gauche, carte au centre)
# ═══════════════════════════════════════════════════════════════════════
col_onglets, col_carte, col_r = st.columns([1.6, 0.95, 1.45], gap="medium")

# ═══════════════════════════════════════════════════════════════════════
# COLONNE GAUCHE – ONGLETS (Analyse + Terrain)
# ═══════════════════════════════════════════════════════════════════════
with col_onglets:
    tab_analyse, tab_terrain = st.tabs(["Analyse prédictive 🔍 ", "Collecte Donees terrain 📥 "])

    # -------------------------------------------------------------------
    # ONGLET ANALYSE PRÉDICTIVE
    # -------------------------------------------------------------------
    with tab_analyse:
        st.markdown("""
        <div class="card c-grn" style="padding:12px; margin-bottom:16px; font-size:14px; color:#0f172a;">
          💡 Saisissez les informations de votre produit pour obtenir une prédiction de prix et des recommandations.
        </div>
        """, unsafe_allow_html=True)

        categories = an.get_categories()
        cat_choix = st.selectbox("Catégorie d'aliment", ["— Choisir —"] + categories, key="ana_cat")
        produits_list = an.get_produits_par_categorie(cat_choix if cat_choix != "— Choisir —" else None)
        produit_choix = st.selectbox("Quel produit vendez-vous ?", ["— Choisir —"] + produits_list, key="ana_produit")

        regions_list = an.get_regions()
        def on_region_analyse_change():
            st.session_state.region_analyse = st.session_state.ana_region
        region_choix = st.selectbox("Région / Marché", ["— Choisir —"] + regions_list, key="ana_region", on_change=on_region_analyse_change)
        if region_choix != "— Choisir —" and st.session_state.region_analyse != region_choix:
            st.session_state.region_analyse = region_choix

        # Filtrage des marchés par produit et région
        marche_choix = None
        if region_choix != "— Choisir —" and produit_choix != "— Choisir —":
            marches_filtres = get_marches_par_produit_et_region(produit_choix, region_choix)
            if marches_filtres:
                marche_choix = st.selectbox("Marché précis (optionnel)", ["— Non précisé —"] + marches_filtres, key="ana_marche")
                marche_choix = None if marche_choix == "— Non précisé —" else marche_choix
            else:
                all_marches = an.get_marches_par_region(region_choix)
                if all_marches:
                    marche_choix = st.selectbox("Marché précis (optionnel)", ["— Non précisé —"] + all_marches, key="ana_marche")
                    marche_choix = None if marche_choix == "— Non précisé —" else marche_choix
                else:
                    st.info("Aucun marché disponible pour cette région.")
        elif region_choix != "— Choisir —":
            all_marches = an.get_marches_par_region(region_choix)
            if all_marches:
                marche_choix = st.selectbox("Marché précis (optionnel)", ["— Non précisé —"] + all_marches, key="ana_marche")
                marche_choix = None if marche_choix == "— Non précisé —" else marche_choix

        unite_act = "kg"
        if produit_choix != "— Choisir —":
            unite_act = an.get_unite(produit_choix)
        hint_map = {"kg":"500","litre":"800","pièce":"350","régime":"1200","botte":"150","douzaine":"1200"}
        hint = f"ex: {hint_map.get(unite_act,'500')} FCFA/{unite_act}"

        prix_input = st.number_input(f"Prix proposé (FCFA / {unite_act})", min_value=0, max_value=50000, value=0, step=10, help=hint, key="ana_prix")

        # Deux boutons côte à côte
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔍 Lancer l'Analyse AgriPulse", key="btn_analyse"):
                if produit_choix == "— Choisir —" or region_choix == "— Choisir —" or prix_input <= 0:
                    st.warning("⚠️ Veuillez compléter tous les champs (produit, région, prix > 0).")
                else:
                    with st.spinner("🧠 Analyse ML en cours…"):
                        res = an.analyse_complete(produit_choix, region_choix, float(prix_input))
                        residus = np.array(res["historique_prix"]) - np.array(res["fitted"])
                        std_res = np.std(residus) if len(residus) > 1 else 0
                        prix_moyen_hist = np.mean(res["historique_prix"]) if len(res["historique_prix"]) > 0 else 1
                        confiance = max(0, min(100, 100 * (1 - std_res / prix_moyen_hist))) if prix_moyen_hist > 0 else 70
                        res["confiance"] = confiance
                        reco = rec.generer_recommandations(
                            produit=produit_choix, region=region_choix, marche=marche_choix or "",
                            prix_propose=prix_input, prix_actuel=res["prix_actuel_marche"],
                            tendance=res["tendance"], predictions=res["predictions"],
                            unite=res["unite"], diff_pct=res["diff_pct"], r2=res["r2"],
                            kmeans_labels=res["kmeans"].get("labels"),
                            kmeans_regions=res["kmeans"].get("regions"),
                        )
                        st.session_state.result = res
                        st.session_state.reco = reco
                        st.session_state.analyse_done = True
                        st.session_state.info_idx += 1
                        st.session_state.produit_choix = produit_choix
                        st.session_state.region_choix = region_choix
                    st.toast("✅ Analyse terminée", icon="🎉")
                    st.success("✅ Analyse terminée — consultez les recommandations à droite →")
        with col_btn2:
            if st.button("🔄 Nouvelle analyse", key="btn_reset_analyse"):
                reset_analyse_fields()

    # -------------------------------------------------------------------
    # ONGLET COLLECTE TERRAIN
    # -------------------------------------------------------------------
    with tab_terrain:
        st.markdown("""
        <div class="card c-grn" style="padding:12px; margin-bottom:16px; font-size:14px; color:#0f172a;">
          ✅ Enregistrez vos observations de terrain. Elles seront vérifiées avant intégration. Merci pour votre contribution.
        </div>
        """, unsafe_allow_html=True)

        f_cat = st.selectbox("Catégorie d'aliment", ["— Choisir —"] + an.get_categories(), key="terrain_cat")
        f_prods = an.get_produits_par_categorie(f_cat if f_cat != "— Choisir —" else None)
        f_produit = st.selectbox("Produit observé", ["— Choisir —"] + f_prods, key="terrain_produit")

        regions_list = an.get_regions()
        def on_region_terrain_change():
            st.session_state.region_terrain = st.session_state.terrain_region
        f_region = st.selectbox("Région", ["— Choisir —"] + regions_list, key="terrain_region", on_change=on_region_terrain_change)
        if f_region != "— Choisir —" and st.session_state.region_terrain != f_region:
            st.session_state.region_terrain = f_region

        if f_region != "— Choisir —":
            all_marches = an.get_marches_par_region(f_region)
            f_marche = st.selectbox("Marché", all_marches, key="terrain_marche")
        else:
            f_marche = st.selectbox("Marché", ["— Sélectionnez d'abord une région —"], key="terrain_marche_vide")

        unite_f = an.get_unite(f_produit) if f_produit not in ("— Choisir —", None) else "kg"
        f_prix = st.number_input(f"Prix observé (FCFA / {unite_f})", min_value=50, step=10, key="terrain_prix")

        today_date = pd.Timestamp.today().date()
        st.markdown(f"""
        <div style="margin-bottom: 12px;">
            <label style="font-size:14px; font-weight:600; color: #1e293b;">Date d'observation</label>
            <div class="locked-date">
                <strong>{today_date.strftime('%d/%m/%Y')}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        f_date = today_date

        f_comm = st.text_area("Commentaire (optionnel)", placeholder="ex: qualité, vendeur, conditions du marché…", key="terrain_comm", height=80)

        col_btn3, col_btn4 = st.columns(2)
        with col_btn3:
            if st.button("💾 Enregistrer l'observation", key="btn_terrain"):
                TERRAIN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "donnees_terrain.csv")
                os.makedirs(os.path.dirname(TERRAIN_PATH), exist_ok=True)

                if (f_produit == "— Choisir —" or f_region == "— Choisir —"
                        or f_marche == "— Sélectionnez d'abord une région —" or f_prix <= 50):
                    st.warning("⚠️ Veuillez compléter tous les champs (produit, région, marché, prix > 50 FCFA).")
                else:
                    new_row = pd.DataFrame([{
                        "date": f_date.isoformat(), "annee": f_date.year, "mois": f_date.month,
                        "region": f_region, "marche": f_marche, "categorie": "Utilisateur",
                        "produit": f_produit, "unite": an.get_unite(f_produit),
                        "prix_fcfa": f_prix, "source": "Terrain", "commentaire": f_comm,
                    }])

                    try:
                        if os.path.exists(TERRAIN_PATH):
                            existing = pd.read_csv(TERRAIN_PATH, encoding="utf-8-sig")
                            df_terrain = pd.concat([existing, new_row], ignore_index=True)
                        else:
                            df_terrain = new_row
                        df_terrain.to_csv(TERRAIN_PATH, index=False, encoding="utf-8-sig")

                        st.toast("📥 Observation enregistrée !", icon="✅")
                        st.success(f"""
                        ✅ **Merci pour votre contribution !**  
                        Vos données ont été enregistrées et seront vérifiées avant intégration à la base principale.  
                        **Récapitulatif :**  
                        - Produit : {f_produit}  
                        - Région : {f_region}  
                        - Marché : {f_marche}  
                        - Prix : {f_prix:,} FCFA / {unite_f}  
                        - Date : {f_date.strftime('%d/%m/%Y')}  
                        🤝 Merci de contribuer à l'intelligence agricole camerounaise.
                        """)
                    except Exception as e:
                        st.error(f"❌ Erreur d'enregistrement : {e}")
        with col_btn4:
            if st.button("🧹 Réinitialiser", key="btn_reset_terrain"):
                reset_terrain_fields()

# ═══════════════════════════════════════════════════════════════════════
# COLONNE CENTRE – CARTE + TENDANCES
# ═══════════════════════════════════════════════════════════════════════
with col_carte:
    st.markdown('<div class="h-sec">🗺️ Cartographie des Prix — Cameroun</div>', unsafe_allow_html=True)

    region_for_map = None
    if st.session_state.region_terrain and st.session_state.region_terrain != "— Choisir —":
        region_for_map = st.session_state.region_terrain
    elif st.session_state.region_analyse and st.session_state.region_analyse != "— Choisir —":
        region_for_map = st.session_state.region_analyse
    elif st.session_state.analyse_done and st.session_state.get('region_choix'):
        region_for_map = st.session_state.region_choix

    prod_carte = st.session_state.get('produit_choix') if st.session_state.analyse_done else None
    df_heat = pd.DataFrame(an.get_heatmap_data(prod_carte))
    r_coords_df = pd.DataFrame([{"region":r,"lat":v["lat"],"lon":v["lon"],"chef_lieu":v["chef_lieu"]}
                                for r,v in rec.REGION_COORDS.items()])
    df_map = df_heat.merge(r_coords_df, on="region", how="left")
    if not df_map.empty and "prix_moyen" in df_map.columns:
        pmin, pmax = df_map["prix_moyen"].min(), df_map["prix_moyen"].max()
        df_map["pn"] = (df_map["prix_moyen"] - pmin) / (pmax - pmin + 1)
    else:
        df_map["pn"] = 0.5

    if region_for_map and region_for_map != "— Choisir —":
        ri = rec.REGION_COORDS.get(region_for_map, {"lat":5.5,"lon":12.3})
        clat, clon = ri["lat"], ri["lon"]
        zoom_level = 8
        if region_for_map in ["Littoral", "Centre", "Ouest"]:
            zoom_level = 9
        elif region_for_map in ["Extrême-Nord", "Nord", "Adamaoua"]:
            zoom_level = 7
        else:
            zoom_level = 8
    else:
        clat, clon, zoom_level = 5.5, 12.3, 5

    fig_map = go.Figure()
    for _, row in df_map.iterrows():
        if pd.isna(row.get("lat")): continue
        pv = int(row["prix_moyen"]) if not pd.isna(row.get("prix_moyen", np.nan)) else 0
        n = float(row["pn"]) if not pd.isna(row.get("pn", np.nan)) else 0.5
        rc = int(n*220); gc = int((1-n)*180+60)
        fig_map.add_trace(go.Scattermapbox(
            lat=[row["lat"]], lon=[row["lon"]], mode="markers+text",
            marker=dict(size=27+n*22, color=f"rgba({rc},{gc},40,.85)", opacity=.9),
            text=[row["chef_lieu"]], textposition="top center",
            textfont=dict(color="#fff",size=11,family="Inter"),
            name=row["region"],
            customdata=[[row["region"],pv,row.get("chef_lieu","")]],
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[2]}<br>Prix moy: <b>%{customdata[1]:,} FCFA</b><extra></extra>",
            showlegend=False))

    if region_for_map and region_for_map != "— Choisir —":
        df_raw = an.load_data()
        for mn in an.get_marches_par_region(region_for_map):
            if mn not in rec.MARCHE_COORDS: continue
            mlat,mlon = rec.MARCHE_COORDS[mn]
            pm = df_raw[df_raw["marche"]==mn]["prix_fcfa"].mean()
            pm = int(pm) if not np.isnan(pm) else 0
            fig_map.add_trace(go.Scattermapbox(
                lat=[mlat], lon=[mlon], mode="markers+text",
                marker=dict(size=12, color="#16a34a", opacity=.95),
                text=[mn.replace("Marché de ","").replace("Marché ","")[:14]],
                textposition="bottom right",
                textfont=dict(color="#0f172a",size=10,family="Inter"),
                hovertemplate=f"<b>{mn}</b><br>Prix moy: {pm:,} FCFA<extra></extra>",
                showlegend=False))

    fig_map.update_layout(
        mapbox=dict(style="carto-positron", center=dict(lat=clat, lon=clon), zoom=zoom_level),
        margin=dict(l=0,r=0,t=0,b=0), height=480,
        paper_bgcolor="rgba(0,0,0,0)", showlegend=False, uirevision="map")
    st.plotly_chart(fig_map, use_container_width=True,
        config={"displayModeBar":True,"scrollZoom":True,
                "modeBarButtonsToRemove":["toImage","sendDataToCloud"],"displaylogo":False})

    st.markdown("""
    <div style="display:flex;align-items:center;gap:8px;margin:-8px 0 12px;font-size:12px;color:var(--txt3)">
      <span style="font-weight:700">Prix :</span>
      <span style="background:linear-gradient(to right,rgba(60,180,60,.7),rgba(220,180,40,.7),rgba(220,60,40,.7));
                  width:100px;height:7px;border-radius:4px;display:inline-block"></span>
      <span>Bas → Élevé &nbsp;·&nbsp; 🟢 Marchés locaux (après analyse)</span>
      <span style="margin-left:12px; font-style:italic;">💡 Passez la souris sur un point pour voir les détails</span>
    </div>
    """, unsafe_allow_html=True)

    # Graphique tendances
    st.markdown('<div class="h-sec">📈 Tendances & Prédictions</div>', unsafe_allow_html=True)
    if st.session_state.analyse_done and st.session_state.result:
        res = st.session_state.result
        ht = res["historique_t"]; hp = res["historique_prix"]
        ft = res["fitted"]; pr = res["predictions"]
        def t2l(t):
            mm=["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]
            return f"{mm[(t-1)%12]} {2019+(t-1)//12}"
        lh = [t2l(t) for t in ht]; tm = max(ht)
        lf = [t2l(tm+h) for h in [1,3,6]]
        vf = [pr["1_mois"],pr["3_mois"],pr["6_mois"]]
        fgt = go.Figure()
        fgt.add_trace(go.Scatter(x=lh+lh[::-1], y=[p*1.08 for p in hp]+[p*0.92 for p in hp[::-1]],
            fill="toself", fillcolor="rgba(22,163,74,.08)", line=dict(color="rgba(0,0,0,0)"), showlegend=False))
        fgt.add_trace(go.Scatter(x=lh, y=hp, mode="lines", name="Prix réel", line=dict(color="#16a34a", width=2.5)))
        fgt.add_trace(go.Scatter(x=lh, y=ft, mode="lines", name=f"Régression (R²={res['r2']:.3f})",
            line=dict(color="#f59e0b", width=2, dash="dot")))
        fgt.add_trace(go.Scatter(x=[lh[-1]]+lf, y=[hp[-1]]+vf, mode="lines+markers", name="Prédictions",
            line=dict(color="#2563eb", width=2.5, dash="dash"), marker=dict(size=10, color="#2563eb", symbol="diamond")))
        fgt.add_hline(y=res["prix_propose"], line_color="#dc2626", line_dash="dot",
            annotation_text=f"Votre prix: {int(res['prix_propose']):,} FCFA", annotation_font=dict(color="#dc2626", size=10))
        fgt.update_layout(
            height=250, margin=dict(l=0,r=0,t=8,b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#fefefe",
            font=dict(family="Inter", size=11, color="#1e293b"),
            legend=dict(font=dict(size=10, color="#1e293b"), bgcolor="rgba(255,255,255,.9)",
                        orientation="h", x=0, y=1.12, xanchor="left"),
            xaxis=dict(gridcolor="#e2e8f0", tickangle=-35, nticks=10,
                       tickfont=dict(color="#0f172a"), title_font=dict(color="#0f172a")),
            yaxis=dict(gridcolor="#e2e8f0", ticksuffix=" F",
                       tickfont=dict(color="#0f172a"), title_font=dict(color="#0f172a")),
            hovermode="x unified")
        st.plotly_chart(fgt, use_container_width=True, config={"displayModeBar":False})
        m1,m2,m3,m4 = st.columns(4)
        with m1: st.metric("Prix Marché", f"{res['prix_actuel_marche']:,} F")
        with m2: st.metric("Votre Prix", f"{int(res['prix_propose']):,} F", f"{res['diff_pct']:+.1f}%")
        with m3: st.metric("Préd. 3 mois", f"{pr['3_mois']:,} F")
        with m4: st.metric("R² Modèle", f"{res['r2']:.3f}")
    else:
        df_all = an.load_data()
        avg_dt = df_all.groupby("date")["prix_fcfa"].mean().reset_index()
        avg_dt.columns = ["date","prix"]
        avg_dt = avg_dt.sort_values("date").tail(72)
        fgd = go.Figure()
        fgd.add_trace(go.Scatter(x=avg_dt["date"].astype(str), y=avg_dt["prix"], mode="lines", fill="tozeroy",
            fillcolor="rgba(22,163,74,.08)", line=dict(color="#16a34a", width=2.5)))
        fgd.update_layout(
            height=250, margin=dict(l=0,r=0,t=20,b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#fefefe",
            font=dict(family="Inter", size=11, color="#1e293b"),
            xaxis=dict(gridcolor="#e2e8f0", tickangle=-35, nticks=10,
                       tickfont=dict(color="#0f172a"), title_font=dict(color="#0f172a")),
            yaxis=dict(gridcolor="#e2e8f0", ticksuffix=" F",
                       tickfont=dict(color="#0f172a"), title_font=dict(color="#0f172a")),
            title=dict(text="Indice Prix Moyen — Tous Produits | 2019-2024",
                       font=dict(size=12, color="#1e293b", family="Inter"), x=.5),
            showlegend=False)
        st.plotly_chart(fgd, use_container_width=True, config={"displayModeBar":False})
# ═══════════════════════════════════════════════════════════════════════
# COLONNE DROITE – Résultats (Visualisations ML, puis Prédictions, puis Recommandations)
# ═══════════════════════════════════════════════════════════════════════
with col_r:
    # ----- 1. Visualisations ML (en premier) -----
    if st.session_state.analyse_done and st.session_state.result:
        res = st.session_state.result
        st.markdown('<div class="h-sec">📊 Visualisations ML — INF 232 EC2</div>', unsafe_allow_html=True)
        t_reg, t_km, t_clf = st.tabs(["📈 Régression", "🔵 K-Means", "🏷️ Classif."])

        with t_reg:
            ht = res["historique_t"]; hp = res["historique_prix"]
            ft = res["fitted"]; pr = res["predictions"]
            def t2l(t):
                mm=["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]
                return f"{mm[(t-1)%12]} {2019+(t-1)//12}"
            lh = [t2l(t) for t in ht]; tm = max(ht)
            lf = [t2l(tm+h) for h in [1,3,6]]
            vf = [pr["1_mois"],pr["3_mois"],pr["6_mois"]]
            fg = go.Figure()
            fg.add_trace(go.Scatter(x=lh+lh[::-1], y=[p*1.08 for p in hp]+[p*0.92 for p in hp[::-1]],
                fill="toself", fillcolor="rgba(22,163,74,.07)", line=dict(color="rgba(0,0,0,0)"), showlegend=False))
            fg.add_trace(go.Scatter(x=lh, y=hp, mode="lines", name="Prix réel", line=dict(color="#16a34a", width=2)))
            fg.add_trace(go.Scatter(x=lh, y=ft, mode="lines", name=f"Régression R²={res['r2']:.2f}",
                line=dict(color="#f59e0b", width=2, dash="dot")))
            fg.add_trace(go.Scatter(x=[lh[-1]]+lf, y=[hp[-1]]+vf, mode="lines+markers", name="Prédictions",
                line=dict(color="#2563eb", width=2.5, dash="dash"), marker=dict(size=9, color="#2563eb", symbol="diamond")))
            fg.add_hline(y=res["prix_propose"], line_color="#dc2626", line_dash="dot",
                annotation_text=f"Votre prix: {int(res['prix_propose']):,}", annotation_font=dict(color="#dc2626", size=10))
            fg.update_layout(
                height=260, margin=dict(l=0,r=0,t=5,b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#fafafa",
                font=dict(family="Inter", size=10, color="#1e293b"),
                legend=dict(font=dict(size=9, color="#1e293b"), bgcolor="rgba(255,255,255,.85)", x=0, y=1.02, orientation="h"),
                xaxis=dict(gridcolor="#e2e8f0", tickangle=-35, nticks=7,
                           tickfont=dict(color="#0f172a"), title_font=dict(color="#0f172a")),
                yaxis=dict(gridcolor="#e2e8f0", ticksuffix=" F",
                           tickfont=dict(color="#0f172a"), title_font=dict(color="#0f172a")),
                hovermode="x unified")
            # ---- Bloc pour bloquer l'échelle Y ----
            data_min = min(hp) * 0.85
            data_max = max(hp) * 1.15
            fg.update_yaxes(range=[data_min, data_max])

            if res["prix_propose"] > data_max:
                fg.add_annotation(
                    x=0.5, y=1.05, xref="paper", yref="paper",
                    text=f"⚠️ Prix proposé ({int(res['prix_propose']):,} FCFA) hors échelle",
                    showarrow=False,
                    font=dict(color="#dc2626", size=9),
                    bgcolor="rgba(255,255,255,0.8)"
                )
            # ---------------------------------------
            st.plotly_chart(fg, use_container_width=True, config={"displayModeBar":False})
            rm = an.regression_multiple(st.session_state.get('produit_choix', ''))
            if "error" not in rm:
                st.markdown(f"""
                <div class="card c-blu" style="padding:12px; font-size:13px">
                  <div class="h-crd">📐 Régression Multiple <span class="badge-grn">R²={rm['r2']}</span></div>
                  <div class="lxs">Variables : temps · mois · région · {rm['n_obs']:,} observations</div>
                </div>""", unsafe_allow_html=True)

        with t_km:
            km = res["kmeans"]
            sil = km.get("silhouette_score",0)
            rk = km.get("regions",[]); lk = km.get("labels",[]); sk = km.get("silhouette_samples",[]); c2 = km.get("coordonnees_2d",[])
            if rk and sk:
                df_sil = pd.DataFrame({"R":rk,"S":sk,"C":[f"C{l+1}" for l in lk]}).sort_values("S",ascending=True)
                pal = ["#16a34a","#f59e0b","#dc2626","#2563eb","#7c3aed"]
                cm = {f"C{i+1}":pal[i%len(pal)] for i in range(km["k"])}
                fig_s = go.Figure()
                for cl in df_sil["C"].unique():
                    sub = df_sil[df_sil["C"]==cl]
                    fig_s.add_trace(go.Bar(y=sub["R"], x=sub["S"], orientation="h", name=cl,
                        marker_color=cm.get(cl,"#16a34a"), marker_line_width=0,
                        text=sub["S"].round(3), textposition="outside", textfont=dict(color="#0f172a", size=9)))
                fig_s.add_vline(x=sil, line_dash="dash", line_color="#1a202c",
                    annotation_text=f"Moy {sil:.2f}", annotation_font=dict(size=9, color="#1a202c"))
                fig_s.update_layout(
                    height=200, margin=dict(l=0,r=0,t=4,b=0),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#fafafa",
                    font=dict(family="Inter", size=9, color="#1e293b"),
                    xaxis=dict(gridcolor="#e2e8f0", title="Silhouette", tickfont=dict(color="#0f172a"),
                               title_font=dict(color="#0f172a")),
                    yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color="#0f172a"),
                               title_font=dict(color="#0f172a")),
                    barmode="stack", showlegend=True,
                    legend=dict(font=dict(size=8, color="#1e293b"), bgcolor="rgba(255,255,255,.85)"))
                st.plotly_chart(fig_s, use_container_width=True, config={"displayModeBar":False})
                if c2 and len(c2)==len(rk):
                    df2 = pd.DataFrame(c2, columns=["PC1","PC2"])
                    df2["R"]=rk; df2["C"]=[f"C{l+1}" for l in lk]
                    fig2 = go.Figure()
                    for cl in df2["C"].unique():
                        s=df2[df2["C"]==cl]
                        fig2.add_trace(go.Scatter(x=s["PC1"], y=s["PC2"], mode="markers+text", name=cl,
                            marker=dict(size=12, color=cm.get(cl,"#16a34a"), opacity=.85),
                            text=s["R"], textposition="top center", textfont=dict(size=9, color="#0f172a")))
                    fig2.update_layout(
                        height=190, margin=dict(l=0,r=0,t=18,b=0),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#fafafa",
                        font=dict(family="Inter", size=9, color="#1e293b"),
                        showlegend=False,
                        title=dict(text="ACP 2D — Projection Régions", font=dict(size=10, color="#1e293b"), x=.5),
                        xaxis=dict(title="PC1", gridcolor="#e2e8f0", tickfont=dict(color="#0f172a"),
                                   title_font=dict(color="#0f172a")),
                        yaxis=dict(title="PC2", gridcolor="#e2e8f0", tickfont=dict(color="#0f172a"),
                                   title_font=dict(color="#0f172a")))
                    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

        with t_clf:
            clf = res.get("classification",{})
            if "error" not in clf and clf:
                acc = clf.get("accuracy",0); imp = clf.get("importances",{}); seuils = clf.get("seuils",{})
                pa = res["prix_actuel_marche"]
                cl_map = {"Bas":"#dc2626","Moyen":"#f59e0b","Élevé":"#16a34a"}
                classe = "Bas" if pa<=seuils.get("bas",0) else ("Moyen" if pa<=seuils.get("moyen",0) else "Élevé")
                col_cl = cl_map.get(classe,"#4a5568")
                st.markdown(f"""
                <div class="card c-grn" style="padding:12px; text-align:center">
                  <div class="lxs">Niveau de prix prédit (Random Forest)</div>
                  <div style="font-size:1.7rem; font-weight:800; color:{col_cl}; font-family:'JetBrains Mono',monospace">{classe}</div>
                  <div class="lxs">Accuracy {acc*100:.1f}% &nbsp;·&nbsp; Seuil bas ≤ {seuils.get('bas',0):,} F | moyen ≤ {seuils.get('moyen',0):,} F</div>
                </div>""", unsafe_allow_html=True)
                if imp:
                    fi = go.Figure(go.Bar(x=list(imp.values()), y=list(imp.keys()), orientation="h",
                        marker_color=["#16a34a","#f59e0b","#2563eb"], marker_line_width=0,
                        text=list(imp.values()), textposition="outside", textfont=dict(color="#0f172a", size=9)))
                    fi.update_layout(
                        height=140, margin=dict(l=0,r=0,t=18,b=0),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#fafafa",
                        font=dict(family="Inter", size=9, color="#1e293b"),
                        title=dict(text="Importance des variables", font=dict(size=10, color="#1e293b"), x=.5),
                        xaxis=dict(gridcolor="#e2e8f0", tickfont=dict(color="#0f172a"),
                                   title_font=dict(color="#0f172a")),
                        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color="#0f172a"),
                                   title_font=dict(color="#0f172a")))
                    st.plotly_chart(fi, use_container_width=True, config={"displayModeBar":False})
            else:
                st.info("Données insuffisantes pour la classification.")

        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ----- 2. Prédictions de prix (maintenant en-dessous) -----
    if st.session_state.analyse_done and st.session_state.result:
        res = st.session_state.result
        p1 = res["predictions"]["1_mois"]
        p3 = res["predictions"]["3_mois"]
        p6 = res["predictions"]["6_mois"]
        pa = res["prix_actuel_marche"]
        def delta(p): return f"+{int((p-pa)/pa*100)}%" if pa>0 else ""

        conf = res.get("confiance", 70)
        st.markdown('<div class="h-sec">📊 Prédictions de prix</div>', unsafe_allow_html=True)
        col_pr1, col_pr2, col_pr3 = st.columns(3)
        with col_pr1: st.metric("+1 mois", f"{p1:,} FCFA", delta(p1))
        with col_pr2: st.metric("+3 mois", f"{p3:,} FCFA", delta(p3))
        with col_pr3: st.metric("+6 mois", f"{p6:,} FCFA", delta(p6))

        st.markdown(f"""
        <div style="margin: 12px 0 8px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
                <span>🔒 Confiance de la prédiction</span>
                <span><strong>{conf:.0f}%</strong></span>
            </div>
            <div style="background-color: #e2e8f0; border-radius: 10px; height: 8px; width: 100%;">
                <div style="background-color: #16a34a; width: {conf:.0f}%; height: 8px; border-radius: 10px;"></div>
            </div>
            <div style="font-size: 11px; color: #475569; margin-top: 4px;">
                Basée sur l'écart type des erreurs passées
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ----- 3. Recommandations AgriPulse -----
    st.markdown('<div class="h-sec">🤖 Recommandations AgriPulse || Visualisations ML </div>', unsafe_allow_html=True)
    if st.session_state.analyse_done and st.session_state.reco:
        res = st.session_state.result
        reco = st.session_state.reco
        diff = res["diff_pct"]
        if diff < -15:
            bc = "c-red"; bm = f"⚠️ Votre prix est {abs(int(diff))}% sous le marché — risque de perte"
        elif diff > 15:
            bc = "c-grn"; bm = f"🟢 Votre prix est {int(diff)}% au-dessus du marché — excellente position"
        else:
            bc = "c-amb"; bm = f"✅ Prix aligné avec le marché (écart : {diff:+.1f}%)"
        st.markdown(f'<div class="card {bc}" style="padding:12px; font-size:14px; font-weight:600">{bm}</div>', unsafe_allow_html=True)

        # Nouveaux onglets : Logistique & Prix, Notes Techniques, Opportunité
        tl, tt, to = st.tabs(["🚛 Logistique & Prix", "📐 Notes Techniques", "💰 Opportunité"])

        with tl:
            logi = reco["logistique"]
            st.markdown(f'<div class="rcard c-amb"><h4>{logi["icon"]} {logi["titre"]}</h4><p>{logi["detail"]}</p></div>', unsafe_allow_html=True)
            astuces_r = [
                " Comparez les prix entre marchés frontaliers avant tout déplacement.",
                " Un groupement de 5 producteurs divise les frais logistiques par 4.",
                "En saison des pluies, privilégiez les routes bitumées accessibles.",
                " Négociez en fin de journée — les vendeurs sont plus flexibles.",
                " Vérifiez les prix par téléphone avant de vous déplacer.",
            ]
            for a in random.sample(astuces_r, 2):
                st.markdown(f'<div style="background:var(--bg3); border:1px dashed var(--brd2); border-radius:8px; padding:10px; font-size:13px; color:var(--txt2); margin-bottom:8px">{a}</div>', unsafe_allow_html=True)

        with tt:
            tech = reco["technique"]
            st.markdown(f'''
            <div class="rcard c-blu"><h4>{tech["icon"]} {tech["titre"]}</h4><p>{tech["detail"]}</p></div>
            <div class="card" style="padding:14px; font-size:13px">
              <div class="h-crd"> Notes Techniques — INF 232 EC2</div>
              <ul style="color:var(--txt2); line-height:1.8; padding-left:20px; margin:8px 0">
                <li>AgriPulse : <strong>94 080 relevés</strong> (2019–2024)</li>
                <li><strong>64 produits</strong> : tomate → café robusta</li>
                <li><strong>10 régions</strong> · 50 marchés du Cameroun</li>
                <li>Modèles : Régression · K-Means · Random Forest · ACP</li>
                <li>Source : <a href="https://data.humdata.org/dataset/wfp-food-prices-for-cameroon" target="_blank" style="color:var(--blu)">WFP Humandata</a></li>
              </ul>
            </div>''', unsafe_allow_html=True)

        with to:
            opp = reco["opportunite"]
            st.markdown(f'<div class="rcard"><h4>{opp["icon"]} {opp["titre"]}</h4><p>{opp["detail"]}</p></div>', unsafe_allow_html=True)

    else:
        st.info("Lancez une analyse pour voir les prédictions et recommandations personnalisées.")

        # Ordre par défaut : Logistique & Prix, Notes Techniques, Opportunité
        tl0, tt0, to0 = st.tabs(["🚛 Logistique & Prix", "📐 Notes Techniques", "💰 Opportunité"])

        with tl0:
            astuces_def = [
                "🚛 Comparez toujours les prix entre marchés frontaliers pour optimiser vos coûts de transport.",
                "📦 Regroupez-vous avec d'autres producteurs pour partager les frais logistiques.",
                "🗓️ Planifiez vos ventes selon les jours de marché hebdomadaires locaux.",
                "⚖️ Vérifiez la qualité de vos produits avant tout déplacement — le refus coûte cher.",
                "📞 Appelez un acheteur de confiance avant de vous rendre sur un marché distant.",
            ]
            for a in astuces_def:
                st.markdown(f'<div style="background:var(--bg3); border:1px dashed var(--brd2); border-radius:8px; padding:10px; font-size:13px; color:var(--txt2); margin-bottom:8px">{a}</div>', unsafe_allow_html=True)

        with tt0:
            st.markdown("""
            <div class="card" style="padding:14px; font-size:13px">
              <div class="h-crd"> Notes Techniques — INF 232 EC2</div>
              <ul style="color:var(--txt2); line-height:1.9; padding-left:20px; margin:8px 0">
                <li>AgriPulse : <strong>94 080 relevés de prix</strong> (2019–2024)</li>
                <li><strong>64 produits agricoles</strong> : tomate → café robusta</li>
                <li><strong>10 régions</strong> et 50 marchés du Cameroun couverts</li>
                <li>Algorithmes : Régression Linéaire Simple & Multiple, K-Means, ACP, Random Forest</li>
                <li>Variations saisonnières modélisées (saison sèche / pluies)</li>
              </ul>
              <div style="font-size:11px; color:var(--txt3); margin-top:6px">
                Source : <a href="https://data.humdata.org/dataset/wfp-food-prices-for-cameroon" target="_blank" style="color:var(--blu)">WFP Food Prices for Cameroon — humdata.org</a>
              </div>
            </div>""", unsafe_allow_html=True)

        with to0:
            st.markdown("""
            <div class="card c-grn" style="padding:14px">
              <div class="h-crd"> Opportunité de Vente</div>
              <p class="btxt">Sélectionnez un produit pour obtenir des <strong>conseils stratégiques</strong>
              sur le moment idéal de vente, les marchés les plus rentables et les tendances saisonnières au Cameroun.</p>
            </div>""", unsafe_allow_html=True)
            for a in random.sample(rec.ASTUCES, min(3, len(rec.ASTUCES))):
                st.markdown(f'<div style="background:var(--bg3); border-radius:8px; padding:10px; font-size:13px; color:var(--txt2); margin-bottom:8px">{a}</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="ft-bar">
      Propulsé par <strong>AgriPulse</strong> · TP232 EC2 ,UY1 🇨🇲<br>
      <span style="font-size:11px">data.humdata.org/wfp-food-prices-for-cameroon</span>
    </div>
    """, unsafe_allow_html=True)