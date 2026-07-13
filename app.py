"""
Hackathon IndabaX Congo 2026 — Tableau de bord décisionnel
=============================================================
Dashboard destiné aux conseillers de l'ACPE : indicateurs clés, répartition
sectorielle/géographique, statistiques sur les recommandations générées, et
recherche en langage naturel (Bonus 1) / analyse skill gap (Bonus 2).

Lancer avec :
    streamlit run dashboard/app.py
"""

import io
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from data_prep import (  # noqa: E402
    load_demandeurs, load_offres, load_ground_truth,
    build_texte_profil, build_texte_offre, clean_text,
)
from run_matching import generate_recommendations  # noqa: E402
from search import SearchEngine  # noqa: E402
from skill_gap import skill_gap  # noqa: E402
from branding import (  # noqa: E402
    render_header, render_footer, render_section_title, render_divider,
    render_banner_card, render_map_card, has_map_image, style_fig,
    CG_GREEN, CG_GOLD, CG_RED, CG_RIVER,
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
    reco_path = os.path.join(OUT_DIR, "recommandations_top10.csv")
    if os.path.exists(reco_path):
        return pd.read_csv(reco_path)
    return generate_recommendations(_dem, _off, top_k=10)


@st.cache_resource(show_spinner="Indexation de la recherche...")
def get_search_engine():
    return SearchEngine()


dem, off, gt = get_data()
reco = get_recommendations(dem, off)

# ------------------------------------------------------ Données ajoutées en session
# NB : Streamlit Cloud (gratuit) réinitialise les fichiers à chaque redémarrage du
# serveur -> les ajouts vivent en mémoire pour la session en cours (st.session_state)
# et peuvent être téléchargés (bouton export) pour être intégrés durablement via GitHub.
if "new_candidates" not in st.session_state:
    st.session_state.new_candidates = []
if "new_offers" not in st.session_state:
    st.session_state.new_offers = []


def dem_with_session() -> pd.DataFrame:
    if not st.session_state.new_candidates:
        return dem
    extra = pd.DataFrame(st.session_state.new_candidates)
    return pd.concat([dem, extra], ignore_index=True)


def off_with_session() -> pd.DataFrame:
    if not st.session_state.new_offers:
        return off
    extra = pd.DataFrame(st.session_state.new_offers)
    return pd.concat([off, extra], ignore_index=True)


def new_id_demandeur() -> str:
    return "NEWCAND" + datetime.now().strftime("%y%m%d%H%M%S")


def new_id_offre() -> str:
    return "NEWJOB" + datetime.now().strftime("%y%m%d%H%M%S")


def export_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return buf.getvalue()

render_header()

tab_overview, tab_reco, tab_search, tab_skillgap, tab_add = st.tabs(
    ["📊 Vue d'ensemble", "🎯 Recommandations", "🔎 Recherche intelligente (Bonus 1)",
     "🧩 Écarts de compétences (Bonus 2)", "➕ Ajouter des données"]
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

    render_divider()
    col1, col2 = st.columns(2)

    with col1:
        render_section_title("Secteurs les plus représentés", "Offres d'emploi par secteur d'activité")
        top_sect = off[off["secteur"] != ""]["secteur"].value_counts().head(10).reset_index()
        top_sect.columns = ["secteur", "nombre"]
        fig = px.bar(top_sect, x="nombre", y="secteur", orientation="h", color="nombre",
                     color_continuous_scale=["#d9ecdf", CG_GREEN])
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False, height=400)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with col2:
        render_section_title("Métiers les plus demandés", "Profils recherchés par les candidats")
        top_metiers = dem[dem["qualification_metier"] != ""]["qualification_metier"].value_counts().head(10).reset_index()
        top_metiers.columns = ["métier", "nombre"]
        fig = px.bar(top_metiers, x="nombre", y="métier", orientation="h", color="nombre",
                     color_continuous_scale=["#f2e2b8", CG_GOLD])
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False, height=400)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    render_divider()
    col3, col4 = st.columns([1.1, 1])
    with col3:
        render_section_title("Répartition géographique", "Localisation des offres d'emploi")
        lieu_counts = off[off["lieu"] != ""]["lieu"].value_counts().head(8).reset_index()
        lieu_counts.columns = ["lieu", "nombre"]
        if has_map_image():
            render_map_card("Répartition des offres d'emploi sur le territoire national")
        else:
            fig = px.pie(lieu_counts, names="lieu", values="nombre", hole=0.5,
                         color_discrete_sequence=[CG_GREEN, CG_GOLD, CG_RED, CG_RIVER, "#6FA287"])
            fig.update_layout(height=360)
            st.plotly_chart(style_fig(fig), use_container_width=True)

    with col4:
        render_section_title("Top localités", "Nombre d'offres par ville")
        fig = px.bar(lieu_counts.sort_values("nombre"), x="nombre", y="lieu", orientation="h",
                     color="nombre", color_continuous_scale=["#d9ecdf", CG_GREEN])
        fig.update_layout(coloraxis_showscale=False, height=360, margin=dict(t=10, l=10, r=10, b=10))
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(style_fig(fig), use_container_width=True)

        render_section_title("Objectif des demandeurs", "")
        obj_counts = dem["Objectif"].value_counts().reset_index()
        obj_counts.columns = ["objectif", "nombre"]
        fig = px.pie(obj_counts, names="objectif", values="nombre", hole=0.55,
                     color_discrete_sequence=[CG_GREEN, CG_GOLD, CG_RED])
        fig.update_layout(height=300, margin=dict(t=10, l=10, r=10, b=10))
        st.plotly_chart(style_fig(fig), use_container_width=True)

    render_divider()
    render_banner_card()

# ----------------------------------------------------------------- Recommandations
with tab_reco:
    if reco is None:
        st.warning("Aucun fichier de recommandations trouvé. Lancez `python src/run_matching.py` d'abord.")
    else:
        render_section_title("Statistiques sur les recommandations générées", "Distribution des scores calculés pour tous les candidats")
        c1, c2, c3 = st.columns(3)
        c1.metric("Candidats couverts", f"{reco['candidate_id'].nunique():,}".replace(",", " "))
        c2.metric("Score moyen (Top-1)", f"{reco[reco['rank']==1]['score'].mean():.1%}")
        c3.metric("Score médian (Top-1)", f"{reco[reco['rank']==1]['score'].median():.1%}")

        fig = px.histogram(reco[reco["rank"] == 1], x="score", nbins=40, color_discrete_sequence=[CG_GREEN])
        fig.update_traces(marker_line_width=0)
        fig.update_layout(bargap=0.05)
        st.plotly_chart(style_fig(fig), use_container_width=True)

        render_divider()
        render_section_title("Consulter les recommandations d'un candidat", "")
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
    render_section_title("Recherche en langage naturel", "Bonus 1 — requête libre, sans mot-clé exact")
    st.caption("Ex : « développeur Python à Brazzaville », « comptable avec mobilité nationale »")
    if st.session_state.new_candidates or st.session_state.new_offers:
        st.caption("🆕 Les données ajoutées dans l'onglet « Ajouter des données » sont incluses dans cette recherche.")
    mode = st.radio("Rechercher parmi :", ["Offres", "Candidats"], horizontal=True)
    query = st.text_input("Votre requête")
    if query:
        engine = get_search_engine()
        if mode == "Offres":
            results = engine.search_offres(query, top_k=15)
            if st.session_state.new_offers:
                extra_off = pd.DataFrame(st.session_state.new_offers)
                q_vec = engine.vec_off.transform([query])
                extra_X = engine.vec_off.transform(extra_off["texte_offre"])
                sims = (q_vec @ extra_X.T).toarray().ravel()
                extra_res = extra_off[["id_offre", "intitule", "entreprise", "secteur", "lieu", "type_contrat"]].copy()
                extra_res.insert(0, "score", sims.round(4))
                results = pd.concat([results, extra_res], ignore_index=True).sort_values("score", ascending=False).head(15)
            st.dataframe(results, use_container_width=True, hide_index=True)
        else:
            results = engine.search_candidats(query, top_k=15)
            if st.session_state.new_candidates:
                extra_dem = pd.DataFrame(st.session_state.new_candidates)
                q_vec = engine.vec_dem.transform([query])
                extra_X = engine.vec_dem.transform(extra_dem["texte_profil"])
                sims = (q_vec @ extra_X.T).toarray().ravel()
                cols = ["id_demandeur", "Métier visé / Qualification visée", "Secteur demandé",
                        "niveau_etude", "Mobilité géographique"]
                extra_res = extra_dem[cols].copy()
                extra_res.insert(0, "score", sims.round(4))
                results = pd.concat([results, extra_res], ignore_index=True).sort_values("score", ascending=False).head(15)
            st.dataframe(results, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------- Skill gap (Bonus 2)
with tab_skillgap:
    render_section_title("Analyse des écarts de compétences", "Bonus 2 — compatibilité candidat / offre")
    st.caption("Disponible pour les offres issues du fichier d'extension (compétences détaillées) ou ajoutées manuellement.")
    dem_all = dem_with_session()
    off_all = off_with_session()
    ext_offers = off_all[off_all["competences"] != ""]
    if ext_offers.empty:
        st.info("Aucune offre avec compétences détaillées disponible.")
    else:
        cid2 = st.selectbox("Candidat", options=sorted(dem_all["id_demandeur"].unique())[:500], key="sg_cand")
        jid2 = st.selectbox(
            "Offre", options=ext_offers["id_offre"] + " — " + ext_offers["intitule"],
        )
        jid2_clean = jid2.split(" — ")[0]
        result = skill_gap(cid2, jid2_clean, dem_all, off_all)
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

# ----------------------------------------------------------------- Ajouter des données
with tab_add:
    render_section_title("➕ Ajouter un candidat ou une offre", "")
    st.info(
        "ℹ️ Les données ajoutées ici sont utilisables **immédiatement** dans les onglets "
        "Recherche et Écarts de compétences. Elles restent en mémoire le temps de votre "
        "session (le serveur gratuit efface tout à chaque redémarrage) — pensez à "
        "**télécharger l'export Excel** en bas de page pour les intégrer durablement au "
        "jeu de données (à réenvoyer sur GitHub)."
    )

    sub_cand, sub_off = st.tabs(["👤 Nouveau candidat", "💼 Nouvelle offre"])

    # ----------------------------------------------------- Nouveau candidat
    with sub_cand:
        with st.form("form_new_candidate", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                metier_vise = st.text_input("Métier visé / Qualification visée *")
                qualification_metier = st.text_input("Qualification métier", value="")
                secteur_demande = st.selectbox(
                    "Secteur demandé", options=[""] + sorted(off["secteur"].replace("", pd.NA).dropna().unique().tolist()),
                )
                secteur_metier = st.text_input("Secteur métier (libre)", value="")
                filiere = st.text_input("Filière / Spécialité", value="")
            with c2:
                diplome = st.selectbox(
                    "Diplôme", options=sorted(dem["Diplome"].replace("", pd.NA).dropna().unique().tolist()),
                )
                niveau_etude = st.selectbox(
                    "Niveau d'étude", options=sorted(dem["niveau_etude"].replace("", pd.NA).dropna().unique().tolist()),
                )
                age = st.number_input("Âge", min_value=14, max_value=70, value=25)
                genre = st.selectbox("Genre", options=["Homme", "Femme"])
                objectif = st.selectbox("Objectif", options=["Emploi", "Stage", "Formation"])
                mobilite = st.selectbox("Mobilité géographique", options=["Oui", "Non", "Non déclaré"])

            submitted = st.form_submit_button("Ajouter ce candidat", type="primary")
            if submitted:
                if not metier_vise.strip():
                    st.error("Le champ « Métier visé » est obligatoire.")
                else:
                    row = {
                        "id_demandeur": new_id_demandeur(),
                        "Age": age,
                        "Qualification": clean_text(qualification_metier),
                        "Secteur d'activité": "",
                        "Objectif": objectif,
                        "Diplome": diplome,
                        "Genre": genre,
                        "niveau_etude": niveau_etude,
                        "qualification_metier": clean_text(qualification_metier),
                        "secteur_metier": clean_text(secteur_metier),
                        "Filière / Spécialité": clean_text(filiere),
                        "Secteur demandé": clean_text(secteur_demande),
                        "Métier visé / Qualification visée": clean_text(metier_vise),
                        "Mobilité géographique": mobilite,
                    }
                    row["texte_profil"] = build_texte_profil(row)
                    st.session_state.new_candidates.append(row)
                    st.success(f"Candidat ajouté : {row['id_demandeur']}")

        if st.session_state.new_candidates:
            last = st.session_state.new_candidates[-1]
            render_divider()
            st.markdown(f"**Aperçu — Top 5 offres pour le dernier candidat ajouté ({last['id_demandeur']})**")
            engine = get_search_engine()
            q_vec = engine.vec_off.transform([last["texte_profil"]])
            sims = (q_vec @ engine.X_off.T).toarray().ravel()
            order = np.argsort(-sims)[:5]
            preview = off.iloc[order][["id_offre", "intitule", "entreprise", "secteur", "lieu"]].copy()
            preview.insert(0, "score", sims[order].round(4))
            st.dataframe(preview, use_container_width=True, hide_index=True)

    # ----------------------------------------------------- Nouvelle offre
    with sub_off:
        with st.form("form_new_offer", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                intitule = st.text_input("Intitulé du poste *")
                secteur = st.selectbox(
                    "Secteur d'activité", options=sorted(off["secteur"].replace("", pd.NA).dropna().unique().tolist()),
                )
                entreprise = st.text_input("Entreprise")
                lieu = st.text_input("Lieu", value="BRAZZAVILLE")
            with c2:
                type_contrat = st.selectbox(
                    "Type de contrat", options=sorted(off["type_contrat"].replace("", pd.NA).dropna().unique().tolist()),
                )
                groupe_contrat = st.selectbox(
                    "Groupe de contrat", options=["Emploi Durable", "Emploi Temporaire", "Stages Classiques", "Alternance"],
                )
                profil = st.text_area("Profil recherché", height=80)
                competences = st.text_area("Compétences requises (séparées par ;)", height=80)
            description = st.text_area("Description du poste", height=80)

            submitted_off = st.form_submit_button("Ajouter cette offre", type="primary")
            if submitted_off:
                if not intitule.strip():
                    st.error("Le champ « Intitulé du poste » est obligatoire.")
                else:
                    row = {
                        "id_offre": new_id_offre(),
                        "intitule": clean_text(intitule),
                        "secteur": clean_text(secteur),
                        "entreprise": clean_text(entreprise),
                        "type_entreprise": "",
                        "lieu": clean_text(lieu),
                        "groupe_contrat": groupe_contrat,
                        "type_contrat": type_contrat,
                        "date_publication": datetime.now().strftime("%Y-%m-%d"),
                        "description": clean_text(description),
                        "profil": clean_text(profil),
                        "competences": clean_text(competences),
                    }
                    row["texte_offre"] = build_texte_offre(row)
                    st.session_state.new_offers.append(row)
                    st.success(f"Offre ajoutée : {row['id_offre']}")

        if st.session_state.new_offers:
            last_off = st.session_state.new_offers[-1]
            render_divider()
            st.markdown(f"**Aperçu — Top 5 candidats pour la dernière offre ajoutée ({last_off['id_offre']})**")
            engine = get_search_engine()
            q_vec = engine.vec_dem.transform([last_off["texte_offre"]])
            sims = (q_vec @ engine.X_dem.T).toarray().ravel()
            order = np.argsort(-sims)[:5]
            cols = ["id_demandeur", "Métier visé / Qualification visée", "Secteur demandé", "niveau_etude"]
            preview = dem.iloc[order][cols].copy()
            preview.insert(0, "score", sims[order].round(4))
            st.dataframe(preview, use_container_width=True, hide_index=True)

    # ----------------------------------------------------- Export
    render_divider()
    render_section_title("📤 Exporter les nouvelles données", "")
    st.caption(
        "Télécharge uniquement les lignes ajoutées durant cette session, au même format "
        "que les fichiers sources — il suffit de les coller à la suite dans le fichier "
        "Excel correspondant, puis de réenvoyer sur GitHub (dossier `data/`) pour rendre "
        "l'ajout permanent."
    )
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        if st.session_state.new_candidates:
            export_cand = pd.DataFrame(st.session_state.new_candidates).drop(columns=["texte_profil"])
            export_cand = export_cand.rename(columns={"id_demandeur": "Matricule"})
            st.download_button(
                "⬇️ Télécharger les nouveaux candidats (.xlsx)",
                data=export_excel_bytes(export_cand),
                file_name="nouveaux_candidats.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.caption("Aucun candidat ajouté pour l'instant.")
    with col_dl2:
        if st.session_state.new_offers:
            export_off = pd.DataFrame(st.session_state.new_offers).drop(columns=["texte_offre"])
            export_off = export_off.rename(columns={
                "id_offre": "Référence offre", "intitule": "Intitule", "secteur": "Secteur activité",
                "entreprise": "Entreprise", "type_entreprise": "Type d'entreprise", "lieu": "Lieu",
                "groupe_contrat": "Groupe de contrat", "type_contrat": "Type contrat",
                "date_publication": "Date de publication",
            })
            st.download_button(
                "⬇️ Télécharger les nouvelles offres (.xlsx)",
                data=export_excel_bytes(export_off),
                file_name="nouvelles_offres.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.caption("Aucune offre ajoutée pour l'instant.")

render_footer()
