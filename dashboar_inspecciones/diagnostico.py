
import pandas as pd

archivo = "INCIDENCIAS CORREAS.csv"
try:
    df = pd.read_csv(archivo, low_memory=False)
    print("Muestra de columna TEMP_F1 (primeros 20):")
    print(df['TEMP_F1'].head(20).tolist())
    
    print("\nTipos de datos únicos en TEMP_F1:")
    print(df['TEMP_F1'].apply(type).value_counts())
    
    print("\nValores no nulos que NO son convertibles directamente (ejemplo):")
    # Intentar conversión y ver qué falla
    temp_numeric = pd.to_numeric(df['TEMP_F1'], errors='coerce')
    failed = df[temp_numeric.isna() & df['TEMP_F1'].notna()]['TEMP_F1']
    print(failed.unique()[:20])
    
except Exception as e:
    print(f"Error: {e}")
