"""
Script para obtener el catálogo de Netflix (vía TMDb API)
y guardarlo en una base de datos MySQL.

Requisitos:
    pip install requests mysql-connector-python python-dotenv

Antes de correr:
    1. Crear un archivo .env con:
        TMDB_API_KEY=tu_api_key_aqui
        DB_HOST=localhost
        DB_USER=root
        DB_PASSWORD=tu_password
        DB_NAME=netflix_catalog
    2. Haber corrido netflix_db.sql para crear las tablas.
"""

import os
import time
import requests
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

# Netflix = provider_id 8 en TMDb
NETFLIX_PROVIDER_ID = 8

# Configuración: país y tipo de contenido a scrapear
PAIS = "AR"  # cambiá a "US", "MX", "ES", etc. según lo que necesites
TIPOS = ["movie", "tv"]  # películas y series
MAX_PAGINAS = 50  # TMDb pagina de a 20 resultados; ajustá según cuánto quieras traer


def conectar_db():
    try:
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "netflix_catalog"),
        )
        return conexion
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        raise


def obtener_pagina(tipo, pagina):
    """Descubre títulos disponibles en Netflix usando el endpoint /discover."""
    url = f"{BASE_URL}/discover/{tipo}"
    params = {
        "api_key": TMDB_API_KEY,
        "with_watch_providers": NETFLIX_PROVIDER_ID,
        "watch_region": PAIS,
        "language": "es-ES",
        "sort_by": "popularity.desc",
        "page": pagina,
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def guardar_generos(cursor, generos):
    """Guarda el catálogo de géneros de TMDb (si no existen)."""
    for g in generos:
        cursor.execute(
            "INSERT IGNORE INTO generos (id, nombre) VALUES (%s, %s)",
            (g["id"], g["name"]),
        )


def obtener_lista_generos(tipo):
    url = f"{BASE_URL}/genre/{tipo}/list"
    params = {"api_key": TMDB_API_KEY, "language": "es-ES"}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json().get("genres", [])


def guardar_titulo(cursor, item, tipo):
    titulo = item.get("title") or item.get("name")
    titulo_original = item.get("original_title") or item.get("original_name")
    fecha = item.get("release_date") or item.get("first_air_date") or None
    if fecha == "":
        fecha = None

    cursor.execute(
        """
        INSERT INTO titulos
            (tmdb_id, tipo, titulo, titulo_original, sinopsis, fecha_estreno,
             idioma_original, popularidad, rating_promedio, cantidad_votos,
             poster_path, pais_disponible)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            popularidad = VALUES(popularidad),
            rating_promedio = VALUES(rating_promedio),
            cantidad_votos = VALUES(cantidad_votos),
            fecha_scrapeo = CURRENT_TIMESTAMP
        """,
        (
            item["id"],
            tipo,
            titulo,
            titulo_original,
            item.get("overview"),
            fecha,
            item.get("original_language"),
            item.get("popularity"),
            item.get("vote_average"),
            item.get("vote_count"),
            item.get("poster_path"),
            PAIS,
        ),
    )

    # Recuperar el id interno para relacionar géneros
    cursor.execute(
        "SELECT id FROM titulos WHERE tmdb_id=%s AND tipo=%s AND pais_disponible=%s",
        (item["id"], tipo, PAIS),
    )
    fila = cursor.fetchone()
    if not fila:
        return
    titulo_id = fila[0]

    for genero_id in item.get("genre_ids", []):
        cursor.execute(
            "INSERT IGNORE INTO titulo_genero (titulo_id, genero_id) VALUES (%s, %s)",
            (titulo_id, genero_id),
        )


def main():
    if not TMDB_API_KEY:
        raise SystemExit("Falta TMDB_API_KEY en el archivo .env")

    conexion = conectar_db()
    cursor = conexion.cursor()

    for tipo in TIPOS:
        print(f"\n=== Descargando géneros de '{tipo}' ===")
        generos = obtener_lista_generos(tipo)
        guardar_generos(cursor, generos)
        conexion.commit()

        print(f"=== Descargando catálogo de Netflix ({tipo}) - país {PAIS} ===")
        pagina = 1
        total_guardados = 0

        while pagina <= MAX_PAGINAS:
            data = obtener_pagina(tipo, pagina)
            resultados = data.get("results", [])
            if not resultados:
                break

            for item in resultados:
                guardar_titulo(cursor, item, tipo)
                total_guardados += 1

            conexion.commit()
            print(f"  Página {pagina}/{data.get('total_pages', '?')} guardada "
                  f"({total_guardados} títulos hasta ahora)")

            if pagina >= data.get("total_pages", 1):
                break

            pagina += 1
            time.sleep(0.3)  # para no saturar la API

        print(f"Total {tipo} guardados: {total_guardados}")

    cursor.close()
    conexion.close()
    print("\n✅ Proceso terminado.")


if __name__ == "__main__":
    main()
