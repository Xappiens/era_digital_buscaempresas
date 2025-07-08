import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import logging
import re
from urllib.parse import urljoin
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_detalles.log'),
        logging.StreamHandler()
    ]
)

class ScraperDetallesEmpresas:
    def __init__(self):
        """Inicializa el scraper"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # Cargar códigos postales
        self.codigos_postales = self.cargar_codigos_postales()

    def cargar_codigos_postales(self):
        """Carga los códigos postales desde el archivo CSV"""
        try:
            df_cp = pd.read_csv('municipios_pedanias_codigos_postales_corregidos.csv')
            # Crear diccionario municipio -> código postal principal
            codigos = {}
            for _, row in df_cp.iterrows():
                municipio = row['municipio'].strip()
                cp = str(row['codigo_postal']).split('.')[0]  # Eliminar decimales
                if municipio not in codigos:
                    codigos[municipio] = cp
            return codigos
        except Exception as e:
            logging.error(f"Error cargando códigos postales: {e}")
            return {}

    def obtener_codigo_postal(self, municipio):
        """Obtiene el código postal para un municipio"""
        municipio_limpio = municipio.strip()
        return self.codigos_postales.get(municipio_limpio, '')

    def cargar_empresas(self, archivo_csv):
        """Carga las empresas desde el archivo CSV generado por el scraper anterior"""
        try:
            df = pd.read_csv(archivo_csv)
            logging.info(f"Cargadas {len(df)} empresas desde {archivo_csv}")
            return df
        except Exception as e:
            logging.error(f"Error cargando archivo CSV: {e}")
            return None

    def extraer_direccion_y_codigo_postal(self, soup):
        """Extrae la dirección y código postal de la empresa"""
        try:
            direccion = None
            codigo_postal = None

            # Buscar en JSON-LD
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'address' in data:
                        address = data['address']
                        if isinstance(address, dict):
                            if 'streetAddress' in address:
                                direccion = address['streetAddress']
                            if 'postalCode' in address:
                                codigo_postal = address['postalCode']
                except:
                    continue

            # Si no se encontró en JSON-LD, buscar en texto
            if not direccion:
                texto_completo = soup.get_text()
                # Buscar dirección en formato: CALLE, NUMERO, CODIGO_POSTAL, CIUDAD
                direccion_match = re.search(r'([A-Z\s\.]+)\s*(\d{5})\s*,\s*([A-Z\s]+)', texto_completo)
                if direccion_match:
                    direccion = direccion_match.group(1).strip()
                    codigo_postal = direccion_match.group(2)

            return direccion, codigo_postal
        except Exception as e:
            logging.error(f"Error extrayendo dirección: {e}")
            return None, None

    def extraer_telefono(self, soup):
        """Extrae el teléfono de la empresa"""
        try:
            # Buscar en JSON-LD
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'telephone' in data:
                        return data['telephone']
                except:
                    continue

            # Buscar por patrón de teléfono en texto
            texto_completo = soup.get_text()
            telefono_match = re.search(r'\b\d{9}\b', texto_completo)
            if telefono_match:
                return telefono_match.group()

            return None
        except Exception as e:
            logging.error(f"Error extrayendo teléfono: {e}")
            return None

    def extraer_cif(self, soup):
        """Extrae el CIF de la empresa"""
        try:
            # Buscar en JSON-LD
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'taxID' in data:
                        return data['taxID']
                except:
                    continue

            # Buscar por patrón CIF en texto
            texto_completo = soup.get_text()
            cif_match = re.search(r'[A-Z]\d{8}', texto_completo)
            if cif_match:
                return cif_match.group()

            return None
        except Exception as e:
            logging.error(f"Error extrayendo CIF: {e}")
            return None

    def extraer_sitio_web(self, soup):
        """Extrae el sitio web de la empresa"""
        try:
            # Lista de dominios a excluir (servicios externos, redes sociales, etc.)
            dominios_excluidos = [
                'axesor.es', 'experian.es', 'google', 'linkedin.com', 'twitter.com',
                'facebook.com', 'instagram.com', 'youtube.com', 'confianzaonline.es',
                'maps.google', 'share', 'via=axesor'
            ]

            # 1. Buscar en la tabla de la ficha (td tras 'Web:' o 'Sitio web:')
            elementos = soup.find_all('td', string=re.compile(r'Web:|Sitio web:', re.IGNORECASE))
            for elemento in elementos:
                siguiente_td = elemento.find_next_sibling('td')
                if siguiente_td:
                    enlace = siguiente_td.find('a', href=True)
                    if enlace and enlace['href'].startswith('http'):
                        url = enlace['href']
                        # Filtrar URLs que no sean de servicios externos
                        if not any(dominio in url.lower() for dominio in dominios_excluidos):
                            return url
                    # Si no es enlace, devolver el texto si parece una URL
                    web = siguiente_td.get_text(strip=True)
                    if web and (web.startswith('http') or web.startswith('www.')):
                        # Filtrar URLs que no sean de servicios externos
                        if not any(dominio in web.lower() for dominio in dominios_excluidos):
                            return web

            # 2. Buscar en JSON-LD (solo si no es de servicios externos)
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'url' in data:
                        url = data['url']
                        # Filtrar URLs que sean de la empresa, no de servicios externos
                        if url and not any(dominio in url.lower() for dominio in dominios_excluidos):
                            return url
                except:
                    continue

            # 3. Buscar enlaces externos (que no sean de servicios externos)
            enlaces = soup.find_all('a', href=True)
            for enlace in enlaces:
                href = enlace['href']
                if href.startswith('http') and not any(dominio in href.lower() for dominio in dominios_excluidos):
                    return href

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
            # Buscar en JSON-LD
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'foundingDate' in data:
                        return data['foundingDate']
                except:
                    continue

            # Buscar en texto por patrón de fecha
            texto_completo = soup.get_text()
            fecha_match = re.search(r'constitución.*?(\d{2}/\d{2}/\d{4})', texto_completo, re.IGNORECASE)
            if fecha_match:
                return fecha_match.group(1)

            return None
        except Exception as e:
            logging.error(f"Error extrayendo fecha de constitución: {e}")
            return None

    def extraer_cnae(self, soup):
        """Extrae el CNAE de la empresa"""
        try:
            # Buscar en JSON-LD
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'isicV4' in data:
                        return data['isicV4']
                except:
                    continue

            # Buscar por patrón CNAE en texto
            texto_completo = soup.get_text()
            cnae_match = re.search(r'CNAE.*?(\d{4})', texto_completo, re.IGNORECASE)
            if cnae_match:
                return cnae_match.group(1)

            return None
        except Exception as e:
            logging.error(f"Error extrayendo CNAE: {e}")
            return None

    def extraer_objeto_social(self, soup):
        """Extrae el objeto social de la empresa con múltiples selectores"""
        try:
            # Buscar en JSON-LD
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'description' in data:
                        return data['description']
                except:
                    continue

            # Buscar por texto que contenga "Objeto social:"
            elementos = soup.find_all('td', string=re.compile(r'Objeto social:', re.IGNORECASE))
            for elemento in elementos:
                siguiente_td = elemento.find_next_sibling('td')
                if siguiente_td:
                    objeto = siguiente_td.get_text(strip=True)
                    if objeto and len(objeto) > 5:
                        return objeto

            # Buscar por texto que contenga "Objeto:"
            elementos = soup.find_all('td', string=re.compile(r'Objeto:', re.IGNORECASE))
            for elemento in elementos:
                siguiente_td = elemento.find_next_sibling('td')
                if siguiente_td:
                    objeto = siguiente_td.get_text(strip=True)
                    if objeto and len(objeto) > 5:
                        return objeto

            # Buscar por texto que contenga "Actividad:"
            elementos = soup.find_all('td', string=re.compile(r'Actividad:', re.IGNORECASE))
            for elemento in elementos:
                siguiente_td = elemento.find_next_sibling('td')
                if siguiente_td:
                    objeto = siguiente_td.get_text(strip=True)
                    if objeto and len(objeto) > 5:
                        return objeto

            # Buscar en cualquier td que contenga texto largo que parezca objeto social
            tds = soup.find_all('td')
            for td in tds:
                texto = td.get_text(strip=True)
                if texto and len(texto) > 50 and any(palabra in texto.lower() for palabra in ['objeto', 'actividad', 'comercializacion', 'produccion', 'servicios']):
                    return texto

            return None
        except Exception as e:
            logging.error(f"Error extrayendo objeto social: {e}")
            return None

    def extraer_detalles_empresa(self, url):
        """Extrae todos los detalles de una empresa desde su página"""
        try:
            logging.info(f"Procesando: {url}")

            # Hacer pausa aleatoria para no sobrecargar el servidor
            time.sleep(random.uniform(2, 4))

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Debug: mostrar estructura de la página
            logging.debug(f"Título de la página: {soup.title.string if soup.title else 'Sin título'}")

            # Extraer dirección y código postal
            direccion, codigo_postal = self.extraer_direccion_y_codigo_postal(soup)
            logging.debug(f"Dirección extraída: {direccion}")

            # Extraer teléfono
            telefono = self.extraer_telefono(soup)
            logging.debug(f"Teléfono extraído: {telefono}")

            # Extraer CIF
            cif = self.extraer_cif(soup)
            logging.debug(f"CIF extraído: {cif}")

            # Extraer sitio web
            sitio_web = self.extraer_sitio_web(soup)
            logging.debug(f"Sitio web extraído: {sitio_web}")

            # Extraer email
            email = self.extraer_email(soup)
            logging.debug(f"Email extraído: {email}")

            # Extraer fecha de constitución
            fecha_constitucion = self.extraer_fecha_constitucion(soup)
            logging.debug(f"Fecha de constitución extraída: {fecha_constitucion}")

            # Extraer CNAE
            cnae = self.extraer_cnae(soup)
            logging.debug(f"CNAE extraído: {cnae}")

            # Extraer objeto social
            objeto_social = self.extraer_objeto_social(soup)
            logging.debug(f"Objeto social extraído: {objeto_social[:100] if objeto_social else 'None'}...")

            detalles = {
                'direccion': direccion,
                'codigo_postal': codigo_postal,
                'telefono': telefono,
                'cif': cif,
                'sitio_web': sitio_web,
                'email': email,
                'fecha_constitucion': fecha_constitucion,
                'cnae': cnae,
                'objeto_social': objeto_social
            }

            # Contar campos extraídos exitosamente
            campos_extraidos = sum(1 for valor in detalles.values() if valor is not None)
            logging.info(f"  Extraídos {campos_extraidos}/8 campos")

            return detalles

        except Exception as e:
            logging.error(f"Error procesando {url}: {e}")
            return None

    def procesar_empresas(self, archivo_csv, max_empresas=10):
        """Procesa las empresas y extrae sus detalles"""
        logging.info(f"Iniciando extracción de detalles para máximo {max_empresas} empresas")

        # Cargar empresas
        df_empresas = self.cargar_empresas(archivo_csv)
        if df_empresas is None:
            return None

        # Limitar a las primeras empresas
        df_empresas = df_empresas.head(max_empresas)

        resultados = []

        for index, row in df_empresas.iterrows():
            # Obtener código postal del archivo de códigos postales
            municipio = row['municipio']
            codigo_postal = self.obtener_codigo_postal(municipio)

            empresa = {
                'razon_social': row['razon_social'],
                'municipio': municipio,
                'codigo_postal': codigo_postal,
                'url_detalles': row['url_detalles']
            }

            # Extraer detalles si hay enlace
            if pd.notna(row['url_detalles']) and row['url_detalles']:
                detalles = self.extraer_detalles_empresa(row['url_detalles'])
                if detalles:
                    # Asegurar que no hay decimales en CNAE y teléfono
                    if 'cnae' in detalles and detalles['cnae']:
                        detalles['cnae'] = str(detalles['cnae']).split('.')[0]
                    if 'telefono' in detalles and detalles['telefono']:
                        detalles['telefono'] = str(detalles['telefono']).split('.')[0]
                    # Usar el código postal del archivo de códigos postales
                    detalles['codigo_postal'] = codigo_postal
                    empresa.update(detalles)

            resultados.append(empresa)
            logging.info(f"Procesada empresa {index + 1}/{len(df_empresas)}: {empresa['razon_social']}")

        return resultados

    def guardar_resultados(self, empresas, prefijo="detalles_empresas"):
        """Guarda los resultados en Excel y CSV con formato correcto"""
        if not empresas:
            logging.error("No hay empresas para guardar")
            return

        df = pd.DataFrame(empresas)

        # Asegurar que teléfono y CNAE se guarden como texto sin decimales
        if 'telefono' in df.columns:
            df.loc[:, 'telefono'] = df['telefono'].astype(str).str.split('.').str[0]
        if 'cnae' in df.columns:
            df.loc[:, 'cnae'] = df['cnae'].astype(str).str.split('.').str[0]

        # Generar timestamp
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")

        # Guardar Excel
        archivo_excel = f"{prefijo}_{timestamp}.xlsx"
        df.to_excel(archivo_excel, index=False)
        logging.info(f"Resultados guardados en Excel: {archivo_excel}")

        # Guardar CSV
        archivo_csv = f"{prefijo}_{timestamp}.csv"
        df.to_csv(archivo_csv, index=False)
        logging.info(f"Resultados guardados en CSV: {archivo_csv}")

        # Mostrar estadísticas
        self.mostrar_estadisticas(df)

        return archivo_excel, archivo_csv

    def mostrar_estadisticas(self, df):
        """Muestra estadísticas de los resultados"""
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS DE DETALLES EXTRAÍDOS")
        print("="*60)

        print(f"Total de empresas procesadas: {len(df)}")

        campos = ['direccion', 'codigo_postal', 'telefono', 'cif', 'sitio_web', 'email', 'fecha_constitucion', 'cnae', 'objeto_social']

        for campo in campos:
            if campo in df.columns:
                empresas_con_campo = df[campo].notna().sum()
                porcentaje = (empresas_con_campo / len(df)) * 100
                print(f"Empresas con {campo}: {empresas_con_campo} ({porcentaje:.1f}%)")

        print("="*60)

def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(description='Scraper de detalles de empresas de Axesor')
    parser.add_argument('--test-url', type=str, help='URL específica para probar el scraper')
    parser.add_argument('--max-empresas', type=int, default=10, help='Número máximo de empresas a procesar')
    parser.add_argument('--archivo-csv', type=str, default="empresas_axesor_20250706_221604.csv", help='Archivo CSV con las empresas')

    args = parser.parse_args()

    scraper = ScraperDetallesEmpresas()

    if args.test_url:
        # Procesar URL específica de prueba
        logging.info(f"Procesando URL de prueba: {args.test_url}")

        # Buscar la empresa en el archivo CSV para obtener el municipio correcto
        df_empresas = scraper.cargar_empresas(args.archivo_csv)
        empresa_encontrada = None

        if df_empresas is not None:
            # Buscar por URL
            empresa_encontrada = df_empresas[df_empresas['url_detalles'] == args.test_url]
            if len(empresa_encontrada) == 0:
                # Si no se encuentra por URL exacta, buscar por nombre de empresa
                nombre_empresa = args.test_url.split('/')[-1].replace('.html', '').replace('_', ' ')
                empresa_encontrada = df_empresas[df_empresas['razon_social'].str.contains(nombre_empresa, case=False, na=False)]

        if empresa_encontrada is not None and len(empresa_encontrada) > 0:
            row = empresa_encontrada.iloc[0]
            nombre_empresa = row['razon_social']
            municipio = row['municipio']
        else:
            # Si no se encuentra, usar valores por defecto
            nombre_empresa = args.test_url.split('/')[-1].replace('.html', '').replace('_', ' ')
            municipio = 'Desconocido'

        empresa_prueba = {
            'razon_social': nombre_empresa,
            'municipio': municipio,
            'url_detalles': args.test_url
        }

        detalles = scraper.extraer_detalles_empresa(args.test_url)
        if detalles:
            empresa_prueba.update(detalles)

        # Guardar resultado
        scraper.guardar_resultados([empresa_prueba], "prueba_empresa")

        # Mostrar resultado detallado
        print("\n" + "="*60)
        print("🔍 RESULTADO DE LA PRUEBA")
        print("="*60)
        for campo, valor in empresa_prueba.items():
            print(f"{campo}: {valor}")
        print("="*60)

    else:
        # Procesar empresas del CSV
        empresas = scraper.procesar_empresas(
            args.archivo_csv,
            max_empresas=args.max_empresas
        )

        if empresas:
            # Guardar resultados
            scraper.guardar_resultados(empresas)
        else:
            logging.error("No se pudieron procesar las empresas")

if __name__ == "__main__":
    main()
