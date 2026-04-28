import pandas as pd
import os

DB_PATH = "data/agripulse_complet.csv"

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError("La base de données CSV est introuvable. Lancez le générateur.")
    return pd.read_csv(DB_PATH)

def save_to_db(new_data_df):
    # Simule l'écriture dans la base de données
    df = get_db_connection()
    df = pd.concat([df, new_data_df], ignore_index=True)
    df.to_csv(DB_PATH, index=False)
    return True