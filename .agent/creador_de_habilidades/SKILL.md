---
name: Creador de Habilidades
description: Guía experta para diseñar y generar nuevas habilidades (skills) en el ecosistema Antigravity, asegurando consistencia, claridad y calidad en las instrucciones en español.
---

# Creador de Habilidades

Esta habilidad te convierte en un arquitecto de habilidades para agentes Antigravity. Tu objetivo es ayudar al usuario a encapsular conocimientos y flujos de trabajo en "Habilidades" reutilizables.

## Flujo de Trabajo

1.  **Entender el Propósito**:
    *   Pregunta al usuario qué problema resuelve esta habilidad o qué tarea automatiza.
    *   Identifica el nombre ideal (corto, descriptivo).

2.  **Estructura de Archivos**:
    *   Siempre crea una carpeta dedicada dentro de `skills/`. El nombre de la carpeta debe estar en `snake_case` (ej. `skills/mi_nueva_habilidad`).
    *   El archivo principal **SIEMPRE** debe llamarse `SKILL.md` y residir en la raíz de esa carpeta.

3.  **Contenido de `SKILL.md`**:
    *   **YAML Frontmatter**: Es obligatorio al inicio del archivo.
        ```yaml
        ---
        name: Nombre Legible de la Habilidad
        description: Breve descripción de qué hace y cuándo usarla.
        ---
        ```
    *   **Instrucciones**:
        *   Usa Markdown claro y estructurado.
        *   Escribe en el idioma solicitado por el usuario (por defecto español si el usuario habla español).
        *   Sé imperativo y directo (ej. "Usa la herramienta X", "Analiza el archivo Y").
        *   Si la habilidad requiere scripts complejos, sugiere crearlos en una subcarpeta `scripts/`.

4.  **Ejemplo de Prompt para Generar una Habilidad**:
    Cuando el usuario te pida crear una habilidad, tu respuesta (o la acción de `write_to_file`) debe generar algo como esto:

    ```markdown
    <!-- Archivo: skills/analisis_datos/SKILL.md -->
    ---
    name: Análisis de Datos
    description: Automatiza la limpieza y resumen estadístico de archivos CSV.
    ---
    
    # Análisis de Datos
    
    Sigue estos pasos para procesar los datos:
    1. Lee el archivo CSV indicado.
    2. ...
    ```

## Mejores Prácticas

*   **Modularidad**: Mantén las habilidades enfocadas en una sola responsabilidad.
*   **Claridad**: Las instrucciones son para que *tú* (el agente) las leas en el futuro. Sé preciso.
*   **Contexto**: Si la habilidad necesita herramientas específicas, menciónalas en la descripción.
