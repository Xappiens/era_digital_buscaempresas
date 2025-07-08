#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper de detalles de empresas de Axesor con almacenamiento en SQLite
Extrae información detallada de empresas y la guarda en base de datos SQLite
"""

import requests
import pandas as pd
import sqlite3
import logging
import re
import json
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import argparse
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_detalles_sqlite.log'),
        logging.StreamHandler()
    ]
)

class ScraperDetallesSQLite:
    def __init__(self, db_path='empresas_murcia.db'):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.init_database()

    def init_database(self):
        """Inicializa la base de datos SQLite con las tablas necesarias"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Tabla principal de empresas con detalles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS empresas_detalles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    razon_social TEXT NOT NULL,
                    municipio TEXT,
                    codigo_postal TEXT,
                    direccion TEXT,
                    telefono TEXT,
                    cif TEXT,
                    sitio_web TEXT,
                    email TEXT,
                    fecha_constitucion TEXT,
                    cnae TEXT,
                    objeto_social TEXT,
                    url_detalles TEXT UNIQUE,
                    fecha_extraccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabla de estadísticas de procesamiento
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS estadisticas_procesamiento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_empresas INTEGER,
                    empresas_procesadas INTEGER,
                    empresas_con_direccion INTEGER,
                    empresas_con_telefono INTEGER,
                    empresas_con_cif INTEGER,
                    empresas_con_web INTEGER,
                    empresas_con_email INTEGER,
                    empresas_con_fecha INTEGER,
                    empresas_con_cnae INTEGER,
                    empresas_con_objeto INTEGER,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            conn.close()
            logging.info(f"Base de datos inicializada: {self.db_path}")

        except Exception as e:
            logging.error(f"Error inicializando base de datos: {e}")
            raise

    def cargar_empresas_desde_csv(self, archivo_csv):
        """Carga las empresas desde el archivo CSV"""
        try:
            df = pd.read_csv(archivo_csv)
            logging.info(f"Cargadas {len(df)} empresas desde {archivo_csv}")
            return df
        except Exception as e:
            logging.error(f"Error cargando CSV: {e}")
            raise

    def empresa_ya_procesada(self, url_detalles):
        """Verifica si una empresa ya fue procesada"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM empresas_detalles WHERE url_detalles = ?", (url_detalles,))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except Exception as e:
            logging.error(f"Error verificando empresa procesada: {e}")
            return False

    def guardar_empresa_en_db(self, datos_empresa):
        """Guarda los datos de una empresa en la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO empresas_detalles
                (razon_social, municipio, codigo_postal, direccion, telefono, cif,
                 sitio_web, email, fecha_constitucion, cnae, objeto_social, url_detalles)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datos_empresa['razon_social'],
                datos_empresa['municipio'],
                datos_empresa['codigo_postal'],
                datos_empresa['direccion'],
                datos_empresa['telefono'],
                datos_empresa['cif'],
                datos_empresa['sitio_web'],
                datos_empresa['email'],
                datos_empresa['fecha_constitucion'],
                datos_empresa['cnae'],
                datos_empresa['objeto_social'],
                datos_empresa['url_detalles']
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logging.error(f"Error guardando empresa en DB: {e}")
            return False

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas de procesamiento en la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Obtener estadísticas actuales
            cursor.execute("SELECT COUNT(*) FROM empresas_detalles")
            total_empresas = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM empresas_detalles WHERE direccion IS NOT NULL AND direccion != ''")
            empresas_con_direccion = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM empresas_detalles WHERE telefono IS NOT NULL AND telefono != ''")
            empresas_con_telefono = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM empresas_detalles WHERE cif IS NOT NULL AND cif != ''")
            empresas_con_cif = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM empresas_detalles WHERE sitio_web IS NOT NULL AND sitio_web != '' AND sitio_web != 'N/A'")
            empresas_con_web = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM empresas_detalles WHERE email IS NOT NULL AND email != ''")
            empresas_con_email = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM empresas_detalles WHERE fecha_constitucion IS NOT NULL AND fecha_constitucion != ''")
            empresas_con_fecha = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM empresas_detalles WHERE cnae IS NOT NULL AND cnae != ''")
            empresas_con_cnae = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM empresas_detalles WHERE objeto_social IS NOT NULL AND objeto_social != ''")
            empresas_con_objeto = cursor.fetchone()[0]

            # Insertar o actualizar estadísticas
            cursor.execute('''
                INSERT OR REPLACE INTO estadisticas_procesamiento
                (id, total_empresas, empresas_procesadas, empresas_con_direccion,
                 empresas_con_telefono, empresas_con_cif, empresas_con_web,
                 empresas_con_email, empresas_con_fecha, empresas_con_cnae,
                 empresas_con_objeto, fecha_actualizacion)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                total_empresas, total_empresas, empresas_con_direccion,
                empresas_con_telefono, empresas_con_cif, empresas_con_web,
                empresas_con_email, empresas_con_fecha, empresas_con_cnae,
                empresas_con_objeto
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logging.error(f"Error actualizando estadísticas: {e}")

    def obtener_estadisticas(self):
        """Obtiene las estadísticas actuales de la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM estadisticas_procesamiento ORDER BY fecha_actualizacion DESC LIMIT 1")
            stats = cursor.fetchone()

            conn.close()

            if stats:
                return {
                    'total_empresas': stats[1],
                    'empresas_procesadas': stats[2],
                    'empresas_con_direccion': stats[3],
                    'empresas_con_telefono': stats[4],
                    'empresas_con_cif': stats[5],
                    'empresas_con_web': stats[6],
                    'empresas_con_email': stats[7],
                    'empresas_con_fecha': stats[8],
                    'empresas_con_cnae': stats[9],
                    'empresas_con_objeto': stats[10]
                }
            return None

        except Exception as e:
            logging.error(f"Error obteniendo estadísticas: {e}")
            return None

    def extraer_direccion(self, soup):
        """Extrae la dirección de la empresa"""
        try:
            # Buscar en la tabla de la ficha
            elementos = soup.find_all('td', string=re.compile(r'Dirección:', re.IGNORECASE))
            for elemento in elementos:
                siguiente_td = elemento.find_next_sibling('td')
                if siguiente_td:
                    direccion = siguiente_td.get_text(strip=True)
                    if direccion:
                        return direccion

            return None
        except Exception as e:
            logging.error(f"Error extrayendo dirección: {e}")
            return None

    def extraer_telefono(self, soup):
        """Extrae el teléfono de la empresa"""
        try:
            # Buscar en la tabla de la ficha
            elementos = soup.find_all('td', string=re.compile(r'Teléfono:', re.IGNORECASE))
            for elemento in elementos:
                siguiente_td = elemento.find_next_sibling('td')
                if siguiente_td:
                    telefono = siguiente_td.get_text(strip=True)
                    if telefono:
                        # Limpiar teléfono (quitar decimales y texto extra)
                        telefono_limpio = re.sub(r'[^\d]', '', telefono)
                        if telefono_limpio:
                            return telefono_limpio

            return None
        except Exception as e:
            logging.error(f"Error extrayendo teléfono: {e}")
            return None

    def extraer_cif(self, soup):
        """Extrae el CIF de la empresa"""
        try:
            # Buscar en la tabla de la ficha
            elementos = soup.find_all('td', string=re.compile(r'CIF:', re.IGNORECASE))
            for elemento in elementos:
                siguiente_td = elemento.find_next_sibling('td')
                if siguiente_td:
                    cif = siguiente_td.get_text(strip=True)
                    if cif:
                        return cif

            return None
        except Exception as e:
            logging.error(f"Error extrayendo CIF: {e}")
            return None

    def extraer_sitio_web(self, soup):
        """Extrae el sitio web de la empresa"""
        try:
            # Buscar específicamente en la tabla de la ficha (td tras 'Sitio web:')
            elementos = soup.find_all('td', string=re.compile(r'Sitio web:', re.IGNORECASE))
            for elemento in elementos:
                siguiente_td = elemento.find_next_sibling('td')
                if siguiente_td:
                    web = siguiente_td.get_text(strip=True)
                    if web and web != 'N/A' and web != '':
                        return web

            return None
        except Exception as e:
            logging.error(f"Error extrayendo sitio web: {e}")
            return None

    def extraer_email(self, soup):
        """Extrae el email de la empresa"""
        try:
            # Buscar específicamente en la tabla de la ficha (td tras 'Email:')
            elementos = soup.find_all('td', string=re.compile(r'Email:', re.IGNORECASE))
            for elemento in elementos:
                siguiente_td = elemento.find_next_sibling('td')
                if siguiente_td:
                    email = siguiente_td.get_text(strip=True)
                    if email and '@' in email:
                        return email

            return None
        except Exception as e:
            logging.error(f"Error extrayendo email: {e}")
            return None

    def extraer_fecha_constitucion(self, soup):
        """Extrae la fecha de constitución de la empresa"""
        try:
            # Buscar en la tabla de la ficha
            elementos = soup.find_all('td', string=re.compile(r'Fecha de constitución:', re.IGNORECASE))
            for elemento in elementos:
                siguiente_td = elemento.find_next_sibling('td')
                if siguiente_td:
                    fecha = siguiente_td.get_text(strip=True)
                    if fecha:
                        return fecha

            return None
        except Exception as e:
            logging.error(f"Error extrayendo fecha de constitución: {e}")
            return None

    def extraer_cnae(self, soup):
        """Extrae el CNAE de la empresa"""
        try:
            # Buscar en la tabla de la ficha
            elementos = soup.find_all('td', string=re.compile(r'CNAE:', re.IGNORECASE))
            for elemento in elementos:
                siguiente_td = elemento.find_next_sibling('td')
                if siguiente_td:
                    cnae = siguiente_td.get_text(strip=True)
                    if cnae:
                        # Limpiar CNAE (quitar decimales)
                        cnae_limpio = re.sub(r'[^\d]', '', cnae)
                        if cnae_limpio:
                            return cnae_limpio

            return None
        except Exception as e:
            logging.error(f"Error extrayendo CNAE: {e}")
            return None

    def extraer_objeto_social(self, soup):
        """Extrae el objeto social de la empresa"""
        try:
            # Buscar en la tabla de la ficha
            elementos = soup.find_all('td', string=re.compile(r'Objeto social:', re.IGNORECASE))
            for elemento in elementos:
                siguiente_td = elemento.find_next_sibling('td')
                if siguiente_td:
                    objeto = siguiente_td.get_text(strip=True)
                    if objeto:
                        return objeto

            return None
        except Exception as e:
            logging.error(f"Error extrayendo objeto social: {e}")
            return None

    def procesar_empresa(self, url_detalles, razon_social, municipio, codigo_postal):
        """Procesa una empresa individual y extrae todos sus detalles"""
        try:
            # Verificar si ya fue procesada
            if self.empresa_ya_procesada(url_detalles):
                logging.info(f"Empresa ya procesada: {razon_social}")
                return None

            logging.info(f"Procesando: {url_detalles}")

            # Hacer petición HTTP
            response = self.session.get(url_detalles, timeout=30)
            response.raise_for_status()

            # Parsear HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extraer todos los campos
            direccion = self.extraer_direccion(soup)
            telefono = self.extraer_telefono(soup)
            cif = self.extraer_cif(soup)
            sitio_web = self.extraer_sitio_web(soup)
            email = self.extraer_email(soup)
            fecha_constitucion = self.extraer_fecha_constitucion(soup)
            cnae = self.extraer_cnae(soup)
            objeto_social = self.extraer_objeto_social(soup)

            # Contar campos extraídos
            campos_extraidos = sum([
                1 if direccion else 0,
                1 if telefono else 0,
                1 if cif else 0,
                1 if sitio_web else 0,
                1 if email else 0,
                1 if fecha_constitucion else 0,
                1 if cnae else 0,
                1 if objeto_social else 0
            ])

            logging.info(f"  Extraídos {campos_extraidos}/8 campos")

            # Crear diccionario con los datos
            datos_empresa = {
                'razon_social': razon_social,
                'municipio': municipio,
                'codigo_postal': codigo_postal,
                'direccion': direccion,
                'telefono': telefono,
                'cif': cif,
                'sitio_web': sitio_web,
                'email': email,
                'fecha_constitucion': fecha_constitucion,
                'cnae': cnae,
                'objeto_social': objeto_social,
                'url_detalles': url_detalles
            }

            # Guardar en base de datos
            if self.guardar_empresa_en_db(datos_empresa):
                logging.info(f"  Guardada en DB: {razon_social}")
                return datos_empresa
            else:
                logging.error(f"  Error guardando en DB: {razon_social}")
                return None

        except Exception as e:
            logging.error(f"Error procesando empresa {razon_social}: {e}")
            return None

    def procesar_empresas(self, max_empresas=None):
        """Procesa todas las empresas del CSV"""
        try:
            # Encontrar el archivo CSV más reciente
            archivos_csv = [f for f in os.listdir('.') if f.startswith('empresas_axesor_') and f.endswith('.csv')]
            if not archivos_csv:
                raise FileNotFoundError("No se encontró archivo CSV de empresas")

            archivo_csv = max(archivos_csv)
            logging.info(f"Usando archivo: {archivo_csv}")

            # Cargar empresas
            df = self.cargar_empresas_desde_csv(archivo_csv)

            # Cargar códigos postales
            df_cp = pd.read_csv('municipios_pedanias_codigos_postales_corregidos.csv')

            # Procesar empresas
            empresas_procesadas = 0
            empresas_exitosas = 0

            for idx, row in df.iterrows():
                if max_empresas and empresas_procesadas >= max_empresas:
                    break

                # Buscar código postal
                codigo_postal = None
                for _, row_cp in df_cp.iterrows():
                    if row_cp['municipio'].lower() == row['municipio'].lower():
                        codigo_postal = str(row_cp['codigo_postal'])
                        break

                if not codigo_postal:
                    codigo_postal = 'N/A'

                # Procesar empresa
                resultado = self.procesar_empresa(
                    row['url_detalles'],
                    row['razon_social'],
                    row['municipio'],
                    codigo_postal
                )

                empresas_procesadas += 1
                if resultado:
                    empresas_exitosas += 1

                # Actualizar estadísticas cada 10 empresas
                if empresas_procesadas % 10 == 0:
                    self.actualizar_estadisticas()
                    stats = self.obtener_estadisticas()
                    if stats:
                        logging.info(f"📊 Progreso: {empresas_procesadas} procesadas, {stats['total_empresas']} en DB")

                # Pausa entre peticiones
                time.sleep(random.uniform(1, 3))

            # Actualizar estadísticas finales
            self.actualizar_estadisticas()

            # Mostrar estadísticas finales
            stats = self.obtener_estadisticas()
            if stats:
                self.mostrar_estadisticas(stats)

            logging.info(f"✅ Procesamiento completado: {empresas_exitosas}/{empresas_procesadas} empresas procesadas")

        except Exception as e:
            logging.error(f"Error en procesamiento: {e}")
            raise

    def mostrar_estadisticas(self, stats):
        """Muestra las estadísticas de procesamiento"""
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS DE DETALLES EXTRAÍDOS")
        print("="*60)
        total = int(stats['total_empresas'])
        print(f"Total de empresas en DB: {total}")
        print(f"Empresas con direccion: {int(stats['empresas_con_direccion'])} ({int(stats['empresas_con_direccion'])/total*100:.1f}%)")
        print(f"Empresas con telefono: {int(stats['empresas_con_telefono'])} ({int(stats['empresas_con_telefono'])/total*100:.1f}%)")
        print(f"Empresas con cif: {int(stats['empresas_con_cif'])} ({int(stats['empresas_con_cif'])/total*100:.1f}%)")
        print(f"Empresas con sitio_web: {int(stats['empresas_con_web'])} ({int(stats['empresas_con_web'])/total*100:.1f}%)")
        print(f"Empresas con email: {int(stats['empresas_con_email'])} ({int(stats['empresas_con_email'])/total*100:.1f}%)")
        print(f"Empresas con fecha_constitucion: {int(stats['empresas_con_fecha'])} ({int(stats['empresas_con_fecha'])/total*100:.1f}%)")
        print(f"Empresas con cnae: {int(stats['empresas_con_cnae'])} ({int(stats['empresas_con_cnae'])/total*100:.1f}%)")
        print(f"Empresas con objeto_social: {int(stats['empresas_con_objeto'])} ({int(stats['empresas_con_objeto'])/total*100:.1f}%)")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Scraper de detalles de empresas con SQLite')
    parser.add_argument('--max-empresas', type=int, help='Número máximo de empresas a procesar')
    parser.add_argument('--db-path', default='empresas_murcia.db', help='Ruta de la base de datos SQLite')

    args = parser.parse_args()

    try:
        scraper = ScraperDetallesSQLite(args.db_path)

        if args.max_empresas:
            logging.info(f"Iniciando extracción de detalles para máximo {args.max_empresas} empresas")
        else:
            logging.info("Iniciando extracción de detalles para todas las empresas")

        scraper.procesar_empresas(args.max_empresas)

    except Exception as e:
        logging.error(f"Error en ejecución: {e}")
        raise

if __name__ == "__main__":
    main()
