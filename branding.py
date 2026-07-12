"""
Identité visuelle du tableau de bord ACPE
============================================
Fournit :
- un rendu SVG fidèle du drapeau de la République du Congo (bande diagonale
  jaune séparant un triangle vert et un triangle rouge, conformément à
  l'article 5 de la Constitution du 20 janvier 2002) ;
- un blason stylisé rappelant les armoiries de la République du Congo
  (couronne forestière, bande fluviale, devise nationale « Unité - Travail -
  Progrès ») — une interprétation simplifiée à but décoratif, pas une
  reproduction héraldique officielle exacte ;
- un badge de secours pour le logo de l'ACPE si le fichier officiel n'est
  pas fourni ;
- le CSS du thème (couleurs du drapeau, cartes, onglets).

Pour utiliser les VRAIS logos (recommandé) :
  1. Téléchargez le logo officiel de l'ACPE depuis https://www.acpe.cg
     (visible en haut de leur site) et enregistrez-le sous
     dashboard/assets/acpe_logo.png
  2. Téléchargez une image des armoiries de la République du Congo
     (ex. Wikipédia « Armoiries de la République du Congo ») et
     enregistrez-la sous dashboard/assets/armoiries_congo.png
  3. Redéployez — le tableau de bord les détecte automatiquement et les
     utilise à la place des versions stylisées ci-dessous.
"""

import base64
from pathlib import Path
from typing import Optional

ASSETS_DIR = Path(__file__).parent / "assets"

# Couleurs officielles (approximatives) du drapeau congolais
CG_GREEN = "#009543"
CG_YELLOW = "#FBDE4A"
CG_RED = "#DC241F"
CG_GOLD = "#C9A227"


def _b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def _image_tag(filename: str, height: int, alt: str) -> Optional[str]:
    """Retourne une balise <img> en base64 si le fichier existe dans assets/, sinon None."""
    path = ASSETS_DIR / filename
    if path.exists():
        ext = path.suffix.lstrip(".").lower()
        ext = "jpeg" if ext == "jpg" else ext
        return f'<img src="data:image/{ext};base64,{_b64(path)}" alt="{alt}" style="height:{height}px;width:auto;object-fit:contain;" />'
    return None


# --------------------------------------------------------------------------- Drapeau
def flag_svg(width: int = 64, height: int = 43, rounded: bool = True) -> str:
    """Drapeau congolais (bande jaune diagonale entre triangle vert et triangle rouge)."""
    radius = 6 if rounded else 0
    return f"""
    <svg width="{width}" height="{height}" viewBox="0 0 900 600" xmlns="http://www.w3.org/2000/svg"
         style="border-radius:{radius}px; box-shadow:0 1px 4px rgba(0,0,0,0.25); display:block;">
      <clipPath id="flagClip"><rect width="900" height="600" rx="14" ry="14"/></clipPath>
      <g clip-path="url(#flagClip)">
        <rect width="900" height="600" fill="{CG_YELLOW}"/>
        <polygon points="0,0 675,0 0,450" fill="{CG_GREEN}"/>
        <polygon points="900,150 900,600 225,600" fill="{CG_RED}"/>
      </g>
    </svg>
    """


# --------------------------------------------------------------------------- Blason stylisé
def coat_of_arms_svg(size: int = 92) -> str:
    """Emblème stylisé (interprétation simplifiée, non officielle) évoquant les
    armoiries congolaises : couronne forestière, fasce fluviale, devise nationale."""
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 220 240" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <path id="topArc" d="M 20,110 A 90,90 0 0 1 200,110" fill="none"/>
        <linearGradient id="shieldGold" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#F3D77A"/>
          <stop offset="100%" stop-color="{CG_GOLD}"/>
        </linearGradient>
      </defs>

      <!-- couronne forestière stylisée -->
      <g fill="{CG_GOLD}">
        <circle cx="110" cy="30" r="9"/>
        <circle cx="80" cy="24" r="7"/>
        <circle cx="140" cy="24" r="7"/>
        <circle cx="55" cy="34" r="6"/>
        <circle cx="165" cy="34" r="6"/>
      </g>

      <!-- texte arqué : République du Congo -->
      <text font-size="12.5" font-weight="700" fill="#5b4300" letter-spacing="1.2"
            font-family="Georgia, 'Times New Roman', serif">
        <textPath href="#topArc" startOffset="50%" text-anchor="middle">
          RÉPUBLIQUE DU CONGO
        </textPath>
      </text>

      <!-- écu -->
      <path d="M 45,55 L 175,55 L 175,140 Q 175,190 110,215 Q 45,190 45,140 Z"
            fill="url(#shieldGold)" stroke="#5b4300" stroke-width="2.5"/>

      <!-- fasce ondée (fleuve) -->
      <path d="M 45,120 Q 65,108 85,120 T 125,120 T 165,120 L 175,124 L 175,140
               Q 175,190 110,215 Q 45,190 45,140 Z"
            fill="{CG_GREEN}" opacity="0.9"/>
      <path d="M 45,108 Q 65,96 85,108 T 125,108 T 165,108 L 175,112 L 175,124
               Q 65,108 45,120 Z"
            fill="{CG_GREEN}"/>

      <!-- lion stylisé tenant un flambeau -->
      <g transform="translate(110,90)">
        <ellipse cx="0" cy="0" rx="15" ry="11" fill="#B5121B"/>
        <circle cx="14" cy="-4" r="8" fill="#B5121B"/>
        <path d="M 20,-14 L 25,-30 L 29,-16 L 34,-28 L 33,-10 Z" fill="{CG_YELLOW}" stroke="#8a3a00" stroke-width="1"/>
        <path d="M -14,4 L -22,18 M -6,8 L -10,22 M 6,8 L 8,22 M 14,4 L 20,16"
              stroke="#8a3a00" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      </g>

      <!-- éléphants stylisés (supports) -->
      <g fill="#2b2b2b">
        <ellipse cx="30" cy="150" rx="16" ry="11"/>
        <ellipse cx="190" cy="150" rx="16" ry="11"/>
      </g>

      <!-- listel : devise -->
      <rect x="18" y="205" width="184" height="26" rx="13" fill="{CG_GOLD}" stroke="#5b4300" stroke-width="1.5"/>
      <text x="110" y="222" font-size="11" font-weight="700" fill="#4a3400" text-anchor="middle"
            letter-spacing="0.8" font-family="Georgia, 'Times New Roman', serif">
        UNITÉ · TRAVAIL · PROGRÈS
      </text>
    </svg>
    """


# --------------------------------------------------------------------------- Badge ACPE (secours)
def acpe_badge_svg(size: int = 80) -> str:
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <circle cx="50" cy="50" r="48" fill="#0B4F2C"/>
      <circle cx="50" cy="50" r="48" fill="none" stroke="{CG_GOLD}" stroke-width="2.5"/>
      <text x="50" y="46" font-size="24" font-weight="800" fill="#FFFFFF" text-anchor="middle"
            font-family="Arial, Helvetica, sans-serif">ACPE</text>
      <text x="50" y="65" font-size="7.5" fill="{CG_YELLOW}" text-anchor="middle"
            font-family="Arial, Helvetica, sans-serif" letter-spacing="0.5">CONGO</text>
    </svg>
    """


def get_acpe_logo_html(height: int = 64) -> str:
    real = _image_tag("acpe_logo.png", height, "Logo ACPE")
    if real:
        return real
    return acpe_badge_svg(height)


def get_coat_of_arms_html(height: int = 92) -> str:
    real = _image_tag("armoiries_congo.png", height, "Armoiries de la République du Congo")
    if real:
        return f'<div style="text-align:center;">{real}<div style="font-size:10px;font-weight:700;letter-spacing:0.6px;color:{CG_GOLD};margin-top:2px;">UNITÉ · TRAVAIL · PROGRÈS</div></div>'
    return coat_of_arms_svg(height)


# --------------------------------------------------------------------------- CSS du thème
def theme_css() -> str:
    return f"""
    <style>
    :root {{
        --cg-green: {CG_GREEN};
        --cg-yellow: {CG_YELLOW};
        --cg-red: {CG_RED};
        --cg-gold: {CG_GOLD};
    }}

    /* Bandeau tricolore en haut de la page */
    .cg-topbar {{
        height: 6px;
        width: 100%;
        background: linear-gradient(90deg, var(--cg-green) 0 33%, var(--cg-yellow) 33% 66%, var(--cg-red) 66% 100%);
        border-radius: 0 0 4px 4px;
        margin-bottom: 1.1rem;
    }}

    /* En-tête */
    .cg-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
        padding: 0.4rem 0 1.1rem 0;
        border-bottom: 1px solid #e8e3d5;
        margin-bottom: 1.4rem;
    }}
    .cg-header-left, .cg-header-right {{
        flex: 0 0 auto;
        display: flex;
        align-items: center;
        gap: 0.7rem;
    }}
    .cg-header-center {{
        flex: 1 1 auto;
        text-align: center;
    }}
    .cg-title {{
        font-size: 2.05rem;
        font-weight: 800;
        color: #1a2e22;
        margin: 0;
        line-height: 1.15;
    }}
    .cg-subtitle {{
        font-size: 0.95rem;
        color: #5a5a5a;
        margin-top: 0.35rem;
    }}
    .cg-badge-flag-row {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 0.3rem;
        justify-content: center;
        font-size: 0.8rem;
        color: #7a7a7a;
        font-weight: 600;
        letter-spacing: 0.3px;
    }}

    /* Cartes de métriques Streamlit */
    div[data-testid="stMetric"] {{
        background: #ffffff;
        border: 1px solid #e8e3d5;
        border-top: 4px solid var(--cg-green);
        border-radius: 10px;
        padding: 1rem 1.1rem 0.8rem 1.1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    div[data-testid="stMetric"]:nth-of-type(4n+2) {{ border-top-color: var(--cg-yellow); }}
    div[data-testid="stMetric"]:nth-of-type(4n+3) {{ border-top-color: var(--cg-red); }}
    div[data-testid="stMetric"]:nth-of-type(4n+4) {{ border-top-color: var(--cg-gold); }}
    div[data-testid="stMetricLabel"] {{ color: #5a5a5a; font-weight: 600; }}
    div[data-testid="stMetricValue"] {{ color: #1a2e22; }}

    /* Onglets */
    button[data-baseweb="tab"] {{
        font-weight: 600;
        font-size: 0.98rem;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--cg-green) !important;
    }}
    div[data-baseweb="tab-highlight"] {{
        background-color: var(--cg-green) !important;
        height: 3px !important;
    }}

    /* Sous-titres de section */
    h3 {{
        color: #1a2e22 !important;
        border-left: 4px solid var(--cg-green);
        padding-left: 0.6rem;
    }}

    /* Pied de page */
    .cg-footer {{
        text-align: center;
        color: #8a8a8a;
        font-size: 0.82rem;
        padding: 1.2rem 0 0.4rem 0;
    }}
    .cg-footer-flag {{
        display: inline-flex;
        vertical-align: middle;
        margin-right: 0.4rem;
    }}
    </style>
    """


def render_header():
    """Injecte le bandeau tricolore + l'en-tête (logo ACPE / titre / armoiries) via st.markdown."""
    import streamlit as st

    st.markdown(theme_css(), unsafe_allow_html=True)
    st.markdown('<div class="cg-topbar"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="cg-header">
            <div class="cg-header-left">{get_acpe_logo_html(64)}</div>
            <div class="cg-header-center">
                <div class="cg-title">🧭 Tableau de bord décisionnel</div>
                <div class="cg-subtitle">Appariement Demandeurs d'emploi / Offres d'emploi</div>
                <div class="cg-badge-flag-row">{flag_svg(28, 19)} Agence Congolaise pour l'Emploi (ACPE) — Hackathon IndabaX Congo 2026</div>
            </div>
            <div class="cg-header-right">{get_coat_of_arms_html(92)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    import streamlit as st

    st.markdown(
        f"""
        <div class="cg-footer">
            <span class="cg-footer-flag">{flag_svg(22, 15)}</span>
            République du Congo — Prototype réalisé dans le cadre du Hackathon IndabaX Congo 2026 —
            moteur d'appariement TF-IDF + règles métier.
        </div>
        """,
        unsafe_allow_html=True,
    )
