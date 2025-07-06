import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import re
import json
from urllib.parse import urljoin, urlparse
import logging
from datetime import datetime
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class ScraperAvanzado:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

        self.empresas_encontradas = []
        self.urls_procesadas = set()

    def cargar_codigos_postales(self, archivo_csv):
        """Carga los códigos postales únicos del CSV"""
        try:
            df = pd.read_csv(archivo_csv)
            codigos_unicos = df['codigo_postal'].unique()
            logging.info(f"Se cargaron {len(codigos_unicos)} códigos postales únicos")
            return codigos_unicos
        except Exception as e:
            logging.error(f"Error al cargar el CSV: {e}")
            return []

    def buscar_en_google_avanzado(self, codigo_postal, max_paginas=3):
        """Búsqueda avanzada en Google con más fuentes"""
        empresas = []

        from config import Config
        queries = Config.QUERIES_GOOGLE

        for query in queries:
            query_formatted = query.format(codigo_postal=codigo_postal)
            for pagina in range(1, max_paginas + 1):
                try:
                    url = f"https://www.google.com/search?q={query_formatted}&start={(pagina-1)*10}"
                    response = self.session.get(url, timeout=15)

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')

                        # Buscar resultados de Google
                        for resultado in soup.find_all(['div', 'article'], class_=['g', 'result']):
                            titulo_elem = resultado.find(['h3', 'h2', 'a'])
                            enlace_elem = resultado.find('a')

                            if titulo_elem and enlace_elem:
                                titulo = titulo_elem.get_text().strip()
                                enlace = enlace_elem.get('href')

                                # Filtrar enlaces válidos
                                if enlace and enlace.startswith('http') and enlace not in self.urls_procesadas:
                                    self.urls_procesadas.add(enlace)

                                    # Extraer datos de la página
                                    datos_empresa = self.extraer_datos_pagina(enlace, codigo_postal)
                                    if datos_empresa:
                                        empresas.append(datos_empresa)

                    time.sleep(random.uniform(2, 4))

                except Exception as e:
                    logging.error(f"Error en búsqueda Google: {e}")
                    continue

        return empresas

    def buscar_en_paginas_amarillas(self, codigo_postal):
        """Busca en Páginas Amarillas"""
        try:
            url = f"https://www.paginasamarillas.es/buscar/empresas/{codigo_postal}"
            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                empresas = []

                # Buscar empresas en los resultados
                for empresa in soup.find_all('div', class_=['result-item', 'business-item']):
                    nombre = empresa.find(['h2', 'h3', 'a'])
                    direccion = empresa.find(['span', 'p'], class_=['address', 'direccion'])
                    telefono = empresa.find(['span', 'a'], class_=['phone', 'telefono'])

                    if nombre:
                        empresa_data = {
                            'razon_social': nombre.get_text().strip(),
                            'direccion': direccion.get_text().strip() if direccion else "",
                            'telefono': telefono.get_text().strip() if telefono else "",
                            'codigo_postal': codigo_postal,
                            'fuente': 'Páginas Amarillas'
                        }

                        # Extraer CIF si está disponible
                        cif = self.extraer_cif_de_texto(nombre.get_text() + " " + (direccion.get_text() if direccion else ""))
                        if cif:
                            empresa_data['cif'] = cif

                        empresas.append(empresa_data)

                return empresas
            else:
                return []

        except Exception as e:
            logging.error(f"Error en Páginas Amarillas: {e}")
            return []

    def buscar_en_infoempresas(self, codigo_postal):
        """Busca en InfoEmpresas"""
        try:
            url = f"https://www.infoempresas.com/empresas-codigo-postal-{codigo_postal}"
            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                empresas = []

                # Buscar empresas en los resultados
                for empresa in soup.find_all('div', class_=['empresa', 'company']):
                    nombre = empresa.find(['h2', 'h3', 'a'])
                    direccion = empresa.find(['span', 'p'], class_=['direccion', 'address'])
                    cnae = empresa.find(['span', 'div'], class_=['cnae', 'activity'])

                    if nombre:
                        empresa_data = {
                            'razon_social': nombre.get_text().strip(),
                            'direccion': direccion.get_text().strip() if direccion else "",
                            'cnae': cnae.get_text().strip() if cnae else "",
                            'codigo_postal': codigo_postal,
                            'fuente': 'InfoEmpresas'
                        }

                        # Extraer CIF
                        cif = self.extraer_cif_de_texto(nombre.get_text() + " " + (direccion.get_text() if direccion else ""))
                        if cif:
                            empresa_data['cif'] = cif

                        empresas.append(empresa_data)

                return empresas
            else:
                return []

        except Exception as e:
            logging.error(f"Error en InfoEmpresas: {e}")
            return []

    def extraer_cif_de_texto(self, texto):
        """Extrae CIF del texto usando patrones regex"""
        from config import Config

        for patron in Config.PATRONES_CIF:
            matches = re.findall(patron, texto, re.IGNORECASE)
            if matches:
                for match in matches:
                    # Si el patrón tiene grupos, tomar el primer grupo
                    if isinstance(match, tuple):
                        cif = match[0]
                    else:
                        cif = match

                    # Validar CIF
                    if Config.validar_cif(cif):
                        return cif.upper()

        return None

    def extraer_datos_pagina(self, url, codigo_postal):
        """Extrae datos detallados de una página web"""
        try:
            response = self.session.get(url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Buscar nombre de empresa
                nombre_empresa = ""
                for selector in ['h1', 'h2', '.company-name', '.empresa-nombre', 'title']:
                    elem = soup.select_one(selector)
                    if elem:
                        nombre_empresa = elem.get_text().strip()
                        break

                if not nombre_empresa:
                    return None

                # Buscar dirección
                direccion = ""
                for selector in ['.address', '.direccion', '.location', '[itemprop="address"]']:
                    elem = soup.select_one(selector)
                    if elem:
                        direccion = elem.get_text().strip()
                        break

                # Buscar email
                email = ""
                from config import Config
                email_pattern = Config.PATRONES_EMAIL[0]
                emails = re.findall(email_pattern, response.text)
                if emails:
                    email = emails[0]

                # Buscar teléfono
                telefono = ""
                telefono_pattern = r'(\+34\s?)?[6-9]\d{8}'
                telefonos = re.findall(telefono_pattern, response.text)
                if telefonos:
                    telefono = telefonos[0]

                # Buscar CIF
                cif = self.extraer_cif_de_texto(response.text)

                # Buscar CNAE
                cnae = ""
                cnae_patterns = [
                    r'CNAE[:\s]*(\d{4})',
                    r'Actividad[:\s]*(\d{4})',
                    r'Código[:\s]*(\d{4})'
                ]
                for pattern in cnae_patterns:
                    match = re.search(pattern, response.text, re.IGNORECASE)
                    if match:
                        cnae = match.group(1)
                        break

                return {
                    'razon_social': nombre_empresa,
                    'direccion': direccion,
                    'codigo_postal': codigo_postal,
                    'email': email,
                    'telefono': telefono,
                    'cif': cif,
                    'cnae': cnae,
                    'fuente': 'Web scraping',
                    'url': url
                }
            else:
                return None

        except Exception as e:
            logging.error(f"Error al extraer datos de {url}: {e}")
            return None

    def buscar_en_redes_sociales(self, codigo_postal):
        """Busca empresas en redes sociales y directorios locales"""
        empresas = []

        # Buscar en Facebook Business
        try:
            url = f"https://www.facebook.com/pages/category/Local-Business/?q={codigo_postal}"
            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Implementar extracción de datos de Facebook
                pass
        except Exception as e:
            logging.error(f"Error en Facebook: {e}")

        return empresas

    def procesar_codigo_postal_avanzado(self, codigo_postal):
        """Procesa un código postal con múltiples fuentes"""
        logging.info(f"Procesando código postal: {codigo_postal}")

        empresas_codigo = []

        # 1. Búsqueda en Google avanzada
        logging.info("  Buscando en Google...")
        empresas_google = self.buscar_en_google_avanzado(codigo_postal)
        empresas_codigo.extend(empresas_google)

        # 2. Páginas Amarillas
        logging.info("  Buscando en Páginas Amarillas...")
        empresas_pa = self.buscar_en_paginas_amarillas(codigo_postal)
        empresas_codigo.extend(empresas_pa)

        # 3. InfoEmpresas
        logging.info("  Buscando en InfoEmpresas...")
        empresas_info = self.buscar_en_infoempresas(codigo_postal)
        empresas_codigo.extend(empresas_info)

        # 4. Redes sociales
        logging.info("  Buscando en redes sociales...")
        empresas_redes = self.buscar_en_redes_sociales(codigo_postal)
        empresas_codigo.extend(empresas_redes)

        # Eliminar duplicados basándose en CIF y nombre
        empresas_unicas = self.eliminar_duplicados_avanzado(empresas_codigo)

        logging.info(f"  Encontradas {len(empresas_unicas)} empresas únicas para el código postal {codigo_postal}")
        return empresas_unicas

    def eliminar_duplicados_avanzado(self, empresas):
        """Elimina empresas duplicadas basándose en CIF, nombre y dirección"""
        empresas_unicas = []
        cif_vistos = set()
        nombres_vistos = set()

        # Ordenar empresas por prioridad (con CIF primero)
        empresas_ordenadas = sorted(empresas, key=lambda x: (x.get('cif') is None, x.get('razon_social', '')))

        for empresa in empresas_ordenadas:
            razon_social = empresa.get('razon_social', '').lower().strip()
            cif = empresa.get('cif', '').upper().strip()

            # Si tiene CIF, usar CIF para deduplicación
            if cif and cif not in cif_vistos:
                cif_vistos.add(cif)
                empresas_unicas.append(empresa)
                logging.debug(f"Empresa agregada por CIF único: {cif} - {razon_social}")

            # Si no tiene CIF, usar nombre
            elif not cif and razon_social and razon_social not in nombres_vistos:
                nombres_vistos.add(razon_social)
                empresas_unicas.append(empresa)
                logging.debug(f"Empresa agregada por nombre único: {razon_social}")

        logging.info(f"Deduplicación: {len(empresas)} -> {len(empresas_unicas)} empresas únicas")
        return empresas_unicas

    def ejecutar_busqueda_avanzada(self, archivo_csv, max_codigos=None):
        """Ejecuta la búsqueda avanzada completa"""
        logging.info("Iniciando búsqueda avanzada de empresas...")

        # Cargar códigos postales
        codigos_postales = self.cargar_codigos_postales(archivo_csv)

        if max_codigos:
            codigos_postales = codigos_postales[:max_codigos]

        total_empresas = 0

        for i, codigo in enumerate(codigos_postales, 1):
            logging.info(f"Progreso: {i}/{len(codigos_postales)}")

            empresas = self.procesar_codigo_postal_avanzado(codigo)
            self.empresas_encontradas.extend(empresas)
            total_empresas += len(empresas)

            # Pausa entre códigos postales
            time.sleep(random.uniform(5, 10))

        logging.info(f"Búsqueda completada. Total de empresas encontradas: {total_empresas}")
        return self.empresas_encontradas

    def guardar_resultados_avanzados(self, archivo_salida="empresas_avanzadas.xlsx"):
        """Guarda los resultados con formato avanzado"""
        if not self.empresas_encontradas:
            logging.warning("No hay empresas para guardar")
            return

        df = pd.DataFrame(self.empresas_encontradas)

        # Reorganizar columnas incluyendo CIF
        columnas_orden = ['razon_social', 'cif', 'direccion', 'codigo_postal', 'cnae', 'email', 'telefono', 'fuente', 'url']
        df = df.reindex(columns=columnas_orden)

        # Limpiar datos
        df = df.dropna(subset=['razon_social'])
        df = df[df['razon_social'].str.len() > 2]

        # Guardar en Excel con formato
        with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Empresas', index=False)

            # Obtener el workbook y worksheet
            workbook = writer.book
            worksheet = writer.sheets['Empresas']

            # Ajustar ancho de columnas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        logging.info(f"Resultados guardados en: {archivo_salida}")

        # También guardar en CSV
        archivo_csv = archivo_salida.replace('.xlsx', '.csv')
        df.to_csv(archivo_csv, index=False, encoding='utf-8-sig')
        logging.info(f"Resultados también guardados en: {archivo_csv}")

        # Generar estadísticas
        self.generar_estadisticas(df)

    def generar_estadisticas(self, df):
        """Genera estadísticas de los resultados"""
        stats = {
            'total_empresas': len(df),
            'empresas_con_cif': len(df[df['cif'].notna() & (df['cif'] != '')]),
            'empresas_con_email': len(df[df['email'].notna() & (df['email'] != '')]),
            'empresas_con_telefono': len(df[df['telefono'].notna() & (df['telefono'] != '')]),
            'empresas_con_cnae': len(df[df['cnae'].notna() & (df['cnae'] != '')]),
            'fuentes_utilizadas': df['fuente'].value_counts().to_dict()
        }

        logging.info("Estadísticas de la búsqueda:")
        for key, value in stats.items():
            logging.info(f"  {key}: {value}")

def main():
    # Crear instancia del scraper avanzado
    scraper = ScraperAvanzado()

    # Archivo CSV con códigos postales
    archivo_csv = "municipios_pedanias_codigos_postales_corregidos.csv"

    # Ejecutar búsqueda avanzada (limitando a 3 códigos postales para prueba)
    empresas = scraper.ejecutar_busqueda_avanzada(archivo_csv, max_codigos=3)

    # Guardar resultados
    scraper.guardar_resultados_avanzados()

    logging.info("Proceso completado!")

if __name__ == "__main__":
    main()
