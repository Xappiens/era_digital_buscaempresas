#!/usr/bin/env python3
"""
Ejemplo de uso del scraper de empresas
Muestra cómo usar la aplicación con configuración personalizada
"""

import pandas as pd
from datetime import datetime
import time

def ejemplo_basico():
    """Ejemplo básico de uso del scraper"""
    print("=" * 50)
    print("EJEMPLO BÁSICO - Scraper de Empresas")
    print("=" * 50)

    try:
        from empresa_scraper import EmpresaScraper

        # Crear instancia del scraper
        scraper = EmpresaScraper()

        # Configurar parámetros
        archivo_csv = "municipios_pedanias_codigos_postales_corregidos.csv"
        max_codigos = 2  # Solo procesar 2 códigos postales para el ejemplo

        print(f"📁 Archivo CSV: {archivo_csv}")
        print(f"🔢 Códigos postales a procesar: {max_codigos}")
        print()

        # Ejecutar búsqueda
        print("🚀 Iniciando búsqueda...")
        empresas = scraper.ejecutar_busqueda(archivo_csv, max_codigos=max_codigos)

        # Guardar resultados
        archivo_salida = f"ejemplo_basico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        scraper.guardar_resultados(archivo_salida)

        print(f"\n✅ Ejemplo básico completado")
        print(f"📊 Empresas encontradas: {len(empresas)}")
        print(f"💾 Resultados guardados en: {archivo_salida}")

        return True

    except Exception as e:
        print(f"❌ Error en ejemplo básico: {e}")
        return False

def ejemplo_avanzado():
    """Ejemplo avanzado con configuración personalizada"""
    print("\n" + "=" * 50)
    print("EJEMPLO AVANZADO - Scraper Avanzado")
    print("=" * 50)

    try:
        from scraper_avanzado import ScraperAvanzado

        # Crear instancia del scraper avanzado
        scraper = ScraperAvanzado()

        # Configuración personalizada
        archivo_csv = "municipios_pedanias_codigos_postales_corregidos.csv"
        max_codigos = 1  # Solo 1 código postal para el ejemplo

        print(f"📁 Archivo CSV: {archivo_csv}")
        print(f"🔢 Códigos postales a procesar: {max_codigos}")
        print("🔧 Configuración avanzada activada")
        print()

        # Ejecutar búsqueda avanzada
        print("🚀 Iniciando búsqueda avanzada...")
        empresas = scraper.ejecutar_busqueda_avanzada(archivo_csv, max_codigos=max_codigos)

        # Guardar resultados con formato avanzado
        archivo_salida = f"ejemplo_avanzado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        scraper.guardar_resultados_avanzados(archivo_salida)

        print(f"\n✅ Ejemplo avanzado completado")
        print(f"📊 Empresas encontradas: {len(empresas)}")
        print(f"💾 Resultados guardados en: {archivo_salida}")

        return True

    except Exception as e:
        print(f"❌ Error en ejemplo avanzado: {e}")
        return False

def ejemplo_codigo_especifico():
    """Ejemplo buscando en un código postal específico"""
    print("\n" + "=" * 50)
    print("EJEMPLO - CÓDIGO POSTAL ESPECÍFICO")
    print("=" * 50)

    try:
        from scraper_avanzado import ScraperAvanzado

        # Crear instancia del scraper
        scraper = ScraperAvanzado()

        # Código postal específico (Bullas)
        codigo_postal = "30180"

        print(f"🔍 Buscando empresas en código postal: {codigo_postal}")
        print()

        # Procesar solo este código postal
        empresas = scraper.procesar_codigo_postal_avanzado(codigo_postal)

        if empresas:
            print(f"\n📊 Empresas encontradas en {codigo_postal}: {len(empresas)}")
            print("\n📋 Muestra de empresas:")

            for i, empresa in enumerate(empresas[:3], 1):
                print(f"   {i}. {empresa['razon_social']}")
                print(f"      📍 {empresa['direccion']}")
                print(f"      📧 {empresa['email']}")
                print(f"      📞 {empresa['telefono']}")
                print(f"      🏢 {empresa['fuente']}")
                print()
        else:
            print("❌ No se encontraron empresas para este código postal")

        return True

    except Exception as e:
        print(f"❌ Error en ejemplo código específico: {e}")
        return False

def ejemplo_analisis_datos():
    """Ejemplo de análisis de los datos obtenidos"""
    print("\n" + "=" * 50)
    print("EJEMPLO - ANÁLISIS DE DATOS")
    print("=" * 50)

    try:
        # Cargar datos de ejemplo (si existen)
        archivos_resultado = [
            "empresas_encontradas.xlsx",
            "empresas_avanzadas.xlsx",
            "demo_empresas.xlsx"
        ]

        df = None
        for archivo in archivos_resultado:
            try:
                df = pd.read_excel(archivo)
                print(f"📊 Datos cargados desde: {archivo}")
                break
            except:
                continue

        if df is None:
            print("❌ No se encontraron archivos de resultados")
            print("   Ejecuta primero uno de los ejemplos anteriores")
            return False

        # Análisis básico
        print(f"\n📈 ANÁLISIS DE DATOS:")
        print(f"   - Total empresas: {len(df)}")
        print(f"   - Empresas con email: {len(df[df['email'].notna() & (df['email'] != '')])}")
        print(f"   - Empresas con teléfono: {len(df[df['telefono'].notna() & (df['telefono'] != '')])}")
        print(f"   - Empresas con CNAE: {len(df[df['cnae'].notna() & (df['cnae'] != '')])}")

        # Análisis por fuentes
        if 'fuente' in df.columns:
            print(f"\n📊 DISTRIBUCIÓN POR FUENTES:")
            fuentes = df['fuente'].value_counts()
            for fuente, cantidad in fuentes.items():
                print(f"   - {fuente}: {cantidad}")

        # Análisis por códigos postales
        if 'codigo_postal' in df.columns:
            print(f"\n📮 EMPRESAS POR CÓDIGO POSTAL:")
            codigos = df['codigo_postal'].value_counts().head(5)
            for codigo, cantidad in codigos.items():
                print(f"   - {codigo}: {cantidad}")

        # Guardar análisis
        archivo_analisis = f"analisis_empresas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(archivo_analisis, 'w', encoding='utf-8') as f:
            f.write("ANÁLISIS DE EMPRESAS ENCONTRADAS\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total empresas: {len(df)}\n\n")

            if 'fuente' in df.columns:
                f.write("DISTRIBUCIÓN POR FUENTES:\n")
                for fuente, cantidad in fuentes.items():
                    f.write(f"- {fuente}: {cantidad}\n")
                f.write("\n")

            if 'codigo_postal' in df.columns:
                f.write("EMPRESAS POR CÓDIGO POSTAL:\n")
                for codigo, cantidad in codigos.items():
                    f.write(f"- {codigo}: {cantidad}\n")

        print(f"\n💾 Análisis guardado en: {archivo_analisis}")

        return True

    except Exception as e:
        print(f"❌ Error en análisis de datos: {e}")
        return False

def menu_principal():
    """Menú principal de ejemplos"""
    print("🧪 EJEMPLOS DE USO - SCRAPER DE EMPRESAS")
    print("=" * 50)
    print()
    print("Selecciona un ejemplo:")
    print("1. Ejemplo básico (2 códigos postales)")
    print("2. Ejemplo avanzado (1 código postal)")
    print("3. Código postal específico (Bullas)")
    print("4. Análisis de datos")
    print("5. Ejecutar todos los ejemplos")
    print("0. Salir")
    print()

    try:
        opcion = input("Opción: ").strip()

        if opcion == "1":
            ejemplo_basico()
        elif opcion == "2":
            ejemplo_avanzado()
        elif opcion == "3":
            ejemplo_codigo_especifico()
        elif opcion == "4":
            ejemplo_analisis_datos()
        elif opcion == "5":
            print("\n🚀 Ejecutando todos los ejemplos...")
            ejemplo_basico()
            time.sleep(2)
            ejemplo_avanzado()
            time.sleep(2)
            ejemplo_codigo_especifico()
            time.sleep(2)
            ejemplo_analisis_datos()
            print("\n✅ Todos los ejemplos completados")
        elif opcion == "0":
            print("👋 ¡Hasta luego!")
            return False
        else:
            print("❌ Opción no válida")

        return True

    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return True

def main():
    """Función principal"""
    print("🎯 EJEMPLOS DE USO DEL SCRAPER DE EMPRESAS")
    print("Región de Murcia - Códigos Postales")
    print()

    # Verificar que el archivo CSV existe
    try:
        df = pd.read_csv("municipios_pedanias_codigos_postales_corregidos.csv")
        print(f"✅ Archivo CSV cargado: {len(df)} filas, {len(df['codigo_postal'].unique())} códigos únicos")
    except Exception as e:
        print(f"❌ Error al cargar CSV: {e}")
        print("   Asegúrate de que el archivo esté en el directorio actual")
        return

    print()

    # Ejecutar menú
    while menu_principal():
        print("\n" + "=" * 50)
        input("Presiona Enter para continuar...")

if __name__ == "__main__":
    main()
