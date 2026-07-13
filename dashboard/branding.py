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

# Couleurs du drapeau national (usage réservé : drapeau, armoiries — ne pas
# utiliser ailleurs dans le thème, pour bien les distinguer de l'identité du site)
CG_GREEN = "#0B6B3A"      # vert du drapeau
CG_YELLOW = "#F2C230"     # jaune du drapeau
CG_RED = "#B7241D"        # rouge du drapeau

# Palette principale du tableau de bord — thème clair, fond bleu très clair, accents vifs
CG_BROWN = "#6C5CE7"      # violet — couleur principale du thème (onglets, boutons, accents)
CG_OCHRE = "#17A398"      # turquoise (assombri pour rester lisible sur fond clair) — accent secondaire
CG_TERRA = "#E08E0B"      # orange (assombri pour rester lisible sur fond clair) — accent tertiaire
CG_GOLD = "#B8862B"       # or institutionnel — armoiries, devise
CG_RIVER = "#2563EB"      # bleu — accent complémentaire (graphiques)
CG_IVORY = "#E9F2FC"      # fond de page — bleu très clair
CG_INK = "#152238"        # texte principal — bleu-nuit très sombre (lisible sur fond clair)

# Couleurs additionnelles du thème
CG_CARD = "#FFFFFF"          # fond des cartes — blanc
CG_CARD_BORDER = "#D6E4F3"   # bordure des cartes — bleu très pâle
CG_TEXT_MUTED = "#57708C"    # texte secondaire (bleu-gris moyen)
CG_GRID = "#DCE7F5"          # lignes de grille des graphiques

FONTS_IMPORT = (
    "https://fonts.googleapis.com/css2?"
    "family=Space+Grotesk:wght@500;600;700&"
    "family=Inter:wght@400;500;600;700&"
    "family=IBM+Plex+Mono:wght@500;600&display=swap"
)


def _clean(html: str) -> str:
    """Supprime l'indentation de chaque ligne d'un bloc HTML/SVG multi-lignes.
    Nécessaire car Markdown interprète tout contenu indenté de 4 espaces ou plus
    comme un bloc de code (donc affiché en texte brut au lieu d'être rendu) —
    piège classique avec des f-strings multi-lignes à l'intérieur de fonctions
    indentées."""
    return "\n".join(line.strip() for line in html.strip("\n").splitlines())


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
    return _clean(f"""
    <svg width="{width}" height="{height}" viewBox="0 0 900 600" xmlns="http://www.w3.org/2000/svg" style="border-radius:{radius}px; box-shadow:0 1px 4px rgba(0,0,0,0.25); display:block;">
      <clipPath id="flagClip"><rect width="900" height="600" rx="14" ry="14"/></clipPath>
      <g clip-path="url(#flagClip)">
        <rect width="900" height="600" fill="{CG_YELLOW}"/>
        <polygon points="0,0 675,0 0,450" fill="{CG_GREEN}"/>
        <polygon points="900,150 900,600 225,600" fill="{CG_RED}"/>
      </g>
    </svg>
    """)


# --------------------------------------------------------------------------- Blason stylisé
def coat_of_arms_svg(size: int = 92) -> str:
    """Emblème stylisé (interprétation simplifiée, non officielle) évoquant les
    armoiries congolaises : couronne forestière, fasce fluviale, devise nationale."""
    return _clean(f"""
    <svg width="{size}" height="{size}" viewBox="0 0 220 240" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <path id="topArc" d="M 20,110 A 90,90 0 0 1 200,110" fill="none"/>
        <linearGradient id="shieldGold" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#F3D77A"/>
          <stop offset="100%" stop-color="{CG_GOLD}"/>
        </linearGradient>
      </defs>
      <g fill="{CG_GOLD}">
        <circle cx="110" cy="30" r="9"/>
        <circle cx="80" cy="24" r="7"/>
        <circle cx="140" cy="24" r="7"/>
        <circle cx="55" cy="34" r="6"/>
        <circle cx="165" cy="34" r="6"/>
      </g>
      <text font-size="12.5" font-weight="700" fill="#5b4300" letter-spacing="1.2" font-family="Georgia, serif"><textPath href="#topArc" startOffset="50%" text-anchor="middle">RÉPUBLIQUE DU CONGO</textPath></text>
      <path d="M 45,55 L 175,55 L 175,140 Q 175,190 110,215 Q 45,190 45,140 Z" fill="url(#shieldGold)" stroke="#5b4300" stroke-width="2.5"/>
      <path d="M 45,120 Q 65,108 85,120 T 125,120 T 165,120 L 175,124 L 175,140 Q 175,190 110,215 Q 45,190 45,140 Z" fill="{CG_GREEN}" opacity="0.9"/>
      <path d="M 45,108 Q 65,96 85,108 T 125,108 T 165,108 L 175,112 L 175,124 Q 65,108 45,120 Z" fill="{CG_GREEN}"/>
      <g transform="translate(110,90)">
        <ellipse cx="0" cy="0" rx="15" ry="11" fill="#B5121B"/>
        <circle cx="14" cy="-4" r="8" fill="#B5121B"/>
        <path d="M 20,-14 L 25,-30 L 29,-16 L 34,-28 L 33,-10 Z" fill="{CG_YELLOW}" stroke="#8a3a00" stroke-width="1"/>
        <path d="M -14,4 L -22,18 M -6,8 L -10,22 M 6,8 L 8,22 M 14,4 L 20,16" stroke="#8a3a00" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      </g>
      <g fill="#2b2b2b">
        <ellipse cx="30" cy="150" rx="16" ry="11"/>
        <ellipse cx="190" cy="150" rx="16" ry="11"/>
      </g>
      <rect x="18" y="205" width="184" height="26" rx="13" fill="{CG_GOLD}" stroke="#5b4300" stroke-width="1.5"/>
      <text x="110" y="222" font-size="11" font-weight="700" fill="#4a3400" text-anchor="middle" letter-spacing="0.8" font-family="Georgia, serif">UNITÉ · TRAVAIL · PROGRÈS</text>
    </svg>
    """)


# --------------------------------------------------------------------------- Badge ACPE (secours)
def acpe_badge_svg(size: int = 80) -> str:
    return _clean(f"""
    <svg width="{size}" height="{size}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <circle cx="50" cy="50" r="48" fill="#0B4F2C"/>
      <circle cx="50" cy="50" r="48" fill="none" stroke="{CG_GOLD}" stroke-width="2.5"/>
      <text x="50" y="46" font-size="24" font-weight="800" fill="#FFFFFF" text-anchor="middle" font-family="Arial, Helvetica, sans-serif">ACPE</text>
      <text x="50" y="65" font-size="7.5" fill="{CG_YELLOW}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" letter-spacing="0.5">CONGO</text>
    </svg>
    """)


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


def has_banner_image() -> bool:
    return (ASSETS_DIR / "acpe_banner.png").exists()


def has_map_image() -> bool:
    return (ASSETS_DIR / "congo_map.png").exists()


def get_banner_image_b64() -> Optional[str]:
    path = ASSETS_DIR / "acpe_banner.png"
    return _b64(path) if path.exists() else None


def get_map_image_b64() -> Optional[str]:
    path = ASSETS_DIR / "congo_map.png"
    return _b64(path) if path.exists() else None


# --------------------------------------------------------------------------- Signature : motif "cap boussole"
def compass_tick_svg(size: int = 26) -> str:
    """Petit repère de cap (arc pointillé + graduation), motif signature évoquant
    l'« orientation » — cœur du sujet (mettre en relation, orienter un candidat
    vers une offre). Réutilisé devant chaque titre de section."""
    return _clean(f"""
    <svg width="{size}" height="{size}" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" style="flex:none;">
      <circle cx="20" cy="20" r="16" fill="none" stroke="{CG_GOLD}" stroke-width="1.4" stroke-dasharray="2.4 3.2" opacity="0.85"/>
      <line x1="20" y1="4" x2="20" y2="10" stroke="{CG_BROWN}" stroke-width="2.2" stroke-linecap="round"/>
      <path d="M20 14 L25 24 L20 21 L15 24 Z" fill="{CG_RED}"/>
    </svg>
    """)


def section_title(text: str, subtitle: str = "") -> str:
    """Titre de section stylisé avec le motif signature (remplace st.subheader
    pour une identité visuelle cohérente sur tout le tableau de bord)."""
    sub_html = f'<div class="cg-section-sub">{subtitle}</div>' if subtitle else ""
    return _clean(f"""
    <div class="cg-section-title">
        {compass_tick_svg(24)}
        <div>
            <div class="cg-section-text">{text}</div>
            {sub_html}
        </div>
    </div>
    """)


def render_section_title(text: str, subtitle: str = ""):
    import streamlit as st
    st.markdown(section_title(text, subtitle), unsafe_allow_html=True)


def render_divider():
    """Séparateur signature (arc pointillé) entre grandes sections."""
    import streamlit as st
    st.markdown(
        _clean(f"""<div style="display:flex;align-items:center;gap:0.6rem;margin:1.6rem 0 1.3rem 0;">
            <div style="flex:1;height:1px;background:linear-gradient(90deg, transparent, #D6E4F3 15%, #D6E4F3 85%, transparent);"></div>
            {compass_tick_svg(20)}
            <div style="flex:1;height:1px;background:linear-gradient(90deg, transparent, #D6E4F3 15%, #D6E4F3 85%, transparent);"></div>
        </div>"""),
        unsafe_allow_html=True,
    )


def render_banner_card():
    """Bannière institutionnelle ACPE (si fournie) présentée dans une carte encadrée."""
    import streamlit as st
    b64 = get_banner_image_b64()
    if not b64:
        return
    st.markdown(
        _clean(f"""
        <div class="cg-banner-card">
            <img src="data:image/png;base64,{b64}" alt="Bannière ACPE" />
        </div>
        """),
        unsafe_allow_html=True,
    )


def render_map_card(caption: str = "") -> bool:
    """Affiche la carte du Congo dans une carte encadrée. Retourne True si affichée."""
    import streamlit as st
    b64 = get_map_image_b64()
    if not b64:
        return False
    cap_html = f'<div class="cg-map-caption">{caption}</div>' if caption else ""
    st.markdown(
        _clean(f"""
        <div class="cg-map-card">
            <img src="data:image/png;base64,{b64}" alt="Carte de la République du Congo" />
            {cap_html}
        </div>
        """),
        unsafe_allow_html=True,
    )
    return True


def render_page_intro(icon: str, title: str, subtitle: str, accent: str = None):
    """En-tête de page compact (icône + titre + description) utilisé en haut de
    chaque onglet secondaire, pour une cohérence visuelle avec le bandeau hero
    de la page d'accueil."""
    import streamlit as st
    accent = accent or CG_BROWN
    st.markdown(
        _clean(f"""
        <div class="cg-page-intro" style="--intro-accent:{accent};">
            <div class="cg-page-intro-icon">{icon_svg(icon, 26, accent)}</div>
            <div>
                <div class="cg-page-intro-title">{title}</div>
                <div class="cg-page-intro-sub">{subtitle}</div>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )


def gradient_colors(values, color_from: str, color_to: str) -> list:
    """Calcule un dégradé de couleurs proportionnel aux valeurs, appliqué directement
    aux barres (sans passer par l'axe de couleur Plotly, qui générait un intitulé
    « undefined » indésirable à côté des graphiques)."""
    import numpy as np

    def hex_to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(*[max(0, min(255, round(c))) for c in rgb])

    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    c0, c1 = hex_to_rgb(color_from), hex_to_rgb(color_to)
    out = []
    for v in values:
        t = (v - lo) / span
        rgb = tuple(c0[i] + (c1[i] - c0[i]) * t for i in range(3))
        out.append(rgb_to_hex(rgb))
    return out


PLOTLY_COLORWAY = [CG_BROWN, CG_OCHRE, CG_TERRA, CG_RIVER, "#EC4899", "#22D3EE"]


# --------------------------------------------------------------------------- Jeu d'icônes (style trait, cohérent)
_ICON_PATHS = {
    "people": '<path d="M9 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/><path d="M2 20c0-3.3 3.1-6 7-6s7 2.7 7 6"/><path d="M16.5 6a2.5 2.5 0 1 1 0 5"/><path d="M18 14c2.8.4 5 2.3 5 5.5"/>',
    "briefcase": '<rect x="2.5" y="7" width="19" height="12.5" rx="2"/><path d="M8 7V5.5A2.5 2.5 0 0 1 10.5 3h3A2.5 2.5 0 0 1 16 5.5V7"/><path d="M2.5 13h19"/>',
    "building": '<rect x="4" y="3" width="10" height="18" rx="1"/><rect x="15" y="9" width="6" height="12" rx="1"/><path d="M7.5 7h1M11.5 7h1M7.5 11h1M11.5 11h1M7.5 15h1M11.5 15h1"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M20 20l-4.7-4.7"/>',
    "puzzle": '<path d="M8 3.5h4a1.5 1.5 0 0 1 0 3 1.5 1.5 0 0 0 0 3H16a2 2 0 0 1 2 2v3.5a1.5 1.5 0 0 1-3 0 1.5 1.5 0 0 0-3 0v.5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-3.5a1.5 1.5 0 0 0 3 0 1.5 1.5 0 0 1 3 0H12a2 2 0 0 1-2-2V5.5a2 2 0 0 1 2-2Z"/>',
    "bolt": '<path d="M13 2 4 14h6l-1 8 9-12h-6l1-8Z"/>',
    "map": '<path d="M9 4 3 6.5v13L9 17l6 2.5 6-2.5v-13L15 6.5 9 4Z"/><path d="M9 4v13M15 6.5v13"/>',
    "chart": '<path d="M4 20V10M12 20V4M20 20v-7"/><path d="M2 20h20"/>',
}


def icon_svg(name: str, size: int = 22, color: str = None, stroke_width: float = 1.8) -> str:
    """Icône ligne (style Feather), monochrome, cohérente sur tout le tableau de bord."""
    color = color or CG_BROWN
    body = _ICON_PATHS.get(name, _ICON_PATHS["target"])
    return _clean(f"""
    <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">{body}</svg>
    """)


# --------------------------------------------------------------------------- Bandeau "hero"
def render_hero(headline: str, subheadline: str, chips: list = None):
    """Grand bandeau d'ouverture (dégradé aux couleurs institutionnelles) pour la page
    d'accueil du tableau de bord — remplace un simple titre par un vrai point d'entrée
    éditorial, comme sur les portails d'une grande institution."""
    import streamlit as st
    chips_html = ""
    if chips:
        items = "".join(
            f'<div class="cg-hero-chip">{icon_svg(ic, 16, "#FFFFFF")}<span>{txt}</span></div>'
            for ic, txt in chips
        )
        chips_html = f'<div class="cg-hero-chips">{items}</div>'
    st.markdown(
        _clean(f"""
        <div class="cg-hero">
            <div class="cg-hero-pattern"></div>
            <div class="cg-hero-content">
                <div class="cg-hero-eyebrow">{compass_tick_svg(18)}<span>ACPE · INTELLIGENCE ARTIFICIELLE AU SERVICE DE L'EMPLOI</span></div>
                <div class="cg-hero-headline">{headline}</div>
                <div class="cg-hero-sub">{subheadline}</div>
                {chips_html}
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------- Cartes KPI sur-mesure
def render_kpi_row(items: list):
    """Ligne de cartes KPI entièrement personnalisées (icône + valeur + libellé),
    plus riche visuellement que st.metric natif. items = liste de dicts avec
    keys: icon, value, label, accent (couleur optionnelle)."""
    import streamlit as st
    cards = []
    for it in items:
        accent = it.get("accent", CG_BROWN)
        cards.append(f"""
        <div class="cg-kpi-card" style="--kpi-accent:{accent};">
            <div class="cg-kpi-icon">{icon_svg(it["icon"], 26, accent)}</div>
            <div class="cg-kpi-value">{it["value"]}</div>
            <div class="cg-kpi-label">{it["label"]}</div>
        </div>
        """)
    st.markdown(
        _clean(f'<div class="cg-kpi-row">{"".join(cards)}</div>'),
        unsafe_allow_html=True,
    )


def render_card_open(title: str = "", subtitle: str = "", icon: str = None):
    """Affiche l'en-tête stylisé d'une carte. À utiliser en tout début d'un
    st.container(border=True) pour un rendu de type carte premium."""
    import streamlit as st
    icon_html = f'<div class="cg-card-icon">{icon_svg(icon, 20, CG_BROWN)}</div>' if icon else ""
    if title:
        st.markdown(
            _clean(f'<div class="cg-card-header">{icon_html}<div><div class="cg-card-title">{title}</div><div class="cg-card-subtitle">{subtitle}</div></div></div>'),
            unsafe_allow_html=True,
        )


def style_fig(fig, title: str = ""):
    """Applique un habillage graphique cohérent (police, couleurs, fond transparent)
    à toute figure Plotly du tableau de bord, avec un titre explicite (le titre
    interne de Plotly affichait littéralement « undefined » lorsqu'il n'était pas
    fourni), des titres d'axes lisibles et de taille suffisante."""
    fig.update_layout(
        title=dict(text=title, font=dict(family="Space Grotesk, sans-serif", size=14, color=CG_INK), x=0, xanchor="left"),
        font=dict(family="Inter, sans-serif", size=13, color=CG_INK),
        colorway=PLOTLY_COLORWAY,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=36 if title else 10, l=10, r=10, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
        coloraxis_showscale=False,
    )
    fig.update_xaxes(
        gridcolor="#DCE7F5", zeroline=False,
        title_font=dict(size=13, color=CG_INK, family="Inter, sans-serif"),
        tickfont=dict(size=11.5, color="#57708C"),
        title_standoff=10,
    )
    fig.update_yaxes(
        gridcolor="#DCE7F5", zeroline=False,
        title_font=dict(size=13, color=CG_INK, family="Inter, sans-serif"),
        tickfont=dict(size=11.5, color="#57708C"),
        title_standoff=10,
    )
    return fig


# --------------------------------------------------------------------------- CSS du thème
def theme_css() -> str:
    return f"""
    <style>
    @import url('{FONTS_IMPORT}');

    :root {{
        --cg-green: {CG_GREEN};
        --cg-yellow: {CG_YELLOW};
        --cg-red: {CG_RED};
        --cg-gold: {CG_GOLD};
        --cg-river: {CG_RIVER};
        --cg-ivory: {CG_IVORY};
        --cg-ink: {CG_INK};
        --cg-primary: {CG_BROWN};
        --cg-ochre: {CG_OCHRE};
        --cg-terra: {CG_TERRA};
        --cg-card: {CG_CARD};
        --cg-card-border: {CG_CARD_BORDER};
        --cg-text-muted: {CG_TEXT_MUTED};
    }}

    /* ---------- Fond général & typographie ---------- */
    .stApp {{
        background-color: var(--cg-ivory);
    }}
    [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"] {{
        background: transparent !important;
    }}
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, sans-serif;
        color: var(--cg-ink);
    }}
    h1, h2, h3, h4 {{
        font-family: 'Space Grotesk', sans-serif !important;
    }}
    code, .stCode, [data-testid="stMetricValue"] {{
        font-family: 'IBM Plex Mono', monospace !important;
    }}

    /* ---------- En-tête : panneau unique, structuré ---------- */
    .cg-header {{
        position: relative;
        overflow: hidden;
        border-radius: 16px;
        margin: 0.4rem 0 1.6rem 0;
        background: var(--cg-card);
        border: 1px solid var(--cg-card-border);
        box-shadow: 0 4px 16px rgba(21,34,56,0.08);
    }}
    .cg-header-accent {{
        height: 6px;
        width: 100%;
        background: linear-gradient(90deg, var(--cg-green) 0 33%, var(--cg-yellow) 33% 66%, var(--cg-red) 66% 100%);
    }}
    .cg-header-row {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1.6rem;
        padding: 1.1rem 1.8rem;
    }}
    .cg-header-left, .cg-header-right {{
        flex: 0 0 auto;
        display: flex;
        align-items: center;
        gap: 0.7rem;
    }}
    .cg-header-center {{
        flex: 1 1 auto;
        max-width: 640px;
        text-align: center;
    }}
    .cg-header-divider {{
        width: 1px;
        align-self: stretch;
        background: var(--cg-card-border);
        flex: 0 0 auto;
    }}
    .cg-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.9rem;
        font-weight: 700;
        color: var(--cg-ink);
        margin: 0;
        line-height: 1.15;
        letter-spacing: -0.01em;
    }}
    .cg-subtitle {{
        font-size: 0.93rem;
        color: var(--cg-text-muted);
        margin-top: 0.3rem;
    }}
    .cg-badge-flag-row {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 0.4rem;
        justify-content: center;
        font-size: 0.8rem;
        color: var(--cg-text-muted);
        font-weight: 600;
        letter-spacing: 0.3px;
    }}
    .cg-flag-motto {{
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.45rem;
    }}
    .cg-motto-text {{
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        color: {CG_GOLD};
        text-align: center;
        white-space: nowrap;
    }}

    /* ---------- Titres de section signature ---------- */
    .cg-section-title {{
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin: 0.4rem 0 1rem 0;
    }}
    .cg-section-text {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.32rem;
        font-weight: 700;
        color: var(--cg-ink);
    }}
    .cg-section-sub {{
        font-size: 0.86rem;
        color: var(--cg-text-muted);
        margin-top: 0.1rem;
    }}

    /* ---------- Cartes de métriques Streamlit ---------- */
    div[data-testid="stMetric"] {{
        background: var(--cg-card);
        border: 1px solid var(--cg-card-border);
        border-top: 4px solid var(--cg-primary);
        border-radius: 12px;
        padding: 1.1rem 1.2rem 0.9rem 1.2rem;
        box-shadow: 0 2px 10px rgba(21,34,56,0.07);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(21,34,56,0.12);
    }}
    div[data-testid="stMetric"]:nth-of-type(4n+2) {{ border-top-color: var(--cg-gold); }}
    div[data-testid="stMetric"]:nth-of-type(4n+3) {{ border-top-color: var(--cg-red); }}
    div[data-testid="stMetric"]:nth-of-type(4n+4) {{ border-top-color: var(--cg-river); }}
    div[data-testid="stMetricLabel"] {{ color: var(--cg-text-muted); font-weight: 600; font-size: 0.85rem; }}
    div[data-testid="stMetricValue"] {{ color: var(--cg-ink); font-weight: 700; }}

    /* ---------- Onglets ---------- */
    button[data-baseweb="tab"] {{
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 0.98rem;
        color: var(--cg-text-muted);
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--cg-primary) !important;
    }}
    div[data-baseweb="tab-highlight"] {{
        background-color: var(--cg-primary) !important;
        height: 3px !important;
        border-radius: 3px;
    }}
    div[data-baseweb="tab-border"] {{ background-color: var(--cg-card-border) !important; }}

    /* ---------- Boutons ---------- */
    .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        border-radius: 8px;
        border: 1.5px solid var(--cg-primary);
        transition: all 0.15s ease;
    }}
    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
        background: var(--cg-primary);
        border-color: var(--cg-primary);
    }}
    .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {{
        background: #4e2f17;
        border-color: #4e2f17;
    }}
    .stDownloadButton > button {{
        border-color: var(--cg-gold);
        color: var(--cg-gold);
    }}
    .stDownloadButton > button:hover {{
        background: var(--cg-gold);
        color: white;
    }}

    /* ---------- Cadres image (bannière ACPE / carte) ---------- */
    .cg-banner-card {{
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid var(--cg-card-border);
        box-shadow: 0 4px 14px rgba(21,34,56,0.08);
        margin: 0.3rem 0 0.6rem 0;
    }}
    .cg-banner-card img {{ width: 100%; display: block; }}

    .cg-map-card {{
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid var(--cg-card-border);
        box-shadow: 0 4px 14px rgba(21,34,56,0.08);
        background: var(--cg-card);
        padding: 0.6rem 0.6rem 0.3rem 0.6rem;
    }}
    .cg-map-card img {{ width: 100%; display: block; border-radius: 8px; }}
    .cg-map-caption {{
        text-align: center;
        font-size: 0.78rem;
        color: var(--cg-text-muted);
        padding: 0.45rem 0 0.15rem 0;
        font-style: italic;
    }}

    /* ---------- Dataframes ---------- */
    div[data-testid="stDataFrame"] {{
        border: 1px solid var(--cg-card-border);
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 1px 6px rgba(21,34,56,0.06);
    }}

    /* ---------- Boîtes d'information ---------- */
    div[data-testid="stAlertContentInfo"], div[data-testid="stNotification"] {{
        border-radius: 10px;
    }}

    /* ---------- Conteneurs à bordure (st.container(border=True)) : rendu carte premium ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 14px !important;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] > div {{
        border-radius: 14px !important;
        box-shadow: 0 3px 14px rgba(21,34,56,0.07);
        background: var(--cg-card);
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] > div > div[data-testid="stVerticalBlock"] {{
        gap: 0.6rem;
    }}

    /* ---------- Bandeau hero (page d'accueil) ---------- */
    .cg-hero {{
        position: relative;
        overflow: hidden;
        border-radius: 20px;
        padding: 2.4rem 2.6rem;
        margin-bottom: 1.6rem;
        background: linear-gradient(120deg, {CG_BROWN} 0%, #9B5FBF 45%, {CG_TERRA} 100%);
        box-shadow: 0 10px 30px rgba(110,68,35,0.25);
    }}
    .cg-hero-pattern {{
        position: absolute;
        inset: 0;
        opacity: 0.12;
        background-image: radial-gradient(circle at 20% 20%, white 1.5px, transparent 1.5px),
                          radial-gradient(circle at 60% 70%, white 1.5px, transparent 1.5px),
                          radial-gradient(circle at 90% 30%, white 1.5px, transparent 1.5px);
        background-size: 60px 60px, 90px 90px, 75px 75px;
    }}
    .cg-hero-content {{ position: relative; z-index: 1; }}
    .cg-hero-eyebrow {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: {CG_YELLOW};
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin-bottom: 0.9rem;
    }}
    .cg-hero-headline {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.3rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.2;
        max-width: 780px;
    }}
    .cg-hero-sub {{
        font-size: 1.02rem;
        color: rgba(255,255,255,0.88);
        margin-top: 0.8rem;
        max-width: 680px;
        line-height: 1.5;
    }}
    .cg-hero-chips {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: 1.4rem;
    }}
    .cg-hero-chip {{
        display: flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.28);
        color: #ffffff;
        font-size: 0.82rem;
        font-weight: 600;
        padding: 0.4rem 0.85rem;
        border-radius: 999px;
        backdrop-filter: blur(2px);
    }}

    /* ---------- Cartes KPI sur-mesure ---------- */
    .cg-kpi-row {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 0.4rem;
    }}
    .cg-kpi-card {{
        background: var(--cg-card);
        border: 1px solid var(--cg-card-border);
        border-radius: 14px;
        padding: 1.2rem 1.3rem;
        box-shadow: 0 2px 10px rgba(21,34,56,0.06);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        position: relative;
        overflow: hidden;
    }}
    .cg-kpi-card::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: var(--kpi-accent, {CG_BROWN});
    }}
    .cg-kpi-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 22px rgba(21,34,56,0.14);
    }}
    .cg-kpi-icon {{
        width: 42px;
        height: 42px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: color-mix(in srgb, var(--kpi-accent, {CG_BROWN}) 22%, var(--cg-card));
        margin-bottom: 0.7rem;
    }}
    .cg-kpi-value {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.85rem;
        font-weight: 700;
        color: {CG_INK};
        line-height: 1.1;
    }}
    .cg-kpi-label {{
        font-size: 0.82rem;
        color: var(--cg-text-muted);
        margin-top: 0.3rem;
        font-weight: 500;
    }}
    @media (max-width: 900px) {{
        .cg-kpi-row {{ grid-template-columns: repeat(2, 1fr); }}
        .cg-hero-headline {{ font-size: 1.7rem; }}
    }}

    /* ---------- En-têtes de carte (icône + titre + sous-titre) ---------- */
    .cg-card-header {{
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin-bottom: 0.6rem;
    }}
    .cg-card-icon {{
        width: 36px;
        height: 36px;
        border-radius: 9px;
        background: rgba(108,92,231,0.16);
        display: flex;
        align-items: center;
        justify-content: center;
        flex: none;
    }}
    .cg-card-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.05rem;
        color: {CG_INK};
    }}
    .cg-card-subtitle {{
        font-size: 0.8rem;
        color: var(--cg-text-muted);
    }}

    /* ---------- En-tête de page compact (onglets secondaires) ---------- */
    .cg-page-intro {{
        display: flex;
        align-items: center;
        gap: 1rem;
        background: var(--cg-card);
        border: 1px solid var(--cg-card-border);
        border-left: 5px solid var(--intro-accent, {CG_BROWN});
        border-radius: 14px;
        padding: 1.1rem 1.4rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 2px 10px rgba(21,34,56,0.06);
    }}
    .cg-page-intro-icon {{
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: color-mix(in srgb, var(--intro-accent, {CG_BROWN}) 22%, var(--cg-card));
        display: flex;
        align-items: center;
        justify-content: center;
        flex: none;
    }}
    .cg-page-intro-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.3rem;
        color: {CG_INK};
    }}
    .cg-page-intro-sub {{
        font-size: 0.88rem;
        color: var(--cg-text-muted);
        margin-top: 0.15rem;
    }}

    /* ---------- Lisibilité renforcée : libellés, légendes, tableaux ---------- */
    [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {{
        font-weight: 700 !important;
        color: var(--cg-ink) !important;
        font-size: 0.95rem !important;
    }}
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{
        color: var(--cg-text-muted) !important;
        font-weight: 500 !important;
    }}
    [data-testid="stMarkdownContainer"] p {{
        color: var(--cg-ink);
        font-weight: 450;
        line-height: 1.55;
    }}
    [data-testid="stMarkdownContainer"] strong {{
        font-weight: 700;
        color: var(--cg-ink);
    }}
    /* Radios / cases à cocher */
    [data-testid="stRadio"] label, [data-testid="stCheckbox"] label {{
        font-weight: 600 !important;
    }}
    /* Tableaux (dataframes) : en-têtes et cellules bien lisibles */
    [data-testid="stDataFrame"] [role="columnheader"] {{
        font-weight: 700 !important;
        color: var(--cg-ink) !important;
        background: rgba(108,92,231,0.10) !important;
    }}
    [data-testid="stDataFrame"] [role="gridcell"] {{
        font-weight: 500 !important;
        color: var(--cg-ink) !important;
    }}
    /* Champs de saisie (texte, nombre, zone de texte) */
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input, [data-baseweb="select"] * {{
        color: var(--cg-ink) !important;
        font-weight: 500 !important;
    }}
    /* Boîtes d'alerte (info / warning / erreur) */
    [data-testid="stAlertContentInfo"] p, [data-testid="stAlertContentWarning"] p,
    [data-testid="stAlertContentError"] p, [data-testid="stAlertContentSuccess"] p {{
        font-weight: 600 !important;
    }}
    /* Onglets internes (sous-onglets candidat/offre etc.) déjà couverts par button[data-baseweb=tab] */

    /* ---------- Pied de page ---------- */
    .cg-footer {{
        text-align: center;
        color: var(--cg-text-muted);
        font-size: 0.82rem;
        padding: 1.4rem 0 0.6rem 0;
    }}
    .cg-footer-flag {{
        display: inline-flex;
        vertical-align: middle;
        margin-right: 0.4rem;
    }}
    </style>
    """


def flag_with_motto_html(flag_width: int = 60) -> str:
    """Drapeau et devise nationale empilés verticalement (remplace le blason)."""
    flag_h = round(flag_width * 43 / 64)
    return _clean(f"""
    <div class="cg-flag-motto">
        {flag_svg(flag_width, flag_h)}
        <div class="cg-motto-text">UNITÉ · TRAVAIL · PROGRÈS</div>
    </div>
    """)


def render_header():
    """Injecte le bandeau d'en-tête (accent tricolore intégré, logo ACPE, titre,
    drapeau+devise) via st.markdown — un panneau unique, propre et bien structuré."""
    import streamlit as st

    st.markdown(theme_css(), unsafe_allow_html=True)
    st.markdown(
        _clean(f"""
        <div class="cg-header">
            <div class="cg-header-accent"></div>
            <div class="cg-header-row">
                <div class="cg-header-left">{get_acpe_logo_html(58)}</div>
                <div class="cg-header-divider"></div>
                <div class="cg-header-center">
                    <div class="cg-title">🧭 Tableau de bord décisionnel</div>
                    <div class="cg-subtitle">Appariement Demandeurs d'emploi / Offres d'emploi</div>
                    <div class="cg-badge-flag-row">Agence Congolaise pour l'Emploi (ACPE) — Hackathon IndabaX Congo 2026</div>
                </div>
                <div class="cg-header-divider"></div>
                <div class="cg-header-right">{flag_with_motto_html(52)}</div>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )


def render_footer():
    import streamlit as st

    st.markdown(
        _clean(f"""
        <div class="cg-footer">
            <span class="cg-footer-flag">{flag_svg(22, 15)}</span>
            République du Congo — Prototype réalisé dans le cadre du Hackathon IndabaX Congo 2026 —
            moteur d'appariement TF-IDF + règles métier.
        </div>
        """),
        unsafe_allow_html=True,
    )
