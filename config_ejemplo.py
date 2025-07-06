# Configuración del scraper de empresas
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

# Configuración de timeouts (segundos)
TIMEOUT_REQUEST = 15
TIMEOUT_PAGINA = 20

# Configuración de User-Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Configuración de logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'scraper.log'

# Configuración de exportación
EXPORTAR_EXCEL = True
EXPORTAR_CSV = True
INCLUIR_ESTADISTICAS = True
