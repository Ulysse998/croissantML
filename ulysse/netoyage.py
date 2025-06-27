import pandas as pd

# Lire le fichier CSV
df = pd.read_csv("sample_data.csv", sep=';')

# Dictionnaire pour convertir les mois en nombre
mois_en_nombre = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}

# Remplacer les noms de mois par leur numéro
df['Month'] = df['Month'].map(mois_en_nombre)

# Colonnes à conserver
colonnes_utiles = ['Station', 'ml filtrated', 'Year', 'Month', 'Day']
df_clean = df[colonnes_utiles].copy()

# Créer une colonne Date formatée
df_clean['Formatted_Date'] = pd.to_datetime(df_clean[['Year', 'Month', 'Day']])

# Sauvegarder le résultat
df_clean.to_csv("cleaned_sample_data.csv", index=False)

print("✅ Nettoyage terminé. Fichier 'cleaned_sample_data.csv' créé.")
