#!/usr/bin/env python3
"""
Scraper específico para Axesor - Directorio de empresas de Murcia
Busca empresas por municipios en https://www.axesor.es/directorio-informacion-empresas/empresas-de-Murcia
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import re
import logging
from datetime import datetime
import os
from urllib.parse import urljoin, quote

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_axesor.log'),
        logging.StreamHandler()
    ]
)

class ScraperAxesor:
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
        self.base_url = "https://www.axesor.es"

    def cargar_municipios_murcia(self, archivo_csv):
        """Carga los municipios únicos de Murcia del CSV"""
        try:
            df = pd.read_csv(archivo_csv)
            # Filtrar solo municipios de Murcia (códigos postales que empiecen por 30)
            df_murcia = df[df['codigo_postal'].astype(str).str.startswith('30')]
            municipios_unicos = df_murcia['municipio'].unique()
            logging.info(f"Se cargaron {len(municipios_unicos)} municipios únicos de Murcia")
            return municipios_unicos
        except Exception as e:
            logging.error(f"Error al cargar el CSV: {e}")
            return []

    def obtener_enlaces_municipios(self):
        """Extrae los enlaces de municipios desde la página principal de Axesor Murcia"""
        url = f"{self.base_url}/directorio-informacion-empresas/empresas-de-Murcia"
        try:
            response = self.session.get(url, timeout=20)
            if response.status_code != 200:
                logging.error(f"No se pudo acceder a la página principal de Axesor ({url})")
                return {}
            soup = BeautifulSoup(response.content, 'html.parser')
            enlaces = {}
            for a in soup.find_all('a', href=True):
                href = a['href']
                texto = a.get_text(strip=True)
                # Enlaces con formato: //www.axesor.es/directorio-informacion-empresas/empresas-de-Murcia/informacion-empresas-de-[Municipio]/1
                if 'informacion-empresas-de-' in href and texto:
                    municipio = texto
                    # Convertir enlace relativo a absoluto
                    if href.startswith('//'):
                        url_completa = 'https:' + href
                    else:
                        url_completa = urljoin(self.base_url, href)
                    enlaces[municipio.lower()] = url_completa
            logging.info(f"Extraídos {len(enlaces)} enlaces de municipios de Axesor")
            return enlaces
        except Exception as e:
            logging.error(f"Error extrayendo enlaces de municipios: {e}")
            return {}

    def buscar_municipio_axesor(self, municipio, max_paginas=10):
        """Busca empresas de un municipio específico en Axesor"""
        empresas = []

        # URL base para buscar empresas por municipio
        municipio_encoded = quote(municipio.lower().replace(' ', '-'))
        url_base = f"{self.base_url}/directorio-informacion-empresas/empresas-de-{municipio_encoded}"

        logging.info(f"Buscando empresas en {municipio}...")

        for pagina in range(1, max_paginas + 1):
            try:
                if pagina == 1:
                    url = url_base
                else:
                    url = f"{url_base}?page={pagina}"

                logging.info(f"  Página {pagina}: {url}")

                response = self.session.get(url, timeout=20)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Buscar empresas en la página
                    empresas_pagina = self.extraer_empresas_pagina(soup, municipio)

                    if empresas_pagina:
                        empresas.extend(empresas_pagina)
                        logging.info(f"    Encontradas {len(empresas_pagina)} empresas en página {pagina}")
                    else:
                        logging.info(f"    No se encontraron más empresas en página {pagina}")
                        break

                else:
                    logging.warning(f"    Error HTTP {response.status_code} en página {pagina}")
                    break

                # Pausa entre páginas
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                logging.error(f"    Error al procesar página {pagina}: {e}")
                break

        logging.info(f"  Total empresas encontradas en {municipio}: {len(empresas)}")
        return empresas

    def extraer_empresas_pagina(self, soup, municipio):
        """Extrae empresas de una página de resultados de Axesor"""
        empresas = []

        # Buscar en tabla de empresas (formato más común en Axesor)
        tabla_empresas = soup.find('table')
        if tabla_empresas:
            filas = tabla_empresas.find_all('tr')
            for fila in filas[1:]:  # Saltar la primera fila (encabezados)
                try:
                    empresa_data = self.extraer_datos_empresa_tabla(fila, municipio)
                    if empresa_data:
                        empresas.append(empresa_data)
                except Exception as e:
                    logging.error(f"Error al extraer datos de empresa de tabla: {e}")
                    continue

        # Si no hay tabla, buscar en otros contenedores
        if not empresas:
            contenedores_empresas = soup.find_all(['div', 'article', 'li'], class_=[
                'empresa-item', 'company-item', 'result-item', 'business-item',
                'empresa', 'company', 'result', 'business'
            ])

            if not contenedores_empresas:
                contenedores_empresas = soup.find_all(['div', 'article'], class_=re.compile(r'.*empresa.*|.*company.*|.*result.*'))

            for contenedor in contenedores_empresas:
                try:
                    empresa_data = self.extraer_datos_empresa(contenedor, municipio)
                    if empresa_data:
                        empresas.append(empresa_data)
                except Exception as e:
                    logging.error(f"Error al extraer datos de empresa: {e}")
                    continue

        logging.info(f"    Extraídas {len(empresas)} empresas de la página")
        return empresas

    def extraer_datos_empresa_tabla(self, fila, municipio):
        """Extrae datos básicos de empresa desde una fila de tabla"""
        try:
            celdas = fila.find_all('td')
            if len(celdas) < 1:
                return None

            # Buscar nombre en la primera celda
            nombre_celda = celdas[0]
            nombre_elem = nombre_celda.find('a') or nombre_celda
            nombre = nombre_elem.get_text(strip=True)
            if not nombre:
                return None

            # Datos básicos
            empresa_data = {
                'razon_social': nombre,
                'municipio': municipio,
                'fuente': 'Axesor'
            }

            # Buscar enlace a detalles
            enlace_elem = nombre_celda.find('a', href=True)
            if enlace_elem:
                href = enlace_elem['href']
                if href.startswith('//'):
                    enlace_detalles = 'https:' + href
                else:
                    enlace_detalles = urljoin(self.base_url, href)
                empresa_data['url_detalles'] = enlace_detalles

            return empresa_data
        except Exception as e:
            logging.error(f"Error al extraer datos de empresa de tabla: {e}")
            return None

    def extraer_datos_empresa(self, contenedor, municipio):
        """Extrae datos básicos de una empresa"""
        try:
            # Buscar nombre de la empresa
            nombre_elem = contenedor.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'.*nombre.*|.*name.*|.*title.*'))
            if not nombre_elem:
                nombre_elem = contenedor.find(['h2', 'h3', 'h4', 'a'])

            if not nombre_elem:
                return None

            nombre = nombre_elem.get_text().strip()
            if not nombre:
                return None

            # Buscar enlace a página de detalles
            enlace_elem = contenedor.find('a', href=True)
            enlace_detalles = None
            if enlace_elem:
                enlace_detalles = urljoin(self.base_url, enlace_elem['href'])

            # Solo datos básicos
            empresa_data = {
                'razon_social': nombre,
                'municipio': municipio,
                'fuente': 'Axesor',
                'url_detalles': enlace_detalles
            }

            return empresa_data

        except Exception as e:
            logging.error(f"Error al extraer datos de empresa: {e}")
            return None

    def obtener_datos_detallados(self, url):
        """Obtiene datos detallados de la página de la empresa"""
        try:
            response = self.session.get(url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                datos = {}

                # Buscar CIF
                cif = self.extraer_cif_de_texto(response.text)
                if cif:
                    datos['cif'] = cif

                # Buscar CNAE
                cnae = self.extraer_cnae_de_texto(response.text)
                if cnae:
                    datos['cnae'] = cnae

                # Buscar código postal
                codigo_postal = self.extraer_codigo_postal_de_texto(response.text)
                if codigo_postal:
                    datos['codigo_postal'] = codigo_postal

                # Buscar dirección más detallada
                direccion_elem = soup.find(['span', 'p', 'div'], class_=re.compile(r'.*direccion.*|.*address.*'))
                if direccion_elem:
                    datos['direccion_completa'] = direccion_elem.get_text().strip()

                # Buscar actividad económica
                actividad_elem = soup.find(['span', 'p', 'div'], class_=re.compile(r'.*actividad.*|.*activity.*|.*sector.*'))
                if actividad_elem:
                    datos['actividad'] = actividad_elem.get_text().strip()

                return datos

        except Exception as e:
            logging.error(f"Error al obtener datos detallados de {url}: {e}")

        return None

    def extraer_cif_de_texto(self, texto):
        """Extrae CIF del texto usando patrones regex"""
        patrones_cif = [
            r'\b[A-Z]\d{8}\b',
            r'\b[A-Z]\d{7}[A-Z]\b',
            r'CIF[:\s]*([A-Z]\d{7,8}[A-Z]?)',
            r'Código[:\s]*([A-Z]\d{7,8}[A-Z]?)',
            r'Fiscal[:\s]*([A-Z]\d{7,8}[A-Z]?)'
        ]

        for patron in patrones_cif:
            matches = re.findall(patron, texto, re.IGNORECASE)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        cif = match[0]
                    else:
                        cif = match

                    if self.validar_cif(cif):
                        return cif.upper()

        return None

    def extraer_cnae_de_texto(self, texto):
        """Extrae CNAE del texto"""
        patrones_cnae = [
            r'CNAE[:\s]*(\d{4})',
            r'Actividad[:\s]*(\d{4})',
            r'Código[:\s]*(\d{4})'
        ]

        for patron in patrones_cnae:
            matches = re.findall(patron, texto, re.IGNORECASE)
            if matches:
                return matches[0]

        return None

    def extraer_codigo_postal_de_texto(self, texto):
        """Extrae código postal del texto"""
        patrones_cp = [
            r'\b30\d{3}\b',  # Códigos postales de Murcia
            r'CP[:\s]*(\d{5})',
            r'Código Postal[:\s]*(\d{5})'
        ]

        for patron in patrones_cp:
            matches = re.findall(patron, texto)
            if matches:
                return matches[0]

        return None

    def validar_cif(self, cif):
        """Valida si un CIF tiene el formato correcto"""
        if not cif:
            return False

        cif_limpio = cif.strip().upper()
        return bool(re.match(r'^[A-Z]\d{7,8}[A-Z]?$', cif_limpio))

    def eliminar_duplicados(self, empresas):
        """Elimina empresas duplicadas basándose solo en razón social"""
        if not empresas:
            return []

        df = pd.DataFrame(empresas)

        # Eliminar duplicados por razón social
        df = df.drop_duplicates(subset=['razon_social'], keep='first')

        return df.to_dict('records')

    def ejecutar_busqueda_axesor(self, archivo_csv, max_municipios=1000, max_paginas=100):
        """Ejecuta la búsqueda para todos los municipios del CSV que tengan enlace en Axesor"""
        logging.info("Iniciando búsqueda en Axesor...")
        municipios = self.cargar_municipios_murcia(archivo_csv)
        if len(municipios) == 0:
            logging.error("No se pudieron cargar municipios")
            return []

        # Obtener enlaces de municipios desde la web
        enlaces_municipios = self.obtener_enlaces_municipios()
        if not enlaces_municipios:
            logging.error("No se pudieron extraer enlaces de municipios de Axesor")
            return []

        municipios_procesados = 0
        municipios_con_enlace = []
        municipios_sin_enlace = []

        # Procesar todos los municipios del CSV que tengan enlace
        for municipio in municipios:
            nombre_busqueda = municipio.lower()
            enlace_encontrado = False

            # Buscar coincidencia exacta primero
            if nombre_busqueda in enlaces_municipios:
                url_municipio = enlaces_municipios[nombre_busqueda]
                logging.info(f"Procesando municipio: {municipio} -> {url_municipio}")
                empresas = self.buscar_municipio_axesor_por_url(municipio, url_municipio, max_paginas)
                self.empresas_encontradas.extend(empresas)
                municipios_procesados += 1
                municipios_con_enlace.append(municipio)
                enlace_encontrado = True
            else:
                # Buscar coincidencia flexible (sin tildes, espacios, etc.)
                for nombre_axesor, url_axesor in enlaces_municipios.items():
                    if self.nombres_coinciden(municipio, nombre_axesor):
                        logging.info(f"Procesando municipio: {municipio} (coincide con {nombre_axesor}) -> {url_axesor}")
                        empresas = self.buscar_municipio_axesor_por_url(municipio, url_axesor, max_paginas)
                        self.empresas_encontradas.extend(empresas)
                        municipios_procesados += 1
                        municipios_con_enlace.append(municipio)
                        enlace_encontrado = True
                        break

            if not enlace_encontrado:
                municipios_sin_enlace.append(municipio)
                logging.warning(f"No se encontró enlace para municipio: {municipio}")

        # Mostrar resumen de municipios procesados
        logging.info(f"Municipios procesados: {municipios_procesados}")
        logging.info(f"Municipios con enlace: {municipios_con_enlace}")
        logging.info(f"Municipios sin enlace: {municipios_sin_enlace}")

        # Eliminar duplicados
        logging.info("Eliminando duplicados...")
        empresas_unicas = self.eliminar_duplicados(self.empresas_encontradas)
        logging.info(f"Búsqueda completada. Total de empresas únicas: {len(empresas_unicas)}")
        return empresas_unicas

    def nombres_coinciden(self, nombre1, nombre2):
        """Compara dos nombres de municipios de forma flexible"""
        # Normalizar nombres (quitar tildes, espacios, guiones, etc.)
        def normalizar(nombre):
            import unicodedata
            # Quitar tildes
            nombre = unicodedata.normalize('NFD', nombre).encode('ascii', 'ignore').decode('utf-8')
            # Convertir a minúsculas y quitar espacios extra
            nombre = nombre.lower().strip()
            # Quitar caracteres especiales
            nombre = nombre.replace('-', ' ').replace('_', ' ')
            # Quitar espacios múltiples
            nombre = ' '.join(nombre.split())
            return nombre

        return normalizar(nombre1) == normalizar(nombre2)

    def buscar_municipio_axesor_por_url(self, municipio, url_base, max_paginas=100):
        """Busca empresas de un municipio específico en Axesor usando el enlace real y paginación dinámica"""
        empresas = []
        pagina_url = url_base
        pagina_num = 1
        while pagina_url and pagina_num <= max_paginas:
            try:
                logging.info(f"  Página {pagina_num}: {pagina_url}")
                response = self.session.get(pagina_url, timeout=20)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    empresas_pagina = self.extraer_empresas_pagina(soup, municipio)
                    if empresas_pagina:
                        empresas.extend(empresas_pagina)
                        logging.info(f"    Encontradas {len(empresas_pagina)} empresas en página {pagina_num}")
                    else:
                        logging.info(f"    No se encontraron más empresas en página {pagina_num}")
                        break
                    # Buscar botón siguiente con múltiples selectores
                    next_btn = None
                    selectores_next = [
                        'a[class*="next"][rel="next"]',
                        'a[class*="next"]',
                        'a[rel="next"]',
                        'a[title*="siguiente"]',
                        'a[title*="next"]',
                        'a.next',
                        'a.icomoon[rel="next"]',
                        'a.next.icomoon[rel="next"]',
                        f'a[href*="/{pagina_num + 1}"]',
                        f'a[href*="page={pagina_num + 1}"]'
                    ]
                    enlaces_paginacion = soup.find_all('a', href=True)
                    enlaces_paginacion_texto = []
                    for enlace in enlaces_paginacion:
                        href = enlace.get('href', '')
                        texto = enlace.get_text(strip=True)
                        if any(palabra in href.lower() for palabra in ['page', str(pagina_num + 1), 'siguiente', 'next']):
                            enlaces_paginacion_texto.append(f"{texto}: {href}")
                    if enlaces_paginacion_texto:
                        logging.info(f"    Enlaces de paginación encontrados: {enlaces_paginacion_texto[:5]}")
                    for selector in selectores_next:
                        next_btn = soup.select_one(selector)
                        if next_btn and next_btn.get('href'):
                            break
                    if next_btn and next_btn.get('href'):
                        href = next_btn['href']
                        logging.info(f"    Botón siguiente encontrado: {href}")
                        if href.startswith('//'):
                            pagina_url = 'https:' + href
                        else:
                            pagina_url = urljoin(self.base_url, href)
                        pagina_num += 1
                        time.sleep(random.uniform(2, 4))
                        continue  # <-- Asegura que el bucle continúe tras encontrar el botón
                    else:
                        # Intentar construir la URL de la siguiente página manualmente
                        siguiente_url = None
                        if f'/{pagina_num}' in pagina_url:
                            siguiente_url = pagina_url.replace(f'/{pagina_num}', f'/{pagina_num + 1}')
                        elif '/1' in pagina_url:
                            siguiente_url = pagina_url.replace('/1', f'/{pagina_num + 1}')
                        if siguiente_url:
                            logging.info(f"    Intentando URL manual: {siguiente_url}")
                            try:
                                test_response = self.session.get(siguiente_url, timeout=10)
                                if test_response.status_code == 200:
                                    pagina_url = siguiente_url
                                    pagina_num += 1
                                    time.sleep(random.uniform(2, 4))
                                    continue  # <-- Asegura que el bucle continúe tras construir la URL
                            except:
                                pass
                        logging.info(f"    No se encontró botón siguiente en página {pagina_num}")
                        break
                else:
                    logging.warning(f"    Error HTTP {response.status_code} en página {pagina_num}")
                    break
            except Exception as e:
                logging.error(f"    Error al procesar página {pagina_num}: {e}")
                break
        logging.info(f"  Total empresas encontradas en {municipio}: {len(empresas)}")
        return empresas

    def guardar_resultados(self, empresas, archivo_salida=None):
        """Guarda los resultados en Excel y CSV"""
        if not empresas:
            logging.warning("No hay empresas para guardar")
            return

        if not archivo_salida:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archivo_salida = f"empresas_axesor_{timestamp}"

        # Crear DataFrame
        df = pd.DataFrame(empresas)

        # Guardar Excel
        archivo_excel = f"{archivo_salida}.xlsx"
        df.to_excel(archivo_excel, index=False, engine='openpyxl')
        logging.info(f"Resultados guardados en Excel: {archivo_excel}")

        # Guardar CSV
        archivo_csv = f"{archivo_salida}.csv"
        df.to_csv(archivo_csv, index=False, encoding='utf-8')
        logging.info(f"Resultados guardados en CSV: {archivo_csv}")

        # Mostrar estadísticas
        self.mostrar_estadisticas(df)

    def mostrar_estadisticas(self, df):
        """Muestra estadísticas de los resultados"""
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS DE RESULTADOS")
        print("="*60)

        print(f"Total de empresas: {len(df)}")

        if 'municipio' in df.columns:
            municipios_unicos = df['municipio'].nunique()
            print(f"Municipios cubiertos: {municipios_unicos}")

        if 'url_detalles' in df.columns:
            empresas_con_enlace = df['url_detalles'].notna().sum()
            print(f"Empresas con enlace a detalles: {empresas_con_enlace}")

        print("="*60)

def main():
    """Función principal"""
    scraper = ScraperAxesor()

    # Ejecutar búsqueda para TODOS los municipios del CSV que tengan enlace en Axesor
    empresas = scraper.ejecutar_busqueda_axesor(
        "municipios_pedanias_codigos_postales_corregidos.csv",
        max_municipios=1000,  # Sin límite realista de municipios
        max_paginas=100       # Sin límite realista de páginas por municipio
    )

    # Guardar resultados
    scraper.guardar_resultados(empresas)

if __name__ == "__main__":
    main()
