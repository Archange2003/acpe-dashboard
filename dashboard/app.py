"""
Hackathon IndabaX Congo 2026 — Tableau de bord décisionnel
=============================================================
Dashboard destiné aux conseillers de l'ACPE : indicateurs clés, répartition
sectorielle/géographique, statistiques sur les recommandations générées, et
recherche en langage naturel (Bonus 1) / analyse skill gap (Bonus 2).

Lancer avec :
    streamlit run dashboard/app.py
"""

import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from data_prep import load_demandeurs, load_offres, load_ground_truth  # noqa: E402
from run_matching import generate_recommendations  # noqa: E402
from search import SearchEngine  # noqa: E402
from skill_gap import skill_gap  # noqa: E402

st.set_page_config(page_title="ACPE — Tableau de bord d'appariement", layout="wide", page_icon="🧭")

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")


@st.cache_data(show_spinner="Chargement des données...")
def get_data():
    dem = load_demandeurs()
    off = load_offres()
    gt = load_ground_truth()
    return dem, off, gt


@st.cache_data(show_spinner="Calcul des recommandations pour l'ensemble des candidats (une seule fois, ~30s)...")
def get_recommendations(_dem, _off):
    reco_path = os.path.join(OUT_DIR, "recommandations_top10.csv")
    if os.path.exists(reco_path):
        return pd.read_csv(reco_path)
    return generate_recommendations(_dem, _off, top_k=10)


@st.cache_resource(show_spinner="Indexation de la recherche...")
def get_search_engine():
    return SearchEngine()


dem, off, gt = get_data()
reco = get_recommendations(dem, off)

st.title("🧭 Tableau de bord décisionnel — Appariement Demandeurs / Offres")
st.caption("Agence Congolaise pour l'Emploi (ACPE) — Hackathon IndabaX Congo 2026")

tab_overview, tab_reco, tab_search, tab_skillgap = st.tabs(
    ["📊 Vue d'ensemble", "🎯 Recommandations", "🔎 Recherche intelligente (Bonus 1)", "🧩 Écarts de compétences (Bonus 2)"]
)

# ----------------------------------------------------------------- Vue d'ensemble
with tab_overview:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Candidats", f"{len(dem):,}".replace(",", " "))
    c2.metric("Offres d'emploi", f"{len(off):,}".replace(",", " "))
    n_secteurs = off[off["secteur"] != ""]["secteur"].nunique()
    c3.metric("Secteurs représentés (offres)", n_secteurs)
    if reco is not None:
        taux_moyen = reco[reco["rank"] == 1]["score"].mean()
        c4.metric("Score moyen (meilleure offre / candidat)", f"{taux_moyen:.0%}")
    else:
        c4.metric("Score moyen", "—")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Secteurs les plus représentés (offres)")
        top_sect = off[off["secteur"] != ""]["secteur"].value_counts().head(10).reset_index()
        top_sect.columns = ["secteur", "nombre"]
        fig = px.bar(top_sect, x="nombre", y="secteur", orientation="h", color="nombre",
                     color_continuous_scale="Blues")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Métiers les plus demandés (candidats)")
        top_metiers = dem[dem["qualification_metier"] != ""]["qualification_metier"].value_counts().head(10).reset_index()
        top_metiers.columns = ["métier", "nombre"]
        fig = px.bar(top_metiers, x="nombre", y="métier", orientation="h", color="nombre",
                     color_continuous_scale="Oranges")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Répartition géographique des offres")
        lieu_counts = off[off["lieu"] != ""]["lieu"].value_counts().head(12).reset_index()
        lieu_counts.columns = ["lieu", "nombre"]
        fig = px.pie(lieu_counts, names="lieu", values="nombre", hole=0.45)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("Objectif des demandeurs")
        obj_counts = dem["Objectif"].value_counts().reset_index()
        obj_counts.columns = ["objectif", "nombre"]
        fig = px.pie(obj_counts, names="objectif", values="nombre", hole=0.45)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------- Recommandations
with tab_reco:
    if reco is None:
        st.warning("Aucun fichier de recommandations trouvé. Lancez `python src/run_matching.py` d'abord.")
    else:
        st.subheader("Statistiques sur les recommandations générées")
        c1, c2, c3 = st.columns(3)
        c1.metric("Candidats couverts", f"{reco['candidate_id'].nunique():,}".replace(",", " "))
        c2.metric("Score moyen (Top-1)", f"{reco[reco['rank']==1]['score'].mean():.1%}")
        c3.metric("Score médian (Top-1)", f"{reco[reco['rank']==1]['score'].median():.1%}")

        fig = px.histogram(reco[reco["rank"] == 1], x="score", nbins=40,
                            title="Distribution des scores de la meilleure offre par candidat")
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("Consulter les recommandations d'un candidat")
        cid = st.selectbox("Choisir un candidat", options=sorted(reco["candidate_id"].unique())[:500])
        k = st.radio("Nombre de recommandations", [5, 10], horizontal=True)
        sub = reco[(reco["candidate_id"] == cid) & (reco["rank"] <= k)].merge(
            off[["id_offre", "intitule", "entreprise", "secteur", "lieu"]],
            left_on="job_id", right_on="id_offre", how="left",
        )
        st.dataframe(sub[["rank", "job_id", "intitule", "entreprise", "secteur", "lieu", "score"]],
                     use_container_width=True, hide_index=True)

# ----------------------------------------------------------------- Recherche (Bonus 1)
with tab_search:
    st.subheader("Recherche en langage naturel")
    st.caption("Ex : « développeur Python à Brazzaville », « comptable avec mobilité nationale »")
    mode = st.radio("Rechercher parmi :", ["Offres", "Candidats"], horizontal=True)
    query = st.text_input("Votre requête")
    if query:
        engine = get_search_engine()
        if mode == "Offres":
            st.dataframe(engine.search_offres(query, top_k=15), use_container_width=True, hide_index=True)
        else:
            st.dataframe(engine.search_candidats(query, top_k=15), use_container_width=True, hide_index=True)

# ----------------------------------------------------------------- Skill gap (Bonus 2)
with tab_skillgap:
    st.subheader("Analyse des écarts de compétences")
    st.caption("Disponible pour les offres issues du fichier d'extension (compétences détaillées).")
    ext_offers = off[off["competences"] != ""]
    if ext_offers.empty:
        st.info("Aucune offre avec compétences détaillées disponible.")
    else:
        cid2 = st.selectbox("Candidat", options=sorted(dem["id_demandeur"].unique())[:500], key="sg_cand")
        jid2 = st.selectbox(
            "Offre", options=ext_offers["id_offre"] + " — " + ext_offers["intitule"],
        )
        jid2_clean = jid2.split(" — ")[0]
        result = skill_gap(cid2, jid2_clean, dem, off)
        st.metric("Compatibilité compétences", f"{result['compatibilite_competences_pct']}%")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**✅ Compétences couvertes**")
            for c in result["competences_couvertes"] or ["(aucune)"]:
                st.markdown(f"- {c}")
        with col_b:
            st.markdown("**⚠️ Compétences manquantes**")
            for c in result["competences_manquantes"] or ["(aucune)"]:
                st.markdown(f"- {c}")

st.divider()
st.caption("Prototype réalisé dans le cadre du Hackathon IndabaX Congo 2026 — moteur d'appariement TF-IDF + règles métier.")
