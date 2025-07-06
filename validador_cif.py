#!/usr/bin/env python3
"""
Validador y limpiador de CIF (Código de Identificación Fiscal)
Utilidades para validar, limpiar y verificar CIFs españoles
"""

import re
import pandas as pd
from datetime import datetime

class ValidadorCIF:
    """Clase para validar y limpiar CIFs españoles"""

    # Tabla de multiplicadores para validación
    MULTIPLICADORES = [1, 2, 1, 2, 1, 2, 1, 2]

    # Letras válidas para CIF
    LETRAS_VALIDAS = 'ABCDEFGHJNPQRSUVW'

    # Tipos de entidad por letra inicial
    TIPOS_ENTIDAD = {
        'A': 'Sociedades Anónimas',
        'B': 'Sociedades de Responsabilidad Limitada',
        'C': 'Sociedades Colectivas',
        'D': 'Sociedades Comanditarias',
        'E': 'Comunidades de Bienes',
        'F': 'Sociedades Cooperativas',
        'G': 'Asociaciones',
        'H': 'Comunidades de Propietarios',
        'J': 'Sociedades Civiles',
        'N': 'Entidades Extranjeras',
        'P': 'Corporaciones Locales',
        'Q': 'Organismos Públicos',
        'R': 'Congregaciones e Instituciones Religiosas',
        'S': 'Órganos de la Administración del Estado',
        'U': 'Uniones Temporales de Empresas',
        'V': 'Otros tipos no definidos',
        'W': 'Establecimientos Permanentes de Entidades no Residentes'
    }

    @classmethod
    def limpiar_cif(cls, cif):
        """Limpia un CIF eliminando espacios y caracteres especiales"""
        if not cif:
            return None

        # Convertir a mayúsculas y eliminar espacios
        cif_limpio = str(cif).strip().upper()

        # Eliminar caracteres especiales excepto letras y números
        cif_limpio = re.sub(r'[^A-Z0-9]', '', cif_limpio)

        return cif_limpio if cif_limpio else None

    @classmethod
    def validar_formato(cls, cif):
        """Valida el formato básico de un CIF"""
        if not cif:
            return False, "CIF vacío"

        cif_limpio = cls.limpiar_cif(cif)
        if not cif_limpio:
            return False, "CIF no válido después de limpieza"

        # Verificar longitud (8 o 9 caracteres)
        if len(cif_limpio) not in [8, 9]:
            return False, f"Longitud incorrecta: {len(cif_limpio)} caracteres"

        # Verificar que empiece con letra válida
        if cif_limpio[0] not in cls.LETRAS_VALIDAS:
            return False, f"Letra inicial no válida: {cif_limpio[0]}"

        # Verificar que el resto sean números (excepto posible letra final)
        if len(cif_limpio) == 8:
            # CIF de 8 dígitos: letra + 7 números
            if not cif_limpio[1:].isdigit():
                return False, "Los caracteres 2-8 deben ser números"
        else:
            # CIF de 9 dígitos: letra + 7 números + letra/número
            if not cif_limpio[1:8].isdigit():
                return False, "Los caracteres 2-8 deben ser números"

        return True, "Formato válido"

    @classmethod
    def calcular_digito_control(cls, cif):
        """Calcula el dígito de control de un CIF"""
        if not cif or len(cif) < 8:
            return None

        # Tomar los 7 dígitos centrales
        numeros = cif[1:8]

        # Calcular suma ponderada
        suma = 0
        for i, numero in enumerate(numeros):
            producto = int(numero) * cls.MULTIPLICADORES[i]
            # Sumar las cifras del producto
            suma += sum(int(d) for d in str(producto))

        # Calcular dígito de control
        digito_control = (10 - (suma % 10)) % 10

        return str(digito_control)

    @classmethod
    def validar_digito_control(cls, cif):
        """Valida el dígito de control de un CIF"""
        if not cif or len(cif) != 9:
            return False, "CIF debe tener 9 caracteres para validar dígito de control"

        digito_calculado = cls.calcular_digito_control(cif)
        digito_real = cif[8]

        if digito_calculado == digito_real:
            return True, "Dígito de control válido"
        else:
            return False, f"Dígito de control incorrecto. Esperado: {digito_calculado}, Encontrado: {digito_real}"

    @classmethod
    def validar_cif_completo(cls, cif):
        """Valida un CIF completo (formato + dígito de control)"""
        # Validar formato
        formato_valido, mensaje_formato = cls.validar_formato(cif)
        if not formato_valido:
            return False, mensaje_formato

        cif_limpio = cls.limpiar_cif(cif)

        # Si tiene 9 caracteres, validar dígito de control
        if len(cif_limpio) == 9:
            control_valido, mensaje_control = cls.validar_digito_control(cif_limpio)
            if not control_valido:
                return False, mensaje_control

        return True, "CIF válido"

    @classmethod
    def obtener_tipo_entidad(cls, cif):
        """Obtiene el tipo de entidad basado en la letra inicial"""
        if not cif:
            return None

        cif_limpio = cls.limpiar_cif(cif)
        if not cif_limpio:
            return None

        letra_inicial = cif_limpio[0]
        return cls.TIPOS_ENTIDAD.get(letra_inicial, "Tipo no definido")

    @classmethod
    def completar_cif(cls, cif):
        """Completa un CIF de 8 dígitos calculando el dígito de control"""
        if not cif:
            return None

        cif_limpio = cls.limpiar_cif(cif)
        if not cif_limpio or len(cif_limpio) != 8:
            return None

        digito_control = cls.calcular_digito_control(cif_limpio)
        if digito_control:
            return cif_limpio + digito_control

        return None

class ProcesadorCIF:
    """Clase para procesar CIFs en archivos de datos"""

    def __init__(self):
        self.validador = ValidadorCIF()
        self.estadisticas = {
            'total': 0,
            'validos': 0,
            'invalidos': 0,
            'completados': 0,
            'tipos_entidad': {}
        }

    def procesar_archivo(self, archivo_entrada, archivo_salida=None):
        """Procesa un archivo Excel/CSV y valida/limpia los CIFs"""
        print(f"🔍 Procesando archivo: {archivo_entrada}")

        try:
            # Cargar archivo
            if archivo_entrada.endswith('.xlsx'):
                df = pd.read_excel(archivo_entrada)
            else:
                df = pd.read_csv(archivo_entrada)

            print(f"📊 Archivo cargado: {len(df)} filas")

            # Buscar columna CIF
            columna_cif = None
            for col in df.columns:
                if 'cif' in col.lower():
                    columna_cif = col
                    break

            if not columna_cif:
                print("❌ No se encontró columna CIF en el archivo")
                return None

            print(f"✅ Columna CIF encontrada: {columna_cif}")

            # Procesar CIFs
            df_procesado = self.procesar_dataframe(df, columna_cif)

            # Guardar resultados
            if archivo_salida:
                if archivo_salida.endswith('.xlsx'):
                    df_procesado.to_excel(archivo_salida, index=False)
                else:
                    df_procesado.to_csv(archivo_salida, index=False, encoding='utf-8-sig')

                print(f"💾 Resultados guardados en: {archivo_salida}")

            # Mostrar estadísticas
            self.mostrar_estadisticas()

            return df_procesado

        except Exception as e:
            print(f"❌ Error al procesar archivo: {e}")
            return None

    def procesar_dataframe(self, df, columna_cif):
        """Procesa un DataFrame y valida/limpia los CIFs"""
        # Crear copia del DataFrame
        df_procesado = df.copy()

        # Agregar columnas de validación
        df_procesado['cif_original'] = df_procesado[columna_cif]
        df_procesado['cif_limpio'] = df_procesado[columna_cif].apply(ValidadorCIF.limpiar_cif)
        df_procesado['cif_valido'] = df_procesado['cif_limpio'].apply(lambda x: ValidadorCIF.validar_cif_completo(x)[0] if x else False)
        df_procesado['cif_completado'] = df_procesado['cif_limpio'].apply(lambda x: ValidadorCIF.completar_cif(x) if x and len(x) == 8 else x)
        df_procesado['tipo_entidad'] = df_procesado['cif_limpio'].apply(ValidadorCIF.obtener_tipo_entidad)

        # Actualizar estadísticas
        self.actualizar_estadisticas(df_procesado)

        return df_procesado

    def actualizar_estadisticas(self, df):
        """Actualiza las estadísticas de procesamiento"""
        self.estadisticas['total'] = len(df)
        self.estadisticas['validos'] = len(df[df['cif_valido'] == True])
        self.estadisticas['invalidos'] = len(df[df['cif_valido'] == False])
        self.estadisticas['completados'] = len(df[df['cif_completado'].notna() & (df['cif_completado'] != df['cif_limpio'])])

        # Tipos de entidad
        tipos = df['tipo_entidad'].value_counts()
        self.estadisticas['tipos_entidad'] = tipos.to_dict()

    def mostrar_estadisticas(self):
        """Muestra las estadísticas de procesamiento"""
        print("\n📊 ESTADÍSTICAS DE PROCESAMIENTO CIF:")
        print(f"   - Total CIFs procesados: {self.estadisticas['total']}")
        print(f"   - CIFs válidos: {self.estadisticas['validos']}")
        print(f"   - CIFs inválidos: {self.estadisticas['invalidos']}")
        print(f"   - CIFs completados: {self.estadisticas['completados']}")

        if self.estadisticas['tipos_entidad']:
            print(f"\n🏢 DISTRIBUCIÓN POR TIPOS DE ENTIDAD:")
            for tipo, cantidad in self.estadisticas['tipos_entidad'].items():
                if pd.notna(tipo):
                    print(f"   - {tipo}: {cantidad}")

def main():
    """Función principal para probar el validador"""
    print("🧪 VALIDADOR DE CIF - PRUEBAS")
    print("=" * 40)

    # Ejemplos de CIFs para probar
    cifs_ejemplo = [
        "B12345678",  # CIF válido
        "A1234567",   # CIF de 8 dígitos
        "B1234567",   # CIF a completar
        "X12345678",  # Letra inválida
        "B1234567A",  # Formato incorrecto
        "",           # Vacío
        "B123456789", # Demasiado largo
    ]

    print("🔍 Probando validación de CIFs:")
    for cif in cifs_ejemplo:
        print(f"\nCIF: '{cif}'")

        # Limpiar
        cif_limpio = ValidadorCIF.limpiar_cif(cif)
        print(f"   Limpio: '{cif_limpio}'")

        # Validar formato
        formato_valido, mensaje = ValidadorCIF.validar_formato(cif)
        print(f"   Formato: {formato_valido} - {mensaje}")

        # Validar completo
        if formato_valido:
            completo_valido, mensaje = ValidadorCIF.validar_cif_completo(cif)
            print(f"   Completo: {completo_valido} - {mensaje}")

            # Tipo de entidad
            tipo = ValidadorCIF.obtener_tipo_entidad(cif)
            print(f"   Tipo: {tipo}")

            # Completar si es necesario
            if len(cif_limpio) == 8:
                cif_completado = ValidadorCIF.completar_cif(cif)
                print(f"   Completado: '{cif_completado}'")

    # Procesar archivo si existe
    archivos_empresas = [
        "empresas_encontradas.xlsx",
        "empresas_avanzadas.xlsx",
        "demo_empresas.xlsx"
    ]

    for archivo in archivos_empresas:
        try:
            procesador = ProcesadorCIF()
            df_procesado = procesador.procesar_archivo(archivo, f"cif_validado_{archivo}")
            if df_procesado is not None:
                break
        except FileNotFoundError:
            continue

    print("\n✅ Pruebas completadas")

if __name__ == "__main__":
    main()
