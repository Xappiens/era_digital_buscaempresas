#!/usr/bin/env python3
"""
Script de prueba para el scraper de empresas
Prueba la funcionalidad básica con un código postal
"""

import sys
import os
import pandas as pd
from datetime import datetime

def test_csv_loading():
    """Prueba la carga del archivo CSV"""
    print("🔍 Probando carga del archivo CSV...")

    try:
        df = pd.read_csv("municipios_pedanias_codigos_postales_corregidos.csv")
        print(f"✅ CSV cargado correctamente")
        print(f"   - Filas: {len(df)}")
        print(f"   - Columnas: {list(df.columns)}")
        print(f"   - Códigos postales únicos: {len(df['codigo_postal'].unique())}")

        # Mostrar algunos códigos postales
        codigos_muestra = df['codigo_postal'].unique()[:5]
        print(f"   - Muestra de códigos: {list(codigos_muestra)}")

        return True, df

    except Exception as e:
        print(f"❌ Error al cargar CSV: {e}")
        return False, None

def test_dependencies():
    """Prueba que las dependencias estén instaladas"""
    print("\n🔍 Probando dependencias...")

    dependencies = [
        ('pandas', 'pandas'),
        ('requests', 'requests'),
        ('bs4', 'beautifulsoup4'),
        ('selenium', 'selenium'),
        ('fake_useragent', 'fake-useragent'),
        ('openpyxl', 'openpyxl')
    ]

    missing = []
    for module, package in dependencies:
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NO INSTALADO")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Dependencias faltantes: {missing}")
        print("   Ejecuta: pip install -r requirements.txt")
        return False
    else:
        print("✅ Todas las dependencias están instaladas")
        return True

def test_basic_scraper():
    """Prueba el scraper básico con un código postal"""
    print("\n🔍 Probando scraper básico...")

    try:
        from empresa_scraper import EmpresaScraper

        scraper = EmpresaScraper()

        # Probar con un código postal
        codigo_test = "30180"  # Bullas

        print(f"   Probando con código postal: {codigo_test}")

        # Probar búsqueda en Google
        resultados = scraper.buscar_en_google(codigo_test, 1)
        print(f"   - Resultados Google: {len(resultados)}")

        if resultados:
            print(f"   - Primer resultado: {resultados[0]['titulo'][:50]}...")

        return True

    except Exception as e:
        print(f"❌ Error en scraper básico: {e}")
        return False

def test_advanced_scraper():
    """Prueba el scraper avanzado"""
    print("\n🔍 Probando scraper avanzado...")

    try:
        from scraper_avanzado import ScraperAvanzado

        scraper = ScraperAvanzado()

        # Probar carga de códigos postales
        codigos = scraper.cargar_codigos_postales("municipios_pedanias_codigos_postales_corregidos.csv")

        if len(codigos) > 0:
            print(f"   ✅ Códigos cargados: {len(codigos)}")
            print(f"   - Muestra: {list(codigos[:3])}")
            return True
        else:
            print("   ❌ No se pudieron cargar códigos postales")
            return False

    except Exception as e:
        print(f"❌ Error en scraper avanzado: {e}")
        return False

def test_config():
    """Prueba la configuración"""
    print("\n🔍 Probando configuración...")

    try:
        from config import Config

        print(f"   ✅ Configuración cargada")
        print(f"   - Archivo CSV: {Config.ARCHIVO_CSV_ENTRADA}")
        print(f"   - Max códigos: {Config.MAX_CODIGOS_POSTALES}")
        print(f"   - Max páginas Google: {Config.MAX_PAGINAS_GOOGLE}")
        print(f"   - Fuentes habilitadas: {sum(Config.FUENTES_HABILITADAS.values())}")

        return True

    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def run_demo():
    """Ejecuta una demostración con pocos códigos postales"""
    print("\n🚀 Ejecutando demostración...")

    try:
        from scraper_avanzado import ScraperAvanzado

        scraper = ScraperAvanzado()

        # Ejecutar con solo 1 código postal para prueba
        empresas = scraper.ejecutar_busqueda_avanzada(
            "municipios_pedanias_codigos_postales_corregidos.csv",
            max_codigos=1
        )

        print(f"   ✅ Demostración completada")
        print(f"   - Empresas encontradas: {len(empresas)}")

        if empresas:
            print(f"   - Primera empresa: {empresas[0]['razon_social']}")

        # Guardar resultados de prueba
        scraper.guardar_resultados_avanzados("demo_empresas.xlsx")

        return True

    except Exception as e:
        print(f"❌ Error en demostración: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 INICIANDO PRUEBAS DEL SCRAPER DE EMPRESAS")
    print("=" * 50)

    tests = [
        ("Carga CSV", test_csv_loading),
        ("Dependencias", test_dependencies),
        ("Configuración", test_config),
        ("Scraper Básico", test_basic_scraper),
        ("Scraper Avanzado", test_advanced_scraper),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {e}")
            results.append((test_name, False))

    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)

    passed = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1

    print(f"\nTotal: {passed}/{len(results)} pruebas pasaron")

    if passed == len(results):
        print("\n🎉 ¡Todas las pruebas pasaron! El scraper está listo para usar.")

        # Preguntar si ejecutar demo
        try:
            response = input("\n¿Ejecutar demostración? (s/n): ").lower()
            if response in ['s', 'si', 'sí', 'y', 'yes']:
                run_demo()
        except KeyboardInterrupt:
            print("\nDemo cancelada por el usuario")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        print("   Asegúrate de instalar todas las dependencias:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()
