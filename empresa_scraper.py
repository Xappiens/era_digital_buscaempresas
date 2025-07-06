import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import json
import os
from datetime import datetime

class EmpresaScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

        # Configurar Selenium
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument(f'--user-agent={self.ua.random}')

        self.empresas_encontradas = []

    def cargar_codigos_postales(self, archivo_csv):
        """Carga los códigos postales únicos del CSV"""
        try:
            df = pd.read_csv(archivo_csv)
            codigos_unicos = df['codigo_postal'].unique()
            print(f"Se cargaron {len(codigos_unicos)} códigos postales únicos")
            return codigos_unicos
        except Exception as e:
            print(f"Error al cargar el CSV: {e}")
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

    def buscar_en_google(self, codigo_postal, pagina=1):
        """Busca empresas en Google para un código postal específico"""
        from config import Config
        query = f"empresas código postal {codigo_postal} Murcia CIF"
        url = f"https://www.google.com/search?q={query}&start={(pagina-1)*10}"

        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                resultados = []

                # Buscar enlaces de resultados
                for resultado in soup.find_all('div', class_='g'):
                    titulo_elem = resultado.find('h3')
                    enlace_elem = resultado.find('a')
                    descripcion_elem = resultado.find('div', class_='VwiC3b')

                    if titulo_elem and enlace_elem:
                        titulo = titulo_elem.get_text()
                        enlace = enlace_elem.get('href')
                        descripcion = descripcion_elem.get_text() if descripcion_elem else ""

                        resultados.append({
                            'titulo': titulo,
                            'enlace': enlace,
                            'descripcion': descripcion
                        })

                return resultados
            else:
                print(f"Error en la búsqueda de Google: {response.status_code}")
                return []

        except Exception as e:
            print(f"Error al buscar en Google: {e}")
            return []

    def buscar_en_einforma(self, codigo_postal):
        """Busca empresas en eInforma"""
        try:
            url = f"https://www.einforma.com/buscar-empresas/codigo-postal-{codigo_postal}"
            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                empresas = []

                # Buscar empresas en los resultados
                for empresa in soup.find_all('div', class_='empresa-item'):
                    nombre = empresa.find('h3')
                    direccion = empresa.find('span', class_='direccion')
                    telefono = empresa.find('span', class_='telefono')

                    if nombre:
                        empresa_data = {
                            'razon_social': nombre.get_text().strip(),
                            'direccion': direccion.get_text().strip() if direccion else "",
                            'telefono': telefono.get_text().strip() if telefono else "",
                            'codigo_postal': codigo_postal,
                            'fuente': 'eInforma'
                        }

                        # Extraer CIF si está disponible
                        texto_completo = nombre.get_text() + " " + (direccion.get_text() if direccion else "")
                        cif = self.extraer_cif_de_texto(texto_completo)
                        if cif:
                            empresa_data['cif'] = cif

                        empresas.append(empresa_data)

                return empresas
            else:
                return []

        except Exception as e:
            print(f"Error al buscar en eInforma: {e}")
            return []

    def buscar_en_axesor(self, codigo_postal):
        """Busca empresas en Axesor"""
        try:
            url = f"https://www.axesor.es/empresas/codigo-postal/{codigo_postal}"
            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                empresas = []

                # Buscar empresas en los resultados
                for empresa in soup.find_all('div', class_='empresa'):
                    nombre = empresa.find('h2')
                    direccion = empresa.find('p', class_='direccion')
                    cnae = empresa.find('span', class_='cnae')

                    if nombre:
                        empresa_data = {
                            'razon_social': nombre.get_text().strip(),
                            'direccion': direccion.get_text().strip() if direccion else "",
                            'cnae': cnae.get_text().strip() if cnae else "",
                            'codigo_postal': codigo_postal,
                            'fuente': 'Axesor'
                        }

                        # Extraer CIF
                        texto_completo = nombre.get_text() + " " + (direccion.get_text() if direccion else "")
                        cif = self.extraer_cif_de_texto(texto_completo)
                        if cif:
                            empresa_data['cif'] = cif

                        empresas.append(empresa_data)

                return empresas
            else:
                return []

        except Exception as e:
            print(f"Error al buscar en Axesor: {e}")
            return []

    def extraer_datos_empresa(self, url, codigo_postal):
        """Extrae datos detallados de una empresa desde una URL"""
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Buscar información de contacto
                email = ""
                telefono = ""
                cnae = ""
                cif = ""

                # Buscar email
                from config import Config
                email_pattern = Config.PATRONES_EMAIL[0]
                emails = re.findall(email_pattern, response.text)
                if emails:
                    email = emails[0]

                # Buscar teléfono
                telefono_pattern = r'(\+34\s?)?[6-9]\d{8}'
                telefonos = re.findall(telefono_pattern, response.text)
                if telefonos:
                    telefono = telefonos[0]

                # Buscar CIF
                cif = self.extraer_cif_de_texto(response.text)

                # Buscar CNAE
                cnae_pattern = r'CNAE[:\s]*(\d{4})'
                cnae_match = re.search(cnae_pattern, response.text)
                if cnae_match:
                    cnae = cnae_match.group(1)

                return {
                    'email': email,
                    'telefono': telefono,
                    'cif': cif,
                    'cnae': cnae
                }
            else:
                return {'email': '', 'telefono': '', 'cif': '', 'cnae': ''}

        except Exception as e:
            print(f"Error al extraer datos de {url}: {e}")
            return {'email': '', 'telefono': '', 'cif': '', 'cnae': ''}

    def procesar_codigo_postal(self, codigo_postal, max_paginas=3):
        """Procesa un código postal completo"""
        print(f"\nProcesando código postal: {codigo_postal}")

        empresas_codigo = []

        # Buscar en Google
        for pagina in range(1, max_paginas + 1):
            print(f"  Buscando en Google página {pagina}...")
            resultados_google = self.buscar_en_google(codigo_postal, pagina)

            for resultado in resultados_google:
                # Extraer datos adicionales de la página
                datos_adicionales = self.extraer_datos_empresa(resultado['enlace'], codigo_postal)

                empresa = {
                    'razon_social': resultado['titulo'],
                    'direccion': resultado['descripcion'],
                    'codigo_postal': codigo_postal,
                    'email': datos_adicionales['email'],
                    'telefono': datos_adicionales['telefono'],
                    'cif': datos_adicionales['cif'],
                    'cnae': datos_adicionales['cnae'],
                    'fuente': 'Google',
                    'url': resultado['enlace']
                }

                empresas_codigo.append(empresa)

            # Pausa entre páginas
            time.sleep(random.uniform(2, 5))

        # Buscar en eInforma
        print(f"  Buscando en eInforma...")
        empresas_einforma = self.buscar_en_einforma(codigo_postal)
        empresas_codigo.extend(empresas_einforma)

        # Buscar en Axesor
        print(f"  Buscando en Axesor...")
        empresas_axesor = self.buscar_en_axesor(codigo_postal)
        empresas_codigo.extend(empresas_axesor)

        # Eliminar duplicados basándose en CIF
        empresas_unicas = self.eliminar_duplicados_por_cif(empresas_codigo)

        print(f"  Encontradas {len(empresas_unicas)} empresas únicas para el código postal {codigo_postal}")
        return empresas_unicas

    def eliminar_duplicados_por_cif(self, empresas):
        """Elimina empresas duplicadas basándose en CIF y nombre"""
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
                print(f"    ✅ Empresa agregada por CIF único: {cif} - {razon_social}")

            # Si no tiene CIF, usar nombre
            elif not cif and razon_social and razon_social not in nombres_vistos:
                nombres_vistos.add(razon_social)
                empresas_unicas.append(empresa)
                print(f"    ✅ Empresa agregada por nombre único: {razon_social}")

        print(f"    📊 Deduplicación: {len(empresas)} -> {len(empresas_unicas)} empresas únicas")
        return empresas_unicas

    def ejecutar_busqueda(self, archivo_csv, max_codigos=None):
        """Ejecuta la búsqueda completa"""
        print("Iniciando búsqueda de empresas...")

        # Cargar códigos postales
        codigos_postales = self.cargar_codigos_postales(archivo_csv)

        if max_codigos:
            codigos_postales = codigos_postales[:max_codigos]

        total_empresas = 0

        for i, codigo in enumerate(codigos_postales, 1):
            print(f"\nProgreso: {i}/{len(codigos_postales)}")

            empresas = self.procesar_codigo_postal(codigo)
            self.empresas_encontradas.extend(empresas)
            total_empresas += len(empresas)

            # Pausa entre códigos postales
            time.sleep(random.uniform(3, 7))

        print(f"\nBúsqueda completada. Total de empresas encontradas: {total_empresas}")
        return self.empresas_encontradas

    def guardar_resultados(self, archivo_salida="empresas_encontradas.xlsx"):
        """Guarda los resultados en un archivo Excel"""
        if not self.empresas_encontradas:
            print("No hay empresas para guardar")
            return

        df = pd.DataFrame(self.empresas_encontradas)

        # Reorganizar columnas incluyendo CIF
        columnas_orden = ['razon_social', 'cif', 'direccion', 'codigo_postal', 'cnae', 'email', 'telefono', 'fuente', 'url']
        df = df.reindex(columns=columnas_orden)

        # Guardar en Excel
        df.to_excel(archivo_salida, index=False)
        print(f"Resultados guardados en: {archivo_salida}")

        # También guardar en CSV
        archivo_csv = archivo_salida.replace('.xlsx', '.csv')
        df.to_csv(archivo_csv, index=False, encoding='utf-8')
        print(f"Resultados también guardados en: {archivo_csv}")

        # Mostrar estadísticas
        self.mostrar_estadisticas(df)

    def mostrar_estadisticas(self, df):
        """Muestra estadísticas de los resultados"""
        print("\n📊 ESTADÍSTICAS DE LA BÚSQUEDA:")
        print(f"   - Total empresas: {len(df)}")
        print(f"   - Empresas con CIF: {len(df[df['cif'].notna() & (df['cif'] != '')])}")
        print(f"   - Empresas con email: {len(df[df['email'].notna() & (df['email'] != '')])}")
        print(f"   - Empresas con teléfono: {len(df[df['telefono'].notna() & (df['telefono'] != '')])}")
        print(f"   - Empresas con CNAE: {len(df[df['cnae'].notna() & (df['cnae'] != '')])}")

        if 'fuente' in df.columns:
            print(f"\n📋 DISTRIBUCIÓN POR FUENTES:")
            fuentes = df['fuente'].value_counts()
            for fuente, cantidad in fuentes.items():
                print(f"   - {fuente}: {cantidad}")

def main():
    # Crear instancia del scraper
    scraper = EmpresaScraper()

    # Archivo CSV con códigos postales
    archivo_csv = "municipios_pedanias_codigos_postales_corregidos.csv"

    # Ejecutar búsqueda (limitando a 5 códigos postales para prueba)
    empresas = scraper.ejecutar_busqueda(archivo_csv, max_codigos=5)

    # Guardar resultados
    scraper.guardar_resultados()

    print("\nProceso completado!")

if __name__ == "__main__":
    main()
