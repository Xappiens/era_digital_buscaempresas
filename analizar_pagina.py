import requests
from bs4 import BeautifulSoup
import re

def analizar_pagina(url):
    """Analiza la estructura de una página de Axesor"""
    print(f"Analizando: {url}")

    # Headers para simular un navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        print(f"Título: {soup.title.string if soup.title else 'Sin título'}")
        print(f"Longitud del contenido: {len(response.content)} bytes")

        # Buscar tablas
        tablas = soup.find_all('table')
        print(f"Encontradas {len(tablas)} tablas")

        # Buscar elementos que contengan información de contacto
        elementos_telefono = soup.find_all(string=re.compile(r'\d{9}', re.IGNORECASE))
        print(f"Elementos con números de teléfono: {len(elementos_telefono)}")

        # Buscar elementos que contengan CIF
        elementos_cif = soup.find_all(string=re.compile(r'[A-Z]\d{8}', re.IGNORECASE))
        print(f"Elementos con CIF: {len(elementos_cif)}")

        # Buscar elementos que contengan "objeto social"
        elementos_objeto = soup.find_all(string=re.compile(r'objeto social', re.IGNORECASE))
        print(f"Elementos con 'objeto social': {len(elementos_objeto)}")

        # Mostrar algunos ejemplos
        print("\nEjemplos de elementos con teléfono:")
        for i, elem in enumerate(elementos_telefono[:5]):
            print(f"  {i+1}: {elem.strip()}")

        print("\nEjemplos de elementos con CIF:")
        for i, elem in enumerate(elementos_cif[:5]):
            print(f"  {i+1}: {elem.strip()}")

        print("\nEjemplos de elementos con objeto social:")
        for i, elem in enumerate(elementos_objeto[:5]):
            print(f"  {i+1}: {elem.strip()}")

        # Buscar todos los td que contengan texto largo
        tds = soup.find_all('td')
        tds_largos = [td for td in tds if td.get_text(strip=True) and len(td.get_text(strip=True)) > 50]
        print(f"\nTDs con texto largo (>50 chars): {len(tds_largos)}")

        for i, td in enumerate(tds_largos[:3]):
            texto = td.get_text(strip=True)
            print(f"  TD {i+1}: {texto[:100]}...")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    url = "https://www.axesor.es/Informes-Empresas/1562295/JAVIER_VILLAESCUSA_SL.html"
    analizar_pagina(url)
