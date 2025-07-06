#!/usr/bin/env python3
"""
Script de instalación para el scraper de empresas
Instala dependencias y configura el entorno
"""

import subprocess
import sys
import os
import platform

def print_header():
    """Imprime el encabezado del instalador"""
    print("=" * 60)
    print("🚀 INSTALADOR DEL SCRAPER DE EMPRESAS - REGIÓN DE MURCIA")
    print("=" * 60)
    print()

def check_python_version():
    """Verifica la versión de Python"""
    print("🔍 Verificando versión de Python...")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python {version.major}.{version.minor} detectado")
        print("   Se requiere Python 3.7 o superior")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detectado")
        return True

def install_pip():
    """Instala o actualiza pip"""
    print("\n🔍 Verificando pip...")

    try:
        import pip
        print("✅ pip está disponible")
        return True
    except ImportError:
        print("❌ pip no está disponible")
        print("   Instalando pip...")

        try:
            # Descargar get-pip.py
            import urllib.request
            url = "https://bootstrap.pypa.io/get-pip.py"
            urllib.request.urlretrieve(url, "get-pip.py")

            # Instalar pip
            subprocess.check_call([sys.executable, "get-pip.py"])

            # Limpiar archivo temporal
            os.remove("get-pip.py")

            print("✅ pip instalado correctamente")
            return True

        except Exception as e:
            print(f"❌ Error al instalar pip: {e}")
            return False

def install_dependencies():
    """Instala las dependencias del proyecto"""
    print("\n🔍 Instalando dependencias...")

    # Intentar instalar desde requirements.txt primero
    if os.path.exists('requirements.txt'):
        try:
            print("   Instalando desde requirements.txt...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("   ✅ Dependencias instaladas desde requirements.txt")
            return True
        except subprocess.CalledProcessError:
            print("   ⚠️  Error al instalar desde requirements.txt, intentando individualmente...")

    # Lista de dependencias como fallback
    dependencies = [
        'pandas',
        'requests',
        'beautifulsoup4',
        'selenium',
        'fake-useragent',
        'webdriver-manager',
        'openpyxl'
    ]

    failed = []

    for dep in dependencies:
        try:
            print(f"   Instalando {dep}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", dep
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"   ✅ {dep} instalado")
        except subprocess.CalledProcessError:
            print(f"   ❌ Error al instalar {dep}")
            failed.append(dep)

    if failed:
        print(f"\n⚠️  Fallaron {len(failed)} dependencias: {failed}")
        return False
    else:
        print("\n✅ Todas las dependencias instaladas correctamente")
        return True

def check_csv_file():
    """Verifica que el archivo CSV esté presente"""
    print("\n🔍 Verificando archivo CSV...")

    csv_file = "municipios_pedanias_codigos_postales_corregidos.csv"

    if os.path.exists(csv_file):
        print(f"✅ Archivo {csv_file} encontrado")

        # Verificar que sea un CSV válido
        try:
            import pandas as pd
            df = pd.read_csv(csv_file)
            print(f"   - Filas: {len(df)}")
            print(f"   - Columnas: {list(df.columns)}")
            print(f"   - Códigos postales únicos: {len(df['codigo_postal'].unique())}")
            return True
        except Exception as e:
            print(f"❌ Error al leer CSV: {e}")
            return False
    else:
        print(f"❌ Archivo {csv_file} no encontrado")
        print("   Asegúrate de que el archivo esté en el directorio actual")
        return False

def create_sample_config():
    """Crea un archivo de configuración de ejemplo"""
    print("\n🔍 Creando configuración de ejemplo...")

    config_content = '''# Configuración del scraper de empresas
# Modifica estos valores según tus necesidades

# Número máximo de códigos postales a procesar (None = todos)
MAX_CODIGOS_POSTALES = 5

# Número máximo de páginas a buscar en Google
MAX_PAGINAS_GOOGLE = 3

# Pausas entre operaciones (segundos)
PAUSA_ENTRE_CODIGOS = (3, 7)
PAUSA_ENTRE_PAGINAS = (2, 5)

# Fuentes habilitadas
FUENTES_HABILITADAS = {
    'google': True,
    'paginas_amarillas': True,
    'einforma': True,
    'axesor': True,
    'infoempresas': True,
    'redes_sociales': False
}
'''

    try:
        with open('config_ejemplo.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ Archivo config_ejemplo.py creado")
        return True
    except Exception as e:
        print(f"❌ Error al crear configuración: {e}")
        return False

def run_test():
    """Ejecuta una prueba básica"""
    print("\n🔍 Ejecutando prueba básica...")

    try:
        # Importar módulos principales
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

        return True

    except Exception as e:
        print(f"❌ Error en prueba básica: {e}")
        return False

def show_next_steps():
    """Muestra los próximos pasos"""
    print("\n" + "=" * 60)
    print("🎉 INSTALACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("Próximos pasos:")
    print()
    print("1. 🔧 Configurar parámetros:")
    print("   - Edita config.py para ajustar la configuración")
    print("   - O usa config_ejemplo.py como referencia")
    print()
    print("2. 🧪 Ejecutar pruebas:")
    print("   python test_scraper.py")
    print()
    print("3. 🚀 Ejecutar scraper básico:")
    print("   python empresa_scraper.py")
    print()
    print("4. 🚀 Ejecutar scraper avanzado:")
    print("   python scraper_avanzado.py")
    print()
    print("5. 📖 Leer documentación:")
    print("   Consulta README.md para más detalles")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - Respeta los términos de servicio de las webs")
    print("   - No sobrecargues los servidores")
    print("   - Usa la información de manera ética y legal")
    print()

def main():
    """Función principal del instalador"""
    print_header()

    # Verificar Python
    if not check_python_version():
        print("\n❌ Instalación cancelada: Python 3.7+ requerido")
        return False

    # Instalar pip si es necesario
    if not install_pip():
        print("\n❌ Instalación cancelada: No se pudo instalar pip")
        return False

    # Instalar dependencias
    if not install_dependencies():
        print("\n⚠️  Algunas dependencias fallaron, pero puedes continuar")

    # Verificar archivo CSV
    if not check_csv_file():
        print("\n⚠️  Archivo CSV no encontrado, pero puedes continuar")

    # Crear configuración de ejemplo
    create_sample_config()

    # Ejecutar prueba básica
    if run_test():
        print("✅ Prueba básica exitosa")
    else:
        print("⚠️  Prueba básica falló, pero puedes continuar")

    # Mostrar próximos pasos
    show_next_steps()

    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Instalación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("   Intenta ejecutar: pip install -r requirements.txt")
