#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper con visualización en tiempo real
Ejecuta el scraper y genera automáticamente la página de visualización
"""

import subprocess
import time
import os
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def ejecutar_scraper(max_empresas=None):
    """Ejecuta el scraper de detalles"""
    try:
        cmd = ['py', 'scraper_detalles_empresas_sqlite.py']
        if max_empresas:
            cmd.extend(['--max-empresas', str(max_empresas)])

        logging.info(f"Ejecutando scraper: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logging.info("✅ Scraper ejecutado correctamente")
            return True
        else:
            logging.error(f"❌ Error en scraper: {result.stderr}")
            return False

    except Exception as e:
        logging.error(f"❌ Error ejecutando scraper: {e}")
        return False

def generar_visualizacion():
    """Genera la página de visualización"""
    try:
        logging.info("Generando página de visualización...")
        result = subprocess.run(['py', 'visualizacion_tiempo_real.py'],
                              capture_output=True, text=True)

        if result.returncode == 0:
            logging.info("✅ Página de visualización generada")
            return True
        else:
            logging.error(f"❌ Error generando visualización: {result.stderr}")
            return False

    except Exception as e:
        logging.error(f"❌ Error generando visualización: {e}")
        return False

def encontrar_archivo_visualizacion():
    """Encuentra el archivo de visualización más reciente"""
    archivos = [f for f in os.listdir('.') if f.startswith('visualizacion_tiempo_real_') and f.endswith('.html')]
    if archivos:
        return max(archivos)
    return None

def main():
    print("🚀 Iniciando sistema de scraping con visualización en tiempo real")
    print("="*60)

    # Parámetros
    max_empresas = input("Número de empresas a procesar (Enter para todas): ").strip()
    max_empresas = int(max_empresas) if max_empresas else None

    intervalo_visualizacion = input("Intervalo de actualización de visualización (segundos, default 30): ").strip()
    intervalo_visualizacion = int(intervalo_visualizacion) if intervalo_visualizacion else 30

    print(f"\n📊 Configuración:")
    print(f"   - Empresas a procesar: {'Todas' if max_empresas is None else max_empresas}")
    print(f"   - Intervalo de visualización: {intervalo_visualizacion} segundos")
    print("="*60)

    # Generar visualización inicial
    if generar_visualizacion():
        archivo_html = encontrar_archivo_visualizacion()
        if archivo_html:
            print(f"🌐 Página inicial generada: {archivo_html}")
            print(f"   Abre este archivo en tu navegador para ver los datos en tiempo real")

    # Ejecutar scraper
    print(f"\n🔄 Ejecutando scraper...")
    if ejecutar_scraper(max_empresas):
        print("✅ Scraper completado")

        # Generar visualización final
        if generar_visualizacion():
            archivo_html = encontrar_archivo_visualizacion()
            if archivo_html:
                print(f"🌐 Página final generada: {archivo_html}")
                print(f"   Abre este archivo en tu navegador para ver los resultados")
    else:
        print("❌ Error en el scraper")

if __name__ == "__main__":
    main()
