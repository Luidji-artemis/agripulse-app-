"""
AgriPulse - Module Analytics
Algorithmes ML : Régression linéaire simple/multiple, ACP, K-Means, Classification
"""
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, r2_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings("ignore")

DATA_PATH   = os.path.join(os.path.dirname(__file__), "..", "data", "prix_agricoles_cameroun.csv")
MODELS_PATH = os.path.join(os.path.dirname(__file__), "..", "models")

# ─── CHARGEMENT DONNÉES ───────────────────────────────────────────────────────
_df_cache = None

def load_data() -> pd.DataFrame:
    global _df_cache
    if _df_cache is None:
        _df_cache = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
        _df_cache["date"] = pd.to_datetime(_df_cache["date"])
        _df_cache["mois_num"] = _df_cache["mois"]
        # Normaliser les noms de colonnes
        _df_cache.columns = _df_cache.columns.str.lower().str.strip()
    return _df_cache

def get_categories():
    df = load_data()
    return sorted(df["categorie"].unique().tolist())

def get_produits_par_categorie(categorie: str):
    df = load_data()
    if categorie:
        return sorted(df[df["categorie"] == categorie]["produit"].unique().tolist())
    return sorted(df["produit"].unique().tolist())

def get_regions():
    df = load_data()
    return sorted(df["region"].unique().tolist())

def get_marches_par_region(region: str):
    df = load_data()
    if region:
        return sorted(df[df["region"] == region]["marche"].unique().tolist())
    return sorted(df["marche"].unique().tolist())

def get_unite(produit: str) -> str:
    df = load_data()
    row = df[df["produit"] == produit]
    if not row.empty:
        return row.iloc[0]["unite"]
    return "kg"

def get_prix_actuel(produit: str, region: str) -> dict:
    """Prix le plus récent pour un produit dans une région."""
    df = load_data()
    sub = df[(df["produit"] == produit) & (df["region"] == region)]
    if sub.empty:
        sub = df[df["produit"] == produit]
    latest = sub[sub["date"] == sub["date"].max()]
    prix_moyen = latest["prix_fcfa"].mean()
    marche = latest.iloc[0]["marche"] if not latest.empty else "N/A"
    return {
        "prix": round(prix_moyen),
        "marche": marche,
        "date": latest.iloc[0]["date"].strftime("%d/%m/%Y") if not latest.empty else "N/A",
        "unite": latest.iloc[0]["unite"] if not latest.empty else "kg",
    }

# ─── 1. RÉGRESSION LINÉAIRE SIMPLE ───────────────────────────────────────────
def regression_simple(produit: str, region: str) -> dict:
    """
    Régression simple : prix ~ temps (mois_index)
    Prédit le prix dans 1, 3 et 6 mois.
    """
    df = load_data()
    sub = df[(df["produit"] == produit) & (df["region"] == region)].copy()
    if sub.empty:
        sub = df[df["produit"] == produit].copy()

    # Indice temporel (mois depuis 2019-01)
    sub["t"] = (sub["annee"] - 2019) * 12 + sub["mois"]
    monthly = sub.groupby("t")["prix_fcfa"].mean().reset_index()
    monthly.columns = ["t", "prix"]
    monthly = monthly.sort_values("t")

    X = monthly[["t"]].values
    y = monthly["prix"].values

    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)

    t_max = int(monthly["t"].max())
    predictions = {}
    for horizon, label in [(1, "1 mois"), (3, "3 mois"), (6, "6 mois")]:
        t_fut = t_max + horizon
        pred = model.predict([[t_fut]])[0]
        predictions[label] = max(0, round(pred))

    return {
        "type": "regression_simple",
        "produit": produit,
        "region": region,
        "r2": round(r2, 3),
        "coef": round(float(model.coef_[0]), 2),
        "intercept": round(float(model.intercept_), 2),
        "tendance": "hausse" if model.coef_[0] > 0 else "baisse",
        "predictions": predictions,
        "historique_t": monthly["t"].tolist(),
        "historique_prix": monthly["prix"].round(0).tolist(),
        "fitted": y_pred.round(0).tolist(),
    }

# ─── 2. RÉGRESSION LINÉAIRE MULTIPLE ─────────────────────────────────────────
def regression_multiple(produit: str) -> dict:
    """
    Régression multiple : prix ~ mois + annee + region_encoded
    """
    df = load_data()
    sub = df[df["produit"] == produit].copy()
    if sub.empty:
        return {"error": "Produit non trouvé"}

    le = LabelEncoder()
    sub["region_enc"] = le.fit_transform(sub["region"])
    sub["t"] = (sub["annee"] - 2019) * 12 + sub["mois"]

    features = ["t", "mois", "region_enc"]
    X = sub[features].values
    y = sub["prix_fcfa"].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred_test = model.predict(X_test)
    r2 = r2_score(y_test, y_pred_test)

    # Sauvegarder modèle
    os.makedirs(MODELS_PATH, exist_ok=True)
    pkl_path = os.path.join(MODELS_PATH, f"reg_mult_{produit.replace(' ', '_')}.pkl")
    with open(pkl_path, "wb") as f:
        pickle.dump({"model": model, "le": le, "features": features}, f)

    coefs = dict(zip(features, model.coef_.round(3)))
    return {
        "type": "regression_multiple",
        "produit": produit,
        "r2": round(r2, 3),
        "coefs": coefs,
        "intercept": round(float(model.intercept_), 2),
        "regions": le.classes_.tolist(),
        "n_obs": len(sub),
    }

# ─── 3. ACP (RÉDUCTION DIMENSIONNALITÉ) ──────────────────────────────────────
def analyse_acp(region: str = None, n_components: int = 2) -> dict:
    """
    ACP sur la matrice produit × mois pour visualiser la structure des prix.
    """
    df = load_data()
    if region:
        df = df[df["region"] == region]

    pivot = df.pivot_table(index="produit", columns="mois", values="prix_fcfa", aggfunc="mean").fillna(0)
    if pivot.empty or pivot.shape[0] < 3:
        return {"error": "Données insuffisantes"}

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(pivot.values)

    n_components = min(n_components, pivot.shape[0] - 1, pivot.shape[1])
    pca = PCA(n_components=n_components)
    coords = pca.fit_transform(X_scaled)

    return {
        "type": "acp",
        "produits": pivot.index.tolist(),
        "coordonnees": coords.tolist(),
        "variance_expliquee": pca.explained_variance_ratio_.round(3).tolist(),
        "n_components": n_components,
    }

# ─── 4. K-MEANS CLUSTERING (NON SUPERVISÉ) ───────────────────────────────────
def kmeans_clustering(produit: str = None, k: int = 4) -> dict:
    """
    Cluster les marchés/régions selon leur profil de prix.
    """
    df = load_data()
    if produit:
        df = df[df["produit"] == produit]

    pivot = df.pivot_table(index="region", columns="mois", values="prix_fcfa", aggfunc="mean").fillna(0)
    if pivot.shape[0] < k:
        k = max(2, pivot.shape[0] - 1)

    scaler = StandardScaler()
    X = scaler.fit_transform(pivot.values)

    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    score = silhouette_score(X, labels) if len(set(labels)) > 1 else 0.0

    # Scores silhouette par point
    from sklearn.metrics import silhouette_samples
    sil_samples = silhouette_samples(X, labels).round(3).tolist()

    # PCA 2D pour visualisation
    pca = PCA(n_components=2)
    coords = pca.fit_transform(X)

    return {
        "type": "kmeans",
        "k": k,
        "produit": produit,
        "regions": pivot.index.tolist(),
        "labels": labels.tolist(),
        "silhouette_score": round(float(score), 3),
        "silhouette_samples": sil_samples,
        "coordonnees_2d": coords.tolist(),
        "inertia": round(float(km.inertia_), 2),
        "centres": km.cluster_centers_.tolist(),
    }

# ─── 5. CLASSIFICATION SUPERVISÉE ────────────────────────────────────────────
# ─── 5. CLASSIFICATION SUPERVISÉE ────────────────────────────────────────────
def classification_prix(produit: str) -> dict:
    """
    Classifie le niveau de prix : Bas / Moyen / Élevé.
    Algorithme : Random Forest.
    """
    df = load_data()
    sub = df[df["produit"] == produit].copy()
    if sub.empty or len(sub) < 50:
        return {"error": "Données insuffisantes"}

    q33 = sub["prix_fcfa"].quantile(0.33)
    q66 = sub["prix_fcfa"].quantile(0.66)

    def categorize(p):
        if p <= q33: return "Bas"
        elif p <= q66: return "Moyen"
        else: return "Élevé"

    sub["label"] = sub["prix_fcfa"].apply(categorize)

    le_region = LabelEncoder()
    sub["region_enc"] = le_region.fit_transform(sub["region"])
    sub["t"] = (sub["annee"] - 2019) * 12 + sub["mois"]

    # CORRECTION : Conversion explicite en types standards numpy
    X = sub[["t", "mois", "region_enc"]].astype(np.float64).to_numpy()
    y = sub["label"].astype(str).to_numpy()
    
    # Nettoyage des valeurs NaN ou infinies
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X_train, y_train)
    acc = clf.score(X_test, y_test)

    importances = dict(zip(["t", "mois", "region"], clf.feature_importances_.round(3)))
    return {
        "type": "classification",
        "produit": produit,
        "accuracy": round(acc, 3),
        "classes": ["Bas", "Moyen", "Élevé"],
        "importances": importances,
        "seuils": {"bas": round(q33), "moyen": round(q66)},
    }
    
# ─── 6. ANALYSE COMPLÈTE (orchestrateur) ─────────────────────────────────────
def analyse_complete(produit: str, region: str, prix_propose: float) -> dict:
    """
    Lance toutes les analyses et génère des recommandations.
    """
    reg_simple  = regression_simple(produit, region)
    kmeans_res  = kmeans_clustering(produit, k=4)
    classif_res = classification_prix(produit)

    # Prix actuel
    prix_actuel_info = get_prix_actuel(produit, region)
    prix_actuel      = prix_actuel_info["prix"]

    # Comparaison prix proposé vs marché
    diff_pct   = ((prix_propose - prix_actuel) / prix_actuel * 100) if prix_actuel > 0 else 0
    prix_1mois = reg_simple["predictions"].get("1 mois", prix_actuel)
    prix_3mois = reg_simple["predictions"].get("3 mois", prix_actuel)
    prix_6mois = reg_simple["predictions"].get("6 mois", prix_actuel)

    tendance   = reg_simple.get("tendance", "stable")

    # Recommandation principale
    if diff_pct < -15:
        conseil = "prix_sous_marche"
    elif diff_pct > 15:
        conseil = "prix_sur_marche"
    else:
        conseil = "prix_juste"

    return {
        "produit": produit,
        "region": region,
        "prix_propose": prix_propose,
        "prix_actuel_marche": prix_actuel,
        "diff_pct": round(diff_pct, 1),
        "conseil": conseil,
        "tendance": tendance,
        "r2": reg_simple["r2"],
        "predictions": {"1_mois": prix_1mois, "3_mois": prix_3mois, "6_mois": prix_6mois},
        "historique_t": reg_simple["historique_t"],
        "historique_prix": reg_simple["historique_prix"],
        "fitted": reg_simple["fitted"],
        "kmeans": kmeans_res,
        "classification": classif_res,
        "unite": prix_actuel_info["unite"],
        "marche_ref": prix_actuel_info["marche"],
    }

# ─── HEATMAP DATA ─────────────────────────────────────────────────────────────
def get_heatmap_data(produit: str = None) -> list:
    """Retourne les données pour la heatmap géographique."""
    df = load_data()
    if produit:
        df = df[df["produit"] == produit]

    latest_date = df["date"].max()
    recent = df[df["date"] >= latest_date - pd.Timedelta(days=30)]
    grouped = recent.groupby("region")["prix_fcfa"].mean().reset_index()
    grouped.columns = ["region", "prix_moyen"]
    grouped["prix_moyen"] = grouped["prix_moyen"].round(0)
    return grouped.to_dict("records")

def get_prix_aleatoire_live() -> dict:
    """Retourne un prix aléatoire pour l'affichage live en haut à gauche."""
    df = load_data()
    latest = df[df["date"] == df["date"].max()]
    row = latest.sample(1).iloc[0]
    return {
        "produit": row["produit"],
        "prix": int(row["prix_fcfa"]),
        "unite": row["unite"],
        "region": row["region"],
        "marche": row["marche"],
    }

def get_tendance_produit(produit: str, region: str = None, mois: int = 12) -> dict:
    """Historique + moyenne par mois sur les N derniers mois."""
    df = load_data()
    sub = df[df["produit"] == produit].copy()
    if region:
        sub = sub[sub["region"] == region]

    sub = sub.sort_values("date")
    latest = sub["date"].max()
    cutoff = latest - pd.Timedelta(days=mois * 30)
    recent = sub[sub["date"] >= cutoff]

    by_date = recent.groupby("date")["prix_fcfa"].mean().reset_index()
    by_date.columns = ["date", "prix"]
    by_date["date_str"] = by_date["date"].dt.strftime("%Y-%m-%d")

    return {
        "dates": by_date["date_str"].tolist(),
        "prix": by_date["prix"].round(0).tolist(),
        "produit": produit,
        "region": region or "Toutes régions",
        "min": round(float(by_date["prix"].min())),
        "max": round(float(by_date["prix"].max())),
        "moyenne": round(float(by_date["prix"].mean())),
    }