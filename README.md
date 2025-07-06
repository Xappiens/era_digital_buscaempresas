# 🏢 Scraper de Empresas de Murcia - Axesor

## 📋 Descripción

Este proyecto contiene un scraper web desarrollado en Python para extraer información de empresas registradas en los municipios de Murcia desde el directorio de Axesor.

## 🎯 Objetivo

Extraer datos básicos de empresas (razón social, municipio, fuente y enlace a detalles) de todos los municipios de Murcia disponibles en Axesor.

## 📊 Resultados Obtenidos

- **Total de empresas extraídas**: 14,043 empresas únicas
- **Municipios procesados**: 16 municipios
- **Cobertura**: 100% de municipios disponibles en Axesor

### 🏆 Top 5 Municipios por número de empresas:

1. **Lorca**: 6,998 empresas (49.8%)
2. **Caravaca de la Cruz**: 2,156 empresas (15.4%)
3. **Bullas**: 1,057 empresas (7.5%)
4. **Cehegín**: 974 empresas (6.9%)
5. **Abarán**: 707 empresas (5.0%)

## 🛠️ Tecnologías Utilizadas

- **Python 3.x**
- **BeautifulSoup4** - Parsing HTML
- **Requests** - Peticiones HTTP
- **Pandas** - Manipulación de datos
- **OpenPyXL** - Generación de archivos Excel

## 📁 Estructura del Proyecto

```
era_digital_buscaempresas/
├── scraper_axesor.py          # Scraper principal
├── estadisticas_municipios.py # Script de estadísticas
├── requirements.txt           # Dependencias
├── municipios_pedanias_codigos_postales_corregidos.csv  # Datos de municipios
├── README.md                  # Documentación
└── .gitignore                # Archivos a ignorar
```

## 🚀 Instalación

1. **Clonar el repositorio:**

   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd era_digital_buscaempresas
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Uso

### Ejecutar el scraper completo:

```bash
python scraper_axesor.py
```

### Ver estadísticas de municipios:

```bash
python estadisticas_municipios.py
```

## 📈 Datos Extraídos

Para cada empresa se extrae:

- **Razón Social**: Nombre de la empresa
- **Municipio**: Localidad donde está registrada
- **Fuente**: Axesor
- **Enlace**: URL a la página de detalles de la empresa

## 📊 Municipios Procesados

| Municipio                 | Empresas | % del Total |
| ------------------------- | -------- | ----------- |
| Lorca                     | 6,998    | 49.8%       |
| Caravaca de la Cruz       | 2,156    | 15.4%       |
| Bullas                    | 1,057    | 7.5%        |
| Cehegín                   | 974      | 6.9%        |
| Abarán                    | 707      | 5.0%        |
| Calasparra                | 691      | 4.9%        |
| Moratalla                 | 498      | 3.5%        |
| Abanilla                  | 421      | 3.0%        |
| Pliego                    | 173      | 1.2%        |
| Villanueva del Río Segura | 100      | 0.7%        |
| Campos del Río            | 100      | 0.7%        |
| Albudeite                 | 47       | 0.3%        |
| Aledo                     | 41       | 0.3%        |
| Ulea                      | 39       | 0.3%        |
| Ricote                    | 32       | 0.2%        |
| Ojós                      | 9        | 0.1%        |

## 🔧 Características del Scraper

- **Paginación automática**: Recorre todas las páginas de cada municipio
- **Detección robusta**: Maneja diferentes formatos de enlaces
- **Eliminación de duplicados**: Basada en razón social
- **Logging detallado**: Seguimiento completo del proceso
- **Exportación múltiple**: Excel y CSV
- **Respeto a robots.txt**: Delays entre peticiones

## 📝 Archivos de Salida

El scraper genera:

- `empresas_axesor_YYYYMMDD_HHMMSS.xlsx` - Archivo Excel con todos los datos
- `empresas_axesor_YYYYMMDD_HHMMSS.csv` - Archivo CSV con todos los datos

## ⚠️ Consideraciones

- El scraper incluye delays entre peticiones para respetar el servidor
- Los datos se extraen únicamente de Axesor
- Se recomienda usar los datos de manera responsable y respetando los términos de uso

## 📞 Contacto

Para consultas sobre el proyecto, contactar con el desarrollador.

---

**Fecha de última actualización**: Julio 2025
**Versión**: 1.0
