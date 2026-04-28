"""
Script de génération du CSV AgriPulse
Données historiques des prix agricoles au Cameroun (2019-2026)
Inspiré des données WFP, actualisé avec tendance modérée et récoltes 2025/2026.
"""
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# ─── RÉGIONS & MARCHÉS (inchangés) ──────────────────────────────────────────
REGIONS_MARCHES = {
    "Adamaoua": ["Marché de Tibati", "Marché de Nyambaka", "Marché de Somie", "Marché à bétail de Ngaoundéré", "Marché centrale de Ngaoundéré"],
    "Centre":   ["Marché NSAM", "Marché de Mokolo", "Marché de Nkoa-Bang", "Marché de Biyem-Assi", "Marché Artisanal de Tsinga"],
    "Est":      ["Marché de Bertoua", "Marché de Yokadouma", "Marché de Batouri", "Marché d'Abong-Mbang", "Marché de Dimako"],
    "Extrême-Nord": ["Grand Marché de Maroua", "Marché de Pouss", "Marché de Mokolo (EN)", "Marché de Kousséri", "Marché de Yagoua"],
    "Littoral": ["Marché Central de Douala", "Marché Artisanal de Douala", "Marché New-Deïdo", "Marché d'Eko", "Marché PK10"],
    "Nord":     ["Marché de Garoua", "Grand-Marché de Garoua", "Marché coopératif du Nord", "Marché de noix de kola de Garoua", "Marché de Guider"],
    "Nord-Ouest": ["Marché Central de Bamenda", "Marché Alimentaire de Bamenda", "Marché de Bamenda Mile Four", "Cattle Market de Bamenda", "Marché de Nkwen"],
    "Ouest":    ["Marché A de Bafoussam", "Marché de Foumban", "Marché de Dschang", "Marché de Mbouda", "Marché de Kekem"],
    "Sud":      ["Marché d'Ebolowa", "Marché Coopératif du Sud", "Marché d'Ambam", "Marché de Kribi", "Marché de Sangmélima"],
    "Sud-Ouest":["Marché Central de Buéa", "Marché de Great Soppo", "Marché de Munya", "Marché de Limbe", "Marché de Kumba"],
}

# ─── PRODUITS (même liste, inchangée) ───────────────────────────────────────
# Format : (categorie, nom, unite, prix_base_FCFA, mois_pics, amplitude)
PRODUITS = [
    # Céréales
    ("Céréales", "Maïs blanc", "kg", 220, [6,7,8,9], 0.25),
    ("Céréales", "Maïs jaune", "kg", 210, [6,7,8,9], 0.25),
    ("Céréales", "Riz local", "kg", 450, [10,11,12], 0.15),
    ("Céréales", "Riz importé long grain", "kg", 520, [], 0.08),
    ("Céréales", "Sorgho rouge", "kg", 190, [11,12,1], 0.30),
    ("Céréales", "Sorgho blanc", "kg", 185, [11,12,1], 0.28),
    ("Céréales", "Millet", "kg", 200, [11,12,1,2], 0.32),
    ("Céréales", "Blé", "kg", 480, [], 0.05),
    # Légumineuses
    ("Légumineuses", "Niébé (haricot)", "kg", 550, [1,2,3], 0.35),
    ("Légumineuses", "Haricot sec", "kg", 600, [1,2,3], 0.30),
    ("Légumineuses", "Soja", "kg", 420, [11,12,1], 0.25),
    ("Légumineuses", "Arachide", "kg", 700, [10,11,12], 0.30),
    ("Légumineuses", "Pois jaune", "kg", 480, [1,2], 0.20),
    # Tubercules
    ("Tubercules", "Manioc frais", "kg", 120, [3,4,5,6], 0.40),
    ("Tubercules", "Manioc cossette", "kg", 180, [7,8,9], 0.35),
    ("Tubercules", "Igname", "kg", 280, [8,9,10], 0.45),
    ("Tubercules", "Macabo (taro)", "kg", 200, [9,10,11], 0.35),
    ("Tubercules", "Patate douce", "kg", 160, [4,5,6], 0.30),
    ("Tubercules", "Pomme de terre", "kg", 350, [4,5,6], 0.35),
    # Farines
    ("Farines & Dérivés", "Farine de maïs", "kg", 320, [10,11,12], 0.20),
    ("Farines & Dérivés", "Gari (farine de manioc)", "kg", 280, [9,10,11], 0.25),
    ("Farines & Dérivés", "Tapioca", "kg", 300, [9,10], 0.20),
    ("Farines & Dérivés", "Farine de blé", "kg", 500, [], 0.08),
    # Bananes & Plantains
    ("Bananes & Plantains", "Banane plantain", "régime", 1200, [3,4,5,11,12], 0.45),
    ("Bananes & Plantains", "Banane dessert", "kg", 280, [3,4,5], 0.30),
    # Fruits
    ("Fruits", "Mangue", "kg", 200, [3,4,5,6], 0.60),
    ("Fruits", "Ananas", "pièce", 350, [3,4,5,6], 0.50),
    ("Fruits", "Avocat", "kg", 400, [2,3,4,5], 0.55),
    ("Fruits", "Orange", "kg", 300, [11,12,1], 0.40),
    ("Fruits", "Pastèque", "kg", 150, [3,4,5], 0.50),
    ("Fruits", "Papaye", "kg", 180, [4,5,6,7], 0.40),
    # Légumes
    ("Légumes", "Tomate", "kg", 350, [11,12,1,2], 0.70),
    ("Légumes", "Oignon", "kg", 450, [11,12,1,2], 0.65),
    ("Légumes", "Piment frais", "kg", 600, [3,4,5], 0.60),
    ("Légumes", "Gombo (okra)", "kg", 400, [6,7,8], 0.50),
    ("Légumes", "Carotte", "kg", 380, [11,12,1], 0.35),
    ("Légumes", "Choux", "pièce", 300, [11,12,1], 0.40),
    ("Légumes", "Feuilles de manioc", "botte", 150, [4,5,6], 0.35),
    ("Légumes", "Feuilles d'okok", "botte", 200, [3,4,5,6], 0.40),
    # Viandes
    ("Viandes & Protéines", "Bœuf", "kg", 2200, [], 0.12),
    ("Viandes & Protéines", "Poulet", "kg", 1800, [12,1], 0.20),
    ("Viandes & Protéines", "Porc", "kg", 1900, [12,1], 0.18),
    ("Viandes & Protéines", "Chèvre", "kg", 2500, [12,1], 0.22),
    ("Viandes & Protéines", "Mouton", "kg", 2800, [12,1], 0.25),
    ("Viandes & Protéines", "Escargot", "kg", 1500, [5,6,7], 0.50),
    ("Viandes & Protéines", "Wagashi (fromage)", "kg", 1200, [], 0.15),
    ("Viandes & Protéines", "Œufs", "douzaine", 1200, [12,1], 0.15),
    # Poissons
    ("Poissons & Fruits de mer", "Tilapia frais", "kg", 1200, [3,4,5], 0.40),
    ("Poissons & Fruits de mer", "Tilapia fumé", "kg", 2200, [], 0.15),
    ("Poissons & Fruits de mer", "Maquereau frais", "kg", 1000, [10,11,12], 0.35),
    ("Poissons & Fruits de mer", "Sardine", "kg", 800, [], 0.10),
    ("Poissons & Fruits de mer", "Crevettes sèches", "kg", 3500, [11,12,1], 0.30),
    ("Poissons & Fruits de mer", "Silure (poisson-chat)", "kg", 1500, [4,5,6], 0.35),
    # Huiles
    ("Huiles & Matières grasses", "Huile de palme", "litre", 800, [4,5,6], 0.30),
    ("Huiles & Matières grasses", "Huile végétale raffinée", "litre", 950, [], 0.10),
    ("Huiles & Matières grasses", "Pâte d'arachide", "kg", 1200, [12,1,2], 0.25),
    # Condiments
    ("Condiments & Épices", "Sel", "kg", 250, [], 0.05),
    ("Condiments & Épices", "Sucre raffiné", "kg", 700, [], 0.08),
    ("Condiments & Épices", "Oignon séché", "kg", 550, [3,4,5], 0.40),
    ("Condiments & Épices", "Gingembre", "kg", 1000, [8,9,10], 0.35),
    ("Condiments & Épices", "Ail", "kg", 1500, [1,2,3], 0.30),
    # Boissons/Café
    ("Boissons & Cacao", "Café robusta", "kg", 1800, [11,12,1,2], 0.40),
    ("Boissons & Cacao", "Cacao", "kg", 1200, [10,11,12], 0.35),
    ("Boissons & Cacao", "Thé", "kg", 2000, [], 0.10),
]

# ─── Multiplicateurs régionaux (inchangés) ──────────────────────────────────
REGION_FACTOR = {
    "Adamaoua": 1.05, "Centre": 1.20, "Est": 0.92,
    "Extrême-Nord": 0.95, "Littoral": 1.25, "Nord": 1.00,
    "Nord-Ouest": 1.08, "Ouest": 1.10, "Sud": 1.05, "Sud-Ouest": 1.12,
}

def seasonal_factor(month, pic_months, amplitude):
    if not pic_months:
        return 1.0
    # distance circulaire au mois pic le plus proche
    angle = min(min(abs(month - m), 12 - abs(month - m)) for m in pic_months)
    factor = 1.0 + amplitude * np.cos(np.pi * angle / 6)
    return max(0.5, factor)

def generate_price(base, region_factor, s_factor, trend_factor, noise_std=0.05):
    price = base * region_factor * s_factor * trend_factor
    noise = np.random.normal(1.0, noise_std)
    return max(50, round(price * noise))

# ════════════════════════════════════════════════════════════════════════
# GÉNÉRATION 2019 → 2026 (fin décembre 2026)
# ════════════════════════════════════════════════════════════════════════
rows = []
start_date = datetime(2019, 1, 1)
end_date   = datetime(2026, 12, 31)   # <- étendu jusqu'à fin 2026

current = start_date
dates = []
while current <= end_date:
    dates.append(current)
    current += timedelta(days=15)     # relevé bimensuel

print(f"Génération de {len(dates)} périodes × {len(PRODUITS)} produits × {len(REGIONS_MARCHES)} régions...")

for region, marches in REGIONS_MARCHES.items():
    rfactor = REGION_FACTOR[region]
    for cat, produit, unite, base_price, pic_months, amplitude in PRODUITS:
        for date in dates:
            marche = random.choice(marches)
            month  = date.month
            year   = date.year
            # Tendance inflationniste modérée : +4% par an, avec un petit effet exponentiel
            trend = 1.0 + 0.04 * (year - 2019) + 0.005 * (year - 2019) ** 1.2
            sfact = seasonal_factor(month, pic_months, amplitude)
            price = generate_price(base_price, rfactor, sfact, trend)
            rows.append({
                "date":      date.strftime("%Y-%m-%d"),
                "annee":     year,
                "mois":      month,
                "region":    region,
                "marche":    marche,
                "categorie": cat,
                "produit":   produit,
                "unite":     unite,
                "prix_fcfa": price,
                "source":    "WFP/AgriPulse",
            })

df = pd.DataFrame(rows)
df = df.sort_values(["date", "region", "produit"]).reset_index(drop=True)

output_path = "prix_agricoles_cameroun.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"✅ CSV généré : {output_path}")
print(f"   Lignes    : {len(df):,}")
print(f"   Colonnes  : {list(df.columns)}")
print(f"\nAperçu (10 dernières lignes) :")
print(df.tail(10).to_string())
print(f"\nStatistiques prix (FCFA/unité) par catégorie :")
print(df.groupby("categorie")["prix_fcfa"].describe().round(0))