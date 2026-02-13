import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


# CONFIGURACIÓN: Nombre del archivo CSV
ARCHIVO_ORIGEN = "INCIDENCIAS CORREAS.csv"

def ejecutar_analisis_agrupado(path_archivo):
    """
    Realiza un análisis de temperatura agrupado por TAG_EQUIPO, 
    DESCRIPCION_COIMPONENTE y LADO_POLIN.
    """
    # 1. CARGA DE DATOS
    try:
        if not os.path.exists(path_archivo):
            print(f"ERROR: No se encuentra el archivo '{path_archivo}'.")
            return None

        df = pd.read_csv(path_archivo, low_memory=False)
        print(f"--- Datos cargados: {len(df)} registros iniciales ---")
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return None

    # 2. LIMPIEZA ESPECÍFICA DE TEMPERATURA
    # Eliminamos nulos en TEMP_F1 y aseguramos formato numérico
    # Eliminamos nulos en TEMP_F1 y aseguramos formato numérico
    filas_iniciales = len(df)
    df_clean = df.dropna(subset=['TEMP_F1']).copy()
    
    # Convertir a numérico, convirtiendo errores a NaN
    # Primero reemplazamos coma por punto para manejar decimales correctamente
    df_clean['TEMP_F1'] = df_clean['TEMP_F1'].astype(str).str.replace(',', '.', regex=False)
    df_clean['TEMP_F1'] = pd.to_numeric(df_clean['TEMP_F1'], errors='coerce')
    
    # Eliminar nuevamente NaNs generados por la conversión (ej. cadenas vacías o texto)
    df_clean = df_clean.dropna(subset=['TEMP_F1'])
    
    filas_finales = len(df_clean)
    filas_eliminadas = filas_iniciales - filas_finales
    
    print(f"Registros válidos tras limpiar TEMP_F1: {filas_finales} (Se eliminaron {filas_eliminadas} filas sin datos o inválidas)")

    # Eliminar columna ID_INSPECCION solicitada
    if 'ID_INSPECCION' in df_clean.columns:
        df_clean = df_clean.drop(columns=['ID_INSPECCION'])
        print("Columna 'ID_INSPECCION' eliminada.")

    # Guardar el archivo limpio completo (opcional, si se desea mantener todo)
    # path_destino = path_archivo.replace(".csv", "_CLEAN.csv")
    # df_clean.to_csv(path_destino, index=False)
    
    # CREACIÓN DE DATAFRAME df_v1 (Solicitud de Usuario)
    cols_v1 = ['ID_ INCIDENCIA', 'TEMP_F1', 'ESTADO_TEMP', 'FECHA_INSPECCION', 'TAG_EQUIPO', 'DESCRIPCION_COIMPONENTE', 'RUTA_INSP', 'ESTADO_V2']
    
    # Validar que existan las columnas antes de filtrar
    cols_presentes_v1 = [c for c in cols_v1 if c in df_clean.columns]
    faltantes = set(cols_v1) - set(cols_presentes_v1)
    
    if not faltantes:
        df_v1 = df_clean[cols_v1].copy()
        print(f"--- Creado df_v1 con {len(df_v1)} registros. ---")
        
        # Guardar df_v1
        path_v1 = path_archivo.replace(".csv", "_v1.csv")
        df_v1.to_csv(path_v1, index=False)
        print(f"--- Archivo df_v1 guardado en: {path_v1} ---")
    else:
        print(f"ADVERTENCIA: No se pudo crear df_v1. Faltan columnas: {faltantes}")
        # Si faltan columnas, guardamos df_clean tal cual como fallback
        path_backup = path_archivo.replace(".csv", "_LimpiezaGeneral.csv")
        df_clean.to_csv(path_backup, index=False)


    # 3. AGRUPACIÓN POR EQUIPO, COMPONENTE Y LADO
    # Definimos las tres columnas de agrupación solicitadas
    columnas_grupo = ['TAG_EQUIPO', 'DESCRIPCION_COIMPONENTE', 'LADO_POLIN']
    
    # Verificamos que todas las columnas existan en el archivo
    columnas_presentes = [col for col in columnas_grupo if col in df_clean.columns]
    
    if len(columnas_presentes) < 3:
        print(f"ADVERTENCIA: Faltan algunas columnas para la agrupación completa.")
        print(f"Columnas encontradas: {columnas_presentes}")
        if not columnas_presentes:
            return df_clean

    print(f"\n--- Análisis Agrupado por {', '.join(columnas_presentes)} ---")
    
    # Calculamos estadísticas detalladas por cada grupo
    resumen_grupos = df_clean.groupby(columnas_presentes)['TEMP_F1'].agg(
        Promedio='mean',
        Maximo='max',
        Minimo='min',
        Registros='count'
    ).reset_index()
    
    # Ordenar por temperatura máxima para identificar puntos críticos rápido
    resumen_grupos = resumen_grupos.sort_values(by='Maximo', ascending=False)
    
    print(resumen_grupos.to_string(index=False))

    # 4. VISUALIZACIÓN
    sns.set_theme(style="whitegrid")
    
    # Creamos una columna temporal para el eje X que combine Equipo y Componente
    # Esto evita que el gráfico sea confuso si un equipo tiene muchos componentes
    df_clean['EQUIPO_COMP'] = df_clean['TAG_EQUIPO'] + "\n(" + df_clean['DESCRIPCION_COIMPONENTE'].astype(str) + ")"
    
    plt.figure(figsize=(16, 8))
    
    # Boxplot para visualizar la dispersión y posibles sobrecalentamientos
    sns.boxplot(
        data=df_clean, 
        x='EQUIPO_COMP', 
        y='TEMP_F1', 
        hue='LADO_POLIN',
        palette='RdYlBu_r' # Colores de frío a calor
    )
    
    plt.title('Distribución de Temperatura por Equipo/Componente y Lado', fontsize=16)
    plt.xlabel('Equipo (Componente)', fontsize=12)
    plt.ylabel('Temperatura (°F)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Lado Polín', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    print("\n[INFO] Generando gráfico comparativo detallado...")
    plt.tight_layout()
    plt.show() 
    
    return resumen_grupos

if __name__ == "__main__":
    # Ejecución del análisis con la nueva jerarquía
    tabla_resumen = ejecutar_analisis_agrupado(ARCHIVO_ORIGEN)
    
    if tabla_resumen is not None:
        print("\nAnálisis por Equipo, Componente y Lado finalizado.")