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

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from data_prep import load_demandeurs, load_offres, load_ground_truth  # noqa: E402
from run_matching import generate_recommendations  # noqa: E402
from search import SearchEngine  # noqa: E402
from skill_gap import skill_gap  # noqa: E402
from branding import (  # noqa: E402
    render_header, render_footer, render_section_title, render_divider,
    render_banner_card, render_map_card, has_map_image, style_fig, gradient_colors,
    render_hero, render_kpi_row, render_card_open, render_page_intro, render_sidebar_nav,
    CG_GREEN, CG_GOLD, CG_RED, CG_RIVER, CG_BROWN, CG_OCHRE, CG_TERRA,
)

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
    for fname in ["recommandations_top10.csv.gz", "recommandations_top10.csv"]:
        reco_path = os.path.join(OUT_DIR, fname)
        if os.path.exists(reco_path) and os.path.getsize(reco_path) > 100:
            try:
                df = pd.read_csv(reco_path)
                if not df.empty:
                    return df
            except (pd.errors.EmptyDataError, pd.errors.ParserError):
                continue
    return generate_recommendations(_dem, _off, top_k=10)


@st.cache_resource(show_spinner="Indexation de la recherche...")
def get_search_engine():
    return SearchEngine(dem, off)


dem, off, gt = get_data()
reco = get_recommendations(dem, off)

render_header()

PAGES = ["📊 Vue d'ensemble", "🎯 Recommandations", "🔎 Recherche intelligente (Bonus 1)",
         "🧩 Écarts de compétences (Bonus 2)"]
page = render_sidebar_nav(PAGES)

# ----------------------------------------------------------------- Vue d'ensemble
if page == PAGES[0]:
    render_hero(
        headline="Chaque profil mérite la bonne opportunité, en un instant.",
        subheadline=(
            "Ce tableau de bord met en relation automatiquement les demandeurs d'emploi "
            "et les offres disponibles grâce à l'intelligence artificielle — pour que les "
            "conseillers de l'ACPE passent moins de temps à chercher, et plus de temps à accompagner."
        ),
        chips=[
            ("people", f"{len(dem):,}".replace(",", " ") + " candidats suivis"),
            ("briefcase", f"{len(off):,}".replace(",", " ") + " offres actives"),
            ("bolt", "Résultats en temps réel"),
        ],
    )

    n_secteurs = off[off["secteur"] != ""]["secteur"].nunique()
    taux_moyen = reco[reco["rank"] == 1]["score"].mean() if reco is not None else None
    render_kpi_row([
        {"icon": "people", "value": f"{len(dem):,}".replace(",", " "), "label": "Candidats enregistrés", "accent": CG_BROWN},
        {"icon": "briefcase", "value": f"{len(off):,}".replace(",", " "), "label": "Offres d'emploi actives", "accent": CG_GOLD},
        {"icon": "building", "value": str(n_secteurs), "label": "Secteurs représentés", "accent": CG_OCHRE},
        {"icon": "target", "value": f"{taux_moyen:.0%}" if taux_moyen is not None else "—", "label": "Compatibilité moyenne (meilleure offre)", "accent": CG_TERRA},
    ])

    render_divider()
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            render_card_open("Secteurs les plus représentés", "Offres d'emploi par secteur d'activité", icon="building")
            top_sect = off[off["secteur"] != ""]["secteur"].value_counts().head(10).reset_index()
            top_sect.columns = ["secteur", "nombre"]
            fig = px.bar(top_sect, x="nombre", y="secteur", orientation="h",
                         labels={"nombre": "Nombre d'offres d'emploi", "secteur": "Secteur d'activité"})
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=380)
            fig.update_traces(marker_line_width=0, marker_color=gradient_colors(top_sect["nombre"], "#E4DEFA", CG_BROWN))
            st.plotly_chart(style_fig(fig, "Top 10 des secteurs par nombre d'offres"), use_container_width=True)

    with col2:
        with st.container(border=True):
            render_card_open("Métiers les plus demandés", "Profils recherchés par les candidats", icon="people")
            top_metiers = dem[dem["qualification_metier"] != ""]["qualification_metier"].value_counts().head(10).reset_index()
            top_metiers.columns = ["métier", "nombre"]
            fig = px.bar(top_metiers, x="nombre", y="métier", orientation="h",
                         labels={"nombre": "Nombre de candidats", "métier": "Métier visé"})
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=380)
            fig.update_traces(marker_line_width=0, marker_color=gradient_colors(top_metiers["nombre"], "#F2E6C8", CG_GOLD))
            st.plotly_chart(style_fig(fig, "Top 10 des métiers par nombre de candidats"), use_container_width=True)

    render_divider()
    col3, col4 = st.columns([1.1, 1])
    lieu_counts = off[off["lieu"] != ""]["lieu"].value_counts().head(8).reset_index()
    lieu_counts.columns = ["lieu", "nombre"]
    with col3:
        with st.container(border=True):
            render_card_open("Répartition géographique", "Localisation des offres d'emploi", icon="map")
            if has_map_image():
                render_map_card("Répartition des offres d'emploi sur le territoire national")
            else:
                fig = px.pie(lieu_counts, names="lieu", values="nombre", hole=0.5,
                             color_discrete_sequence=[CG_BROWN, CG_GOLD, CG_TERRA, CG_OCHRE, CG_RIVER],
                             labels={"lieu": "Ville", "nombre": "Nombre d'offres"})
                fig.update_layout(height=360)
                st.plotly_chart(style_fig(fig, "Part des offres par ville"), use_container_width=True)

    with col4:
        with st.container(border=True):
            render_card_open("Top localités", "Nombre d'offres par ville", icon="chart")
            lieu_sorted = lieu_counts.sort_values("nombre")
            fig = px.bar(lieu_sorted, x="nombre", y="lieu", orientation="h",
                         labels={"nombre": "Nombre d'offres d'emploi", "lieu": "Ville"})
            fig.update_layout(height=210, margin=dict(t=5, l=5, r=5, b=5))
            fig.update_traces(marker_line_width=0, marker_color=gradient_colors(lieu_sorted["nombre"], "#E4DEFA", CG_BROWN))
            st.plotly_chart(style_fig(fig, "Classement des villes par nombre d'offres"), use_container_width=True)

        with st.container(border=True):
            render_card_open("Objectif des demandeurs", "", icon="target")
            obj_counts = dem["Objectif"].value_counts().reset_index()
            obj_counts.columns = ["objectif", "nombre"]
            fig = px.pie(obj_counts, names="objectif", values="nombre", hole=0.55,
                         color_discrete_sequence=[CG_BROWN, CG_GOLD, CG_TERRA],
                         labels={"objectif": "Objectif recherché", "nombre": "Nombre de candidats"})
            fig.update_layout(height=250, margin=dict(t=5, l=5, r=5, b=5))
            st.plotly_chart(style_fig(fig, "Répartition par objectif (emploi / stage / formation)"), use_container_width=True)


# ----------------------------------------------------------------- Recommandations
if page == PAGES[1]:
    render_page_intro(
        "target", "Recommandations générées",
        "Le Top-10 des offres les plus compatibles, calculé pour chacun des 41 298 candidats.",
        accent=CG_GOLD,
    )
    if reco is None:
        st.warning("Aucun fichier de recommandations trouvé. Lancez `python src/run_matching.py` d'abord.")
    else:
        with st.container(border=True):
            render_card_open("Statistiques sur les recommandations générées", "Distribution des scores calculés pour tous les candidats", icon="chart")
            c1, c2, c3 = st.columns(3)
            c1.metric("Candidats couverts", f"{reco['candidate_id'].nunique():,}".replace(",", " "))
            c2.metric("Score moyen (Top-1)", f"{reco[reco['rank']==1]['score'].mean():.1%}")
            c3.metric("Score médian (Top-1)", f"{reco[reco['rank']==1]['score'].median():.1%}")

            fig = px.histogram(reco[reco["rank"] == 1], x="score", nbins=40, color_discrete_sequence=[CG_BROWN],
                               labels={"score": "Score de compatibilité (meilleure offre)"})
            fig.update_traces(marker_line_width=0)
            fig.update_layout(bargap=0.05, yaxis_title="Nombre de candidats")
            fig.update_xaxes(tickformat=".0%")
            st.plotly_chart(style_fig(fig, "Distribution des scores de la meilleure offre par candidat"), use_container_width=True)

        render_divider()
        with st.container(border=True):
            render_card_open("Consulter les recommandations d'un candidat", "", icon="people")
            cid = st.selectbox("Choisir un candidat", options=sorted(reco["candidate_id"].unique())[:500])
            k = st.radio("Nombre de recommandations", [5, 10], horizontal=True)
            sub = reco[(reco["candidate_id"] == cid) & (reco["rank"] <= k)].merge(
                off[["id_offre", "intitule", "entreprise", "secteur", "lieu"]],
                left_on="job_id", right_on="id_offre", how="left",
            )
            st.dataframe(sub[["rank", "job_id", "intitule", "entreprise", "secteur", "lieu", "score"]],
                         use_container_width=True, hide_index=True)

# ----------------------------------------------------------------- Recherche (Bonus 1)
if page == PAGES[2]:
    render_page_intro(
        "search", "Recherche intelligente",
        "Bonus 1 — interrogez les offres ou les candidats en langage naturel, sans mot-clé exact.",
        accent=CG_OCHRE,
    )
    with st.container(border=True):
        render_card_open("Votre requête", "Ex : « développeur Python à Brazzaville », « comptable avec mobilité nationale »", icon="search")
        mode = st.radio("Rechercher parmi :", ["Offres", "Candidats"], horizontal=True)
        query = st.text_input("Votre requête")
        if query:
            engine = get_search_engine()
            if mode == "Offres":
                results = engine.search_offres(query, top_k=15)
                st.dataframe(results, use_container_width=True, hide_index=True)
            else:
                results = engine.search_candidats(query, top_k=15)
                st.dataframe(results, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------- Skill gap (Bonus 2)
if page == PAGES[3]:
    render_page_intro(
        "puzzle", "Écarts de compétences",
        "Bonus 2 — pour une paire candidat/offre, identifiez les compétences déjà couvertes et celles qui manquent.",
        accent=CG_TERRA,
    )
    with st.container(border=True):
        render_card_open("Analyse de compatibilité", "Disponible pour les offres issues du fichier d'extension (compétences détaillées).", icon="puzzle")
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
                    st.markdown(f"- **{c}**")
            with col_b:
                st.markdown("**⚠️ Compétences manquantes**")
                for c in result["competences_manquantes"] or ["(aucune)"]:
                    st.markdown(f"- **{c}**")

render_footer()
