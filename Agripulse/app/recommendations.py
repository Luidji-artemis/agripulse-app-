"""
AgriPulse - Moteur de Recommandations
Génère des recommandations intelligentes basées sur les données du CSV.
"""
import random
from datetime import datetime

# ─── COORDONNÉES GÉOGRAPHIQUES DES RÉGIONS ───────────────────────────────────
REGION_COORDS = {
    "Adamaoua":    {"lat": 6.5, "lon": 13.5, "chef_lieu": "Ngaoundéré"},
    "Centre":      {"lat": 3.85, "lon": 11.5, "chef_lieu": "Yaoundé"},
    "Est":         {"lat": 4.0,  "lon": 14.0, "chef_lieu": "Bertoua"},
    "Extrême-Nord":{"lat": 10.5, "lon": 14.3, "chef_lieu": "Maroua"},
    "Littoral":    {"lat": 4.0,  "lon": 9.7,  "chef_lieu": "Douala"},
    "Nord":        {"lat": 8.5,  "lon": 13.5, "chef_lieu": "Garoua"},
    "Nord-Ouest":  {"lat": 6.0,  "lon": 10.2, "chef_lieu": "Bamenda"},
    "Ouest":       {"lat": 5.5,  "lon": 10.5, "chef_lieu": "Bafoussam"},
    "Sud":         {"lat": 2.9,  "lon": 11.5, "chef_lieu": "Ebolowa"},
    "Sud-Ouest":   {"lat": 4.2,  "lon": 9.2,  "chef_lieu": "Buéa"},
}

MARCHE_COORDS = {
    "Marché Central de Yaoundé": (3.868, 11.518),
    "Marché de Mokolo": (3.875, 11.510),
    "Marché de Mfoundi": (3.862, 11.521),
    "Marché de Biyem-Assi": (3.832, 11.489),
    "Marché Artisanal de Tsinga": (3.878, 11.497),
    "Marché Central de Douala": (4.049, 9.698),
    "Marché Artisanal de Douala": (4.055, 9.701),
    "Marché New-Deïdo": (4.070, 9.720),
    "Marché d'Eko": (4.040, 9.690),
    "Marché PK10": (4.032, 9.722),
    "Marché de Ngaoundéré": (7.325, 13.584),
    "Marché à bétail de Ngaoundéré": (7.318, 13.572),
    "Marché de Tibati": (6.469, 12.628),
    "Marché de Nyambaka": (6.832, 13.068),
    "Marché de Somie": (6.955, 13.102),
    "Grand Marché de Maroua": (10.597, 14.324),
    "Marché de Pouss": (10.852, 14.867),
    "Marché de Mokolo (EN)": (10.742, 13.803),
    "Marché de Kousséri": (12.076, 15.031),
    "Marché de Yagoua": (10.341, 15.237),
    "Marché de Garoua": (9.302, 13.397),
    "Grand-Marché de Garoua": (9.298, 13.401),
    "Marché coopératif du Nord": (9.310, 13.390),
    "Marché de noix de kola de Garoua": (9.315, 13.405),
    "Marché de Guider": (9.932, 13.953),
    "Marché Central de Bamenda": (5.961, 10.145),
    "Marché Alimentaire de Bamenda": (5.955, 10.148),
    "Marché de Bamenda Mile Four": (5.970, 10.162),
    "Cattle Market de Bamenda": (5.978, 10.135),
    "Marché de Nkwen": (5.981, 10.139),
    "Marché A de Bafoussam": (5.478, 10.421),
    "Marché de Foumban": (5.729, 10.907),
    "Marché de Dschang": (5.448, 10.055),
    "Marché de Mbouda": (5.626, 10.254),
    "Marché de Kekem": (5.179, 10.012),
    "Marché d'Ebolowa": (2.900, 11.153),
    "Marché Coopératif du Sud": (2.910, 11.160),
    "Marché d'Ambam": (2.384, 11.268),
    "Marché de Kribi": (2.940, 9.909),
    "Marché de Sangmélima": (3.007, 11.985),
    "Marché Central de Buéa": (4.154, 9.241),
    "Marché de Great Soppo": (4.168, 9.254),
    "Marché de Munya": (4.140, 9.235),
    "Marché de Limbe": (4.017, 9.200),
    "Marché de Kumba": (4.636, 9.447),
    "Marché de Bertoua": (4.577, 13.686),
    "Marché de Yokadouma": (3.526, 15.056),
    "Marché de Batouri": (4.438, 14.365),
    "Marché d'Abong-Mbang": (3.998, 13.182),
    "Marché de Dimako": (4.292, 13.835),
}

# ─── CONTEXTE SAISONNIER CAMEROUN ────────────────────────────────────────────
def get_saison() -> str:
    mois = datetime.now().month
    if mois in [11, 12, 1, 2, 3]:
        return "saison_seche"
    elif mois in [3, 4, 5]:
        return "grande_saison_pluies_debut"
    elif mois in [6, 7, 8]:
        return "grande_saison_pluies"
    else:
        return "petite_saison_seche"

def get_saison_label() -> str:
    s = get_saison()
    labels = {
        "saison_seche": "Saison sèche",
        "grande_saison_pluies_debut": "Début grande saison des pluies",
        "grande_saison_pluies": "Grande saison des pluies",
        "petite_saison_seche": "Petite saison sèche",
    }
    return labels.get(s, "")

# ─── GÉNÉRATEUR DE RECOMMANDATIONS ───────────────────────────────────────────
def generer_recommandations(
    produit: str,
    region: str,
    marche: str,
    prix_propose: float,
    prix_actuel: float,
    tendance: str,
    predictions: dict,
    unite: str,
    diff_pct: float,
    r2: float,
    kmeans_labels: list = None,
    kmeans_regions: list = None,
) -> dict:
    saison = get_saison()
    saison_label = get_saison_label()
    mois_actuel = datetime.now().month
    prix_3mois = predictions.get("3_mois", prix_actuel)
    prix_6mois = predictions.get("6_mois", prix_actuel)
    gain_3mois_pct = round((prix_3mois - prix_actuel) / prix_actuel * 100, 1) if prix_actuel else 0
    confiance = "élevée" if r2 > 0.7 else "modérée" if r2 > 0.4 else "faible"

    # ── OPPORTUNITÉ VENTE ──────────────────────────────────────────────────────
    if diff_pct < -15:
        opp_icon = "⚠️"
        opp_titre = "Attention — Prix Sous le Marché"
        if tendance == "hausse" and gain_3mois_pct > 10:
            opp_detail = (
                f"Le prix proposé ({int(prix_propose):,} FCFA/{unite}) est "
                f"inférieur de {abs(int(diff_pct))}% au prix moyen du marché "
                f"({int(prix_actuel):,} FCFA/{unite}). "
                f"La tendance est à la hausse : si vous patientez environ 3 mois, "
                f"le prix attendu sera de {int(prix_3mois):,} FCFA/{unite}. "
                f"Stockez votre {produit} si vous avez les capacités de conservation — "
                f"les marchés de la région {region} montrent une demande croissante "
                f"en {saison_label}."
            )
        elif saison == "grande_saison_pluies":
            opp_detail = (
                f"Nous sommes en {saison_label} : c'est souvent la période de basse "
                f"des prix pour {produit}. Votre prix proposé ({int(prix_propose):,} FCFA) "
                f"reflète cette réalité saisonnière. Si votre situation financière le permet, "
                f"attendez la fin de la saison des pluies pour vendre à un meilleur prix "
                f"(estimation : {int(prix_3mois):,} FCFA/{unite} dans 3 mois)."
            )
        else:
            opp_detail = (
                f"Le prix proposé de {int(prix_propose):,} FCFA/{unite} est nettement "
                f"sous le prix du marché ({int(prix_actuel):,} FCFA/{unite}). "
                f"Comparez avec d'autres marchés de la région {region} — "
                f"certains marchés affichent des prix plus favorables. "
                f"Ne bradez pas votre production."
            )
    elif diff_pct > 15:
        opp_icon = "🟢"
        opp_titre = "Opportunité Favorable — Prix Au-Dessus du Marché"
        opp_detail = (
            f"Excellente position ! Votre prix ({int(prix_propose):,} FCFA/{unite}) dépasse "
            f"de {int(diff_pct)}% le prix moyen du marché ({int(prix_actuel):,} FCFA/{unite}). "
            f"Profitez-en pour vendre maintenant, surtout si la tendance prédite dans 6 mois "
            f"est de {int(prix_6mois):,} FCFA/{unite}. "
            f"Assurez-vous que la qualité de votre {produit} justifie cette prime de prix "
            f"auprès des acheteurs du marché {marche}."
        )
    else:
        opp_icon = "✅"
        opp_titre = "Prix Juste — Aligné avec le Marché"
        if gain_3mois_pct > 8:
            opp_detail = (
                f"Votre prix ({int(prix_propose):,} FCFA/{unite}) est bien aligné avec "
                f"le marché actuel. Bonne nouvelle : la tendance à 3 mois pointe vers "
                f"{int(prix_3mois):,} FCFA/{unite}. Vous pouvez vendre maintenant à prix correct "
                f"ou attendre quelques semaines si votre {produit} se conserve bien."
            )
        else:
            opp_detail = (
                f"Votre prix de {int(prix_propose):,} FCFA/{unite} est cohérent avec les "
                f"prix pratiqués sur les marchés de {region}. La tendance est stable. "
                f"Concentrez-vous sur la fidélisation de vos acheteurs habituels "
                f"sur le marché {marche}."
            )

    # ── LOGISTIQUE ────────────────────────────────────────────────────────────
    logi_icon = "🚛"
    logi_titre = "Logistique & Marchés Alternatifs"

    # Trouver la région avec le meilleur prix prédit
    regions_bonus = {
        "Littoral": "Douala (forte densité urbaine, prix premium)",
        "Centre": "Yaoundé (marché administratif stable)",
        "Ouest": "Bafoussam (carrefour commercial des Hauts-Plateaux)",
        "Nord": "Garoua (axe Tchad-Cameroun, flux transfrontalier)",
    }
    alt_region = regions_bonus.get(region, "une grande ville voisine")

    logi_detail = (
        f"Marchés alternatifs conseillés : si {marche} sature ou offre des prix bas, "
        f"envisagez de transporter votre {produit} vers {alt_region}. "
        f"Actuellement en {saison_label}, les routes du {region} sont "
        f"{'accessibles' if saison == 'saison_seche' else 'parfois difficiles en zone rurale — anticipez les délais'}. "
        f"Regroupez-vous avec d'autres producteurs pour partager le transport "
        f"et réduire le coût logistique par {unite}. "
        f"Prédiction de confiance {confiance} (R²={r2}) basée sur {len(kmeans_regions or [])} régions analysées."
    )

    # ── DÉTAILS TECHNIQUES ────────────────────────────────────────────────────
    tech_icon = "📊"
    tech_titre = "Détails Techniques — Analyse AgriPulse"
    tech_detail = (
        f"Modèle : Régression linéaire (R²={r2}) + K-Means clustering régional. "
        f"Données : 94 080 relevés de prix (2019-2024) sur 10 régions, 50 marchés, 64 produits. "
        f"Prix 3 mois : {int(prix_3mois):,} FCFA/{unite} | "
        f"Prix 6 mois : {int(prix_6mois):,} FCFA/{unite}. "
        f"Saison actuelle : {saison_label}. "
        f"Confiance prédiction : {confiance}."
    )

    return {
        "opportunite": {
            "icon": opp_icon,
            "titre": opp_titre,
            "detail": opp_detail,
        },
        "logistique": {
            "icon": logi_icon,
            "titre": logi_titre,
            "detail": logi_detail,
        },
        "technique": {
            "icon": tech_icon,
            "titre": tech_titre,
            "detail": tech_detail,
        },
        "saison": saison_label,
        "confiance": confiance,
        "prix_3mois": int(prix_3mois),
        "prix_6mois": int(prix_6mois),
        "gain_3mois_pct": gain_3mois_pct,
    }

# ─── ASTUCES POUR INTERFACE PAR DÉFAUT ───────────────────────────────────────
ASTUCES = [
    "💡 Remplissez le formulaire à gauche pour obtenir une analyse personnalisée de votre produit.",
    "📍 Sélectionnez votre région pour voir les prix sur la carte thermique du Cameroun.",
    "📈 AgriPulse utilise 94 080 relevés de prix (2019-2024) pour ses prédictions.",
    "🌾 Comparez vos prix avec ceux de 50 marchés répartis sur les 10 régions du Cameroun.",
    "🔮 Nos modèles de régression prédisent les prix à 1, 3 et 6 mois.",
    "🗂️ 64 produits agricoles sont référencés, de la tomate au café robusta.",
    "🤝 Rejoignez un groupement de producteurs pour mieux négocier vos prix.",
    "🚛 Comparez toujours le prix du transport avant de changer de marché.",
    "☀️ Les prix varient fortement selon la saison des pluies et la saison sèche au Cameroun.",
    "📊 Le K-Means clustering identifie des groupes de régions avec des comportements de prix similaires.",
]

def get_astuce_aleatoire() -> str:
    return random.choice(ASTUCES)