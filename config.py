# Configuración del scraper de empresas
import os
import re
from datetime import datetime

class Config:
    # Configuración de archivos
    ARCHIVO_CSV_ENTRADA = "municipios_pedanias_codigos_postales_corregidos.csv"
    ARCHIVO_SALIDA_EXCEL = f"empresas_encontradas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    ARCHIVO_SALIDA_CSV = f"empresas_encontradas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    ARCHIVO_LOG = "scraper.log"

    # Configuración de búsqueda
    MAX_CODIGOS_POSTALES = None  # None para procesar todos, número para limitar
    MAX_PAGINAS_GOOGLE = 3
    MAX_PAGINAS_OTRAS_FUENTES = 2

    # Configuración de pausas (en segundos)
    PAUSA_ENTRE_CODIGOS = (3, 7)  # (mínimo, máximo)
    PAUSA_ENTRE_PAGINAS = (2, 5)
    PAUSA_ENTRE_REQUESTS = (1, 3)

    # Configuración de timeouts
    TIMEOUT_REQUEST = 15
    TIMEOUT_PAGINA = 20

    # Configuración de User Agents
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]

    # Fuentes de datos habilitadas
    FUENTES_HABILITADAS = {
        'google': True,
        'paginas_amarillas': True,
        'einforma': True,
        'axesor': True,
        'infoempresas': True,
        'redes_sociales': False  # Deshabilitado por defecto
    }

    # Queries de búsqueda personalizadas
    QUERIES_GOOGLE = [
        "empresas código postal {codigo_postal} Murcia",
        "directorio empresas {codigo_postal}",
        "empresas ubicadas {codigo_postal}",
        "comercios {codigo_postal} Murcia",
        "negocios {codigo_postal} Región de Murcia",
        "CIF empresas {codigo_postal} Murcia",
        "empresas con CIF {codigo_postal}"
    ]

    # Patrones de regex para extracción de datos
    PATRONES_EMAIL = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    ]

    PATRONES_TELEFONO = [
        r'(\+34\s?)?[6-9]\d{8}',
        r'(\+34\s?)?9\d{8}',
        r'(\+34\s?)?8\d{8}'
    ]

    # Patrones para CIF (Código de Identificación Fiscal)
    PATRONES_CIF = [
        r'\b[A-Z]\d{8}\b',  # CIF estándar: 1 letra + 8 dígitos
        r'\b[A-Z]\d{7}[A-Z]\b',  # CIF con letra al final
        r'\b[A-Z]\d{8}[A-Z]\b',  # CIF con letra al final (9 caracteres)
        r'CIF[:\s]*([A-Z]\d{7,8}[A-Z]?)',  # CIF después de "CIF:"
        r'Código[:\s]*([A-Z]\d{7,8}[A-Z]?)',  # CIF después de "Código:"
        r'Fiscal[:\s]*([A-Z]\d{7,8}[A-Z]?)',  # CIF después de "Fiscal:"
        r'Identificación[:\s]*([A-Z]\d{7,8}[A-Z]?)',  # CIF después de "Identificación:"
        r'([A-Z]\d{7,8}[A-Z]?)\s*\(CIF\)',  # CIF seguido de (CIF)
        r'([A-Z]\d{7,8}[A-Z]?)\s*CIF',  # CIF seguido de CIF
    ]

    PATRONES_CNAE = [
        r'CNAE[:\s]*(\d{4})',
        r'Actividad[:\s]*(\d{4})',
        r'Código[:\s]*(\d{4})',
        r'CNAE\s*(\d{4})'
    ]

    # Configuración de logging
    NIVEL_LOG = 'INFO'
    FORMATO_LOG = '%(asctime)s - %(levelname)s - %(message)s'

    # Configuración de proxies (opcional)
    USAR_PROXIES = False
    PROXIES = {
        'http': None,
        'https': None
    }

    # Configuración de retry
    MAX_REINTENTOS = 3
    TIEMPO_ESPERA_REINTENTO = 5

    # Configuración de filtros
    FILTRAR_DUPLICADOS = True
    MIN_LONGITUD_NOMBRE = 3
    EXCLUIR_PALABRAS = ['página', 'error', 'not found', '404']

    # Configuración de deduplicación
    DEDUPLICACION_PRIORIDAD = ['cif', 'razon_social', 'direccion']  # Orden de prioridad para deduplicación

    @classmethod
    def obtener_user_agent(cls):
        """Obtiene un User Agent aleatorio"""
        import random
        return random.choice(cls.USER_AGENTS)

    @classmethod
    def obtener_pausa(cls, tipo='entre_codigos'):
        """Obtiene una pausa aleatoria según el tipo"""
        import random
        if tipo == 'entre_codigos':
            return random.uniform(*cls.PAUSA_ENTRE_CODIGOS)
        elif tipo == 'entre_paginas':
            return random.uniform(*cls.PAUSA_ENTRE_PAGINAS)
        elif tipo == 'entre_requests':
            return random.uniform(*cls.PAUSA_ENTRE_REQUESTS)
        else:
            return random.uniform(1, 3)

    @classmethod
    def validar_cif(cls, cif):
        """Valida si un CIF tiene el formato correcto"""
        if not cif:
            return False

        # Limpiar espacios y caracteres especiales
        cif_limpio = cif.strip().upper()

        # Verificar formato básico
        if not re.match(r'^[A-Z]\d{7,8}[A-Z]?$', cif_limpio):
            return False

        return True
