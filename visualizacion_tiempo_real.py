#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualización en tiempo real de empresas desde SQLite
Genera una página HTML que se actualiza automáticamente
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

def generar_visualizacion_tiempo_real():
    """Genera una página HTML que muestra las empresas en tiempo real"""

    # Conectar a la base de datos
    conn = sqlite3.connect('empresas_murcia.db')

    # Obtener todas las empresas ordenadas por fecha de extracción (más recientes primero)
    query = """
    SELECT
        razon_social,
        municipio,
        codigo_postal,
        direccion,
        telefono,
        cif,
        sitio_web,
        email,
        fecha_constitucion,
        cnae,
        objeto_social,
        url_detalles,
        fecha_extraccion
    FROM empresas_detalles
    ORDER BY fecha_extraccion DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("❌ No hay empresas en la base de datos")
        return None

    # Obtener estadísticas
    total_empresas = len(df)
    municipios_unicos = df['municipio'].nunique()
    cnaes_unicos = df['cnae'].nunique()
    codigos_postales_unicos = df['codigo_postal'].nunique()

    # Contar campos con datos
    empresas_con_direccion = df['direccion'].notna().sum()
    empresas_con_telefono = df['telefono'].notna().sum()
    empresas_con_cif = df['cif'].notna().sum()
    empresas_con_web = df['sitio_web'].notna().sum()
    empresas_con_email = df['email'].notna().sum()
    empresas_con_fecha = df['fecha_constitucion'].notna().sum()
    empresas_con_cnae = df['cnae'].notna().sum()
    empresas_con_objeto = df['objeto_social'].notna().sum()

    # Generar HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏢 Empresas de Murcia - Tiempo Real</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .last-update {{
            text-align: center;
            color: white;
            margin-bottom: 20px;
            font-size: 0.9em;
            opacity: 0.8;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
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
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .filter-group {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
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
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            max-height: 600px;
            overflow-y: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
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
        .btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
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
        .new-company {{
            background: #e8f5e8 !important;
            border-left: 4px solid #27ae60;
        }}
        .export-buttons {{
            text-align: center;
            margin-top: 20px;
        }}
        .export-buttons .btn {{
            margin: 0 10px;
            padding: 12px 24px;
            font-size: 14px;
        }}
        .auto-refresh {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .auto-refresh button {{
            background: #e74c3c;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }}
        .auto-refresh button.active {{
            background: #27ae60;
        }}
        .progress-bar {{
            width: 100%;
            height: 4px;
            background: #ecf0f1;
            border-radius: 2px;
            overflow: hidden;
            margin-top: 10px;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3498db, #27ae60);
            width: 0%;
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏢 Empresas de Murcia - Tiempo Real</h1>
            <p>Base de datos en tiempo real de empresas registradas en los municipios de Murcia</p>
        </div>

        <div class="last-update">
            Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </div>

        <div class="auto-refresh">
            <button id="auto-refresh-btn" onclick="toggleAutoRefresh()">🔄 Auto-refresh: DESACTIVADO</button>
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill"></div>
            </div>
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
                <div class="stat-number">{codigos_postales_unicos}</div>
                <div class="stat-label">Códigos Postales</div>
            </div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{empresas_con_direccion}</div>
                <div class="stat-label">Con Dirección ({empresas_con_direccion/total_empresas*100:.1f}%)</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{empresas_con_telefono}</div>
                <div class="stat-label">Con Teléfono ({empresas_con_telefono/total_empresas*100:.1f}%)</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{empresas_con_cif}</div>
                <div class="stat-label">Con CIF ({empresas_con_cif/total_empresas*100:.1f}%)</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{empresas_con_web}</div>
                <div class="stat-label">Con Sitio Web ({empresas_con_web/total_empresas*100:.1f}%)</div>
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
                        {''.join([f'<option value="{cp}">{cp}</option>' for cp in sorted([c for c in df['codigo_postal'].unique() if pd.notna(c) and c != ''])])}
                    </select>
                </div>
                <div class="filter-item">
                    <label for="cnae-filter">CNAE:</label>
                    <select id="cnae-filter">
                        <option value="">Todos los CNAEs</option>
                        {''.join([f'<option value="{cnae}">{cnae}</option>' for cnae in sorted([c for c in df['cnae'].unique() if pd.notna(c) and c != ''])])}
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
                        <th>Fecha Extracción</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''
                    <tr class="{'new-company' if idx < 5 else ''}">
                        <td>{row['razon_social']}</td>
                        <td>{row['municipio']}</td>
                        <td>{row['codigo_postal'] if pd.notna(row['codigo_postal']) else ''}</td>
                        <td>{row['cif'] if pd.notna(row['cif']) else ''}</td>
                        <td>{row['cnae'] if pd.notna(row['cnae']) else ''}</td>
                        <td>{row['telefono'] if pd.notna(row['telefono']) else ''}</td>
                        <td>{'<a href="' + row['sitio_web'] + '" target="_blank" class="btn btn-success">🌐 Sitio Web</a>' if pd.notna(row['sitio_web']) and row['sitio_web'] != '' else ''}</td>
                        <td>{row['email'] if pd.notna(row['email']) and row['email'] != '' else ''}</td>
                        <td>{row['fecha_constitucion'] if pd.notna(row['fecha_constitucion']) else ''}</td>
                        <td class="objeto-social" title="{row['objeto_social'] if pd.notna(row['objeto_social']) else ''}">{str(row['objeto_social'])[:100] + '...' if pd.notna(row['objeto_social']) and len(str(row['objeto_social'])) > 100 else (row['objeto_social'] if pd.notna(row['objeto_social']) else '')}</td>
                        <td><a href="{row['url_detalles']}" target="_blank" class="btn btn-primary">Ver</a></td>
                        <td>{row['fecha_extraccion'][:19] if pd.notna(row['fecha_extraccion']) else ''}</td>
                    </tr>
                    ''' for idx, (_, row) in enumerate(df.iterrows())])}
                </tbody>
            </table>
        </div>

        <div class="export-buttons">
            <button onclick="exportToCSV()" class="btn btn-success">📥 Exportar a CSV</button>
            <button onclick="exportToExcel()" class="btn btn-primary">📊 Exportar a Excel</button>
        </div>
    </div>

    <script>
        let autoRefreshInterval;
        let autoRefreshActive = false;
        let refreshCountdown = 30;

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
            const statNumbers = document.querySelectorAll('.stat-card .stat-number');
            if (statNumbers.length > 0) {{
                statNumbers[0].textContent = visibleCount;
            }}
        }}

        function toggleAutoRefresh() {{
            const btn = document.getElementById('auto-refresh-btn');
            const progressFill = document.getElementById('progress-fill');

            if (autoRefreshActive) {{
                clearInterval(autoRefreshInterval);
                autoRefreshActive = false;
                btn.textContent = '🔄 Auto-refresh: DESACTIVADO';
                btn.classList.remove('active');
                progressFill.style.width = '0%';
            }} else {{
                autoRefreshActive = true;
                btn.textContent = '🔄 Auto-refresh: ACTIVADO';
                btn.classList.add('active');
                refreshCountdown = 30;
                updateProgress();

                autoRefreshInterval = setInterval(() => {{
                    refreshCountdown--;
                    updateProgress();

                    if (refreshCountdown <= 0) {{
                        location.reload();
                    }}
                }}, 1000);
            }}
        }}

        function updateProgress() {{
            const progressFill = document.getElementById('progress-fill');
            const progress = ((30 - refreshCountdown) / 30) * 100;
            progressFill.style.width = progress + '%';
        }}

        function exportToCSV() {{
            const data = empresasData;
            const headers = ['Empresa', 'Municipio', 'C.P.', 'CIF', 'CNAE', 'Teléfono', 'Sitio Web', 'Email', 'Fecha Constitución', 'Objeto Social', 'URL Detalles'];

            let csvContent = headers.join(',') + '\\n';

            data.forEach(row => {{
                const values = [
                    `"${{row.razon_social}}"`,
                    `"${{row.municipio}}"`,
                    `"${{row.codigo_postal || ''}}"`,
                    `"${{row.cif || ''}}"`,
                    `"${{row.cnae || ''}}"`,
                    `"${{row.telefono || ''}}"`,
                    `"${{row.sitio_web || ''}}"`,
                    `"${{row.email || ''}}"`,
                    `"${{row.fecha_constitucion || ''}}"`,
                    `"${{row.objeto_social || ''}}"`,
                    `"${{row.url_detalles}}"`,
                ];
                csvContent += values.join(',') + '\\n';
            }});

            const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'empresas_murcia_' + new Date().toISOString().slice(0,10) + '.csv';
            link.click();
        }}

        function exportToExcel() {{
            alert('Función de exportación a Excel simulada. Usa la exportación a CSV.');
        }}

        // Event listeners
        document.getElementById('municipio-filter').addEventListener('change', filterTable);
        document.getElementById('cp-filter').addEventListener('change', filterTable);
        document.getElementById('cnae-filter').addEventListener('change', filterTable);
        document.getElementById('search-filter').addEventListener('input', filterTable);

        // Inicializar filtros
        filterTable();

        // Auto-refresh cada 30 segundos si está activado
        setInterval(() => {{
            if (autoRefreshActive) {{
                location.reload();
            }}
        }}, 30000);
    </script>
</body>
</html>
"""

    # Guardar archivo HTML
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_html = f"visualizacion_tiempo_real_{timestamp}.html"

    with open(archivo_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Página de visualización en tiempo real generada: {archivo_html}")
    print(f"📊 Total de empresas en DB: {total_empresas}")
    print(f"🏘️ Municipios: {municipios_unicos}")
    print(f"🏭 CNAEs únicos: {cnaes_unicos}")
    print(f"📅 Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    return archivo_html

if __name__ == "__main__":
    generar_visualizacion_tiempo_real()
