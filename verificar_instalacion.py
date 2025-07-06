#!/usr/bin/env python3
"""
Script de verificación de instalación
Verifica que todas las dependencias estén instaladas correctamente
"""

import sys
import importlib

def print_header():
    """Imprime el encabezado del verificador"""
    print("=" * 60)
    print("🔍 VERIFICADOR DE INSTALACIÓN - SCRAPER DE EMPRESAS")
    print("=" * 60)
    print()

def check_dependency(module_name, package_name=None):
    """Verifica si una dependencia está instalada"""
    if package_name is None:
        package_name = module_name

    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - NO INSTALADO")
        return False

def check_python_version():
    """Verifica la versión de Python"""
    print("🐍 Verificando versión de Python...")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python {version.major}.{version.minor} detectado")
        print("   Se requiere Python 3.7 o superior")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detectado")
        return True

def check_dependencies():
    """Verifica todas las dependencias"""
    print("\n📦 Verificando dependencias...")

    dependencies = [
        ('pandas', 'pandas'),
        ('requests', 'requests'),
        ('bs4', 'beautifulsoup4'),
        ('selenium', 'selenium'),
        ('fake_useragent', 'fake-useragent'),
        ('webdriver_manager', 'webdriver-manager'),
        ('openpyxl', 'openpyxl'),
        ('dotenv', 'python-dotenv')
    ]

    failed = []

    for module, package in dependencies:
        if not check_dependency(module, package):
            failed.append(package)

    return failed

def check_files():
    """Verifica que los archivos necesarios estén presentes"""
    print("\n📁 Verificando archivos del proyecto...")

    required_files = [
        'municipios_pedanias_codigos_postales_corregidos.csv',
        'empresa_scraper.py',
        'scraper_avanzado.py',
        'config.py',
        'requirements.txt',
        'validador_cif.py'
    ]

    missing_files = []

    for file in required_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                print(f"✅ {file}")
        except FileNotFoundError:
            print(f"❌ {file} - NO ENCONTRADO")
            missing_files.append(file)

    return missing_files

def test_basic_functionality():
    """Prueba funcionalidad básica"""
    print("\n🧪 Probando funcionalidad básica...")

    try:
        # Probar importación de módulos principales
        import pandas as pd
        import requests
        from bs4 import BeautifulSoup

        print("✅ Módulos principales importados correctamente")

        # Probar request básico
        response = requests.get("https://httpbin.org/get", timeout=10)
        if response.status_code == 200:
            print("✅ Conexión a internet funcionando")
        else:
            print("❌ Problema con conexión a internet")
            return False

        # Probar lectura de CSV
        try:
            df = pd.read_csv('municipios_pedanias_codigos_postales_corregidos.csv')
            print(f"✅ CSV leído correctamente ({len(df)} filas)")
        except Exception as e:
            print(f"❌ Error al leer CSV: {e}")
            return False

        return True

    except Exception as e:
        print(f"❌ Error en prueba básica: {e}")
        return False

def main():
    """Función principal"""
    print_header()

    # Verificar versión de Python
    python_ok = check_python_version()

    # Verificar dependencias
    failed_deps = check_dependencies()

    # Verificar archivos
    missing_files = check_files()

    # Probar funcionalidad
    functionality_ok = test_basic_functionality()

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)

    if python_ok:
        print("✅ Python: OK")
    else:
        print("❌ Python: PROBLEMA")

    if not failed_deps:
        print("✅ Dependencias: TODAS INSTALADAS")
    else:
        print(f"❌ Dependencias: {len(failed_deps)} FALTANTES")
        print(f"   Faltan: {', '.join(failed_deps)}")

    if not missing_files:
        print("✅ Archivos: TODOS PRESENTES")
    else:
        print(f"❌ Archivos: {len(missing_files)} FALTANTES")
        print(f"   Faltan: {', '.join(missing_files)}")

    if functionality_ok:
        print("✅ Funcionalidad: OK")
    else:
        print("❌ Funcionalidad: PROBLEMA")

    # Recomendaciones
    print("\n💡 RECOMENDACIONES:")

    if failed_deps:
        print("   - Ejecuta: py -m pip install -r requirements.txt")

    if missing_files:
        print("   - Asegúrate de tener todos los archivos del proyecto")

    if not functionality_ok:
        print("   - Revisa la conexión a internet")
        print("   - Verifica que el archivo CSV esté presente")

    if python_ok and not failed_deps and not missing_files and functionality_ok:
        print("\n🎉 ¡INSTALACIÓN COMPLETA Y FUNCIONAL!")
        print("   Puedes ejecutar: py empresa_scraper.py")
    else:
        print("\n⚠️  Hay problemas que resolver antes de usar la aplicación")

if __name__ == "__main__":
    main()
