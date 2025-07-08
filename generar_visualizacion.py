import pandas as pd
import glob
import os
from datetime import datetime

def generar_visualizacion():
    """Genera una página HTML de visualización con los datos de empresas"""

    # Buscar el archivo más reciente de detalles de empresas
    archivos = glob.glob('detalles_empresas_*.csv')
    if not archivos:
        print("No se encontraron archivos de detalles de empresas")
        return

    # Obtener el archivo más reciente
    archivo_mas_reciente = max(archivos, key=os.path.getctime)
    print(f"Usando archivo: {archivo_mas_reciente}")

    # Cargar datos
    df = pd.read_csv(archivo_mas_reciente)

    # Limpiar datos
    df = df.fillna('N/A')

    # Asegurar que teléfono y CNAE se muestren sin decimales
    if 'telefono' in df.columns:
        df.loc[:, 'telefono'] = df['telefono'].astype(str).str.split('.').str[0]
    if 'cnae' in df.columns:
        df.loc[:, 'cnae'] = df['cnae'].astype(str).str.split('.').str[0]

    # Obtener estadísticas
    total_empresas = len(df)
    municipios_unicos = df['municipio'].nunique()
    cnaes_unicos = df['cnae'].nunique()

    # Generar HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Empresas de Murcia - Visualización</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .stat-label {{
            color: #7f8c8d;
            margin-top: 5px;
        }}
        .filters {{
            padding: 30px;
            background: white;
            border-bottom: 1px solid #ecf0f1;
        }}
        .filter-group {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .filter-item {{
            display: flex;
            flex-direction: column;
        }}
        .filter-item label {{
            font-weight: bold;
            margin-bottom: 5px;
            color: #2c3e50;
        }}
        .filter-item select, .filter-item input {{
            padding: 10px;
            border: 2px solid #ecf0f1;
            border-radius: 5px;
            font-size: 14px;
        }}
        .filter-item select:focus, .filter-item input:focus {{
            outline: none;
            border-color: #3498db;
        }}
        .table-container {{
            padding: 30px;
            max-height: 600px;
            overflow-y: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        th {{
            background: #34495e;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .export-buttons {{
            padding: 20px 30px;
            text-align: center;
            background: #f8f9fa;
        }}
        .btn {{
            padding: 12px 24px;
            margin: 0 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
        }}
        .btn-primary {{
            background: #3498db;
            color: white;
        }}
        .btn-success {{
            background: #27ae60;
            color: white;
        }}
        .btn:hover {{
            opacity: 0.9;
            transform: translateY(-2px);
            transition: all 0.3s ease;
        }}
        .no-results {{
            text-align: center;
            padding: 50px;
            color: #7f8c8d;
            font-size: 1.2em;
        }}
        .objeto-social {{
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .objeto-social:hover {{
            white-space: normal;
            overflow: visible;
            position: relative;
            z-index: 1000;
            background: white;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            border-radius: 5px;
            padding: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏢 Empresas de Murcia</h1>
            <p>Base de datos completa de empresas registradas en los municipios de Murcia</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_empresas}</div>
                <div class="stat-label">Total Empresas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{municipios_unicos}</div>
                <div class="stat-label">Municipios</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{cnaes_unicos}</div>
                <div class="stat-label">CNAEs Únicos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{df['codigo_postal'].nunique()}</div>
                <div class="stat-label">Códigos Postales</div>
            </div>
        </div>

        <div class="filters">
            <div class="filter-group">
                <div class="filter-item">
                    <label for="municipio-filter">Municipio:</label>
                    <select id="municipio-filter">
                        <option value="">Todos los municipios</option>
                        {''.join([f'<option value="{municipio}">{municipio}</option>' for municipio in sorted(df['municipio'].unique())])}
                    </select>
                </div>
                <div class="filter-item">
                    <label for="cp-filter">Código Postal:</label>
                    <select id="cp-filter">
                        <option value="">Todos los códigos postales</option>
                        {''.join([f'<option value="{cp}">{cp}</option>' for cp in sorted(df['codigo_postal'].unique()) if cp != 'N/A'])}
                    </select>
                </div>
                <div class="filter-item">
                    <label for="cnae-filter">CNAE:</label>
                    <select id="cnae-filter">
                        <option value="">Todos los CNAEs</option>
                        {''.join([f'<option value="{cnae}">{cnae}</option>' for cnae in sorted(df['cnae'].unique()) if cnae != 'N/A'])}
                    </select>
                </div>
                <div class="filter-item">
                    <label for="search-filter">Buscar empresa:</label>
                    <input type="text" id="search-filter" placeholder="Nombre de la empresa...">
                </div>
            </div>
        </div>

        <div class="table-container">
            <table id="empresas-table">
                <thead>
                    <tr>
                        <th>Empresa</th>
                        <th>Municipio</th>
                        <th>C.P.</th>
                        <th>CIF</th>
                        <th>CNAE</th>
                        <th>Teléfono</th>
                        <th>Sitio Web</th>
                        <th>Email</th>
                        <th>Fecha Constitución</th>
                        <th>Objeto Social</th>
                        <th>Detalles</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''
                    <tr>
                        <td>{row['razon_social']}</td>
                        <td>{row['municipio']}</td>
                        <td>{row['codigo_postal']}</td>
                        <td>{row['cif']}</td>
                        <td>{row['cnae']}</td>
                        <td>{row['telefono']}</td>
                        <td>{'<a href="' + row['sitio_web'] + '" target="_blank" class="btn btn-success">🌐 Sitio Web</a>' if row['sitio_web'] != 'N/A' and not row['sitio_web'].startswith('https://www.experian.es') and not row['sitio_web'].startswith('https://www.linkedin.com') else 'N/A'}</td>
                        <td>{row['email'] if pd.notna(row['email']) and row['email'] != 'N/A' else ''}</td>
                        <td>{row['fecha_constitucion']}</td>
                        <td class="objeto-social" title="{row['objeto_social']}">{row['objeto_social'][:100]}{'...' if len(str(row['objeto_social'])) > 100 else ''}</td>
                        <td><a href="{row['url_detalles']}" target="_blank" class="btn btn-primary">Ver</a></td>
                    </tr>
                    ''' for _, row in df.iterrows()])}
                </tbody>
            </table>
        </div>

        <div class="export-buttons">
            <a href="{archivo_mas_reciente}" download class="btn btn-success">📥 Descargar CSV</a>
            <button onclick="exportToExcel()" class="btn btn-primary">📊 Exportar a Excel</button>
        </div>
    </div>

    <script>
        // Datos para el filtrado
        const empresasData = {df.to_dict('records')};

        // Función de filtrado
        function filterTable() {{
            const municipioFilter = document.getElementById('municipio-filter').value;
            const cpFilter = document.getElementById('cp-filter').value;
            const cnaeFilter = document.getElementById('cnae-filter').value;
            const searchFilter = document.getElementById('search-filter').value.toLowerCase();

            const tbody = document.querySelector('#empresas-table tbody');
            const rows = tbody.querySelectorAll('tr');

            let visibleCount = 0;

            rows.forEach(row => {{
                const empresa = row.cells[0].textContent.toLowerCase();
                const municipio = row.cells[1].textContent;
                const cp = row.cells[2].textContent;
                const cnae = row.cells[4].textContent;

                const matchesMunicipio = !municipioFilter || municipio === municipioFilter;
                const matchesCP = !cpFilter || cp === cpFilter;
                const matchesCNAE = !cnaeFilter || cnae === cnaeFilter;
                const matchesSearch = !searchFilter || empresa.includes(searchFilter);

                if (matchesMunicipio && matchesCP && matchesCNAE && matchesSearch) {{
                    row.style.display = '';
                    visibleCount++;
                }} else {{
                    row.style.display = 'none';
                }}
            }});

            // Actualizar contador
            updateStats(visibleCount);
        }}

        function updateStats(visibleCount) {{
            const statNumber = document.querySelector('.stat-card .stat-number');
            if (statNumber) {{
                statNumber.textContent = visibleCount;
            }}
        }}

        // Event listeners
        document.getElementById('municipio-filter').addEventListener('change', filterTable);
        document.getElementById('cp-filter').addEventListener('change', filterTable);
        document.getElementById('cnae-filter').addEventListener('change', filterTable);
        document.getElementById('search-filter').addEventListener('input', filterTable);

        // Función para exportar a Excel (simulada)
        function exportToExcel() {{
            alert('Función de exportación a Excel simulada. Los datos están disponibles en el archivo CSV.');
        }}

        // Inicializar filtros
        filterTable();
    </script>
</body>
</html>
"""

    # Guardar archivo HTML
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_html = f"visualizacion_empresas_{timestamp}.html"

    with open(archivo_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Página de visualización generada: {archivo_html}")
    print(f"📊 Total de empresas: {total_empresas}")
    print(f"🏘️ Municipios: {municipios_unicos}")
    print(f"🏭 CNAEs únicos: {cnaes_unicos}")

    return archivo_html

if __name__ == "__main__":
    generar_visualizacion()
