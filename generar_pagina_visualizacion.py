#!/usr/bin/env python3
"""
Script para generar una página web interactiva para visualizar y filtrar datos de empresas
"""

import pandas as pd
import json
import os
from datetime import datetime

def generar_pagina_visualizacion(archivo_csv):
    """Genera una página HTML interactiva para visualizar los datos de empresas"""

    # Cargar datos
    try:
        df = pd.read_csv(archivo_csv)
        print(f"✅ Datos cargados: {len(df)} empresas")
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        return None

    # Preparar datos para JavaScript
    empresas_data = []
    for _, row in df.iterrows():
        empresa = {
            'razon_social': str(row.get('razon_social', '')),
            'municipio': str(row.get('municipio', '')),
            'codigo_postal': str(row.get('codigo_postal', '')) if pd.notna(row.get('codigo_postal')) else '',
            'cif': str(row.get('cif', '')) if pd.notna(row.get('cif')) else '',
            'direccion': str(row.get('direccion', '')) if pd.notna(row.get('direccion')) else '',
            'telefono': str(row.get('telefono', '')) if pd.notna(row.get('telefono')) else '',
            'email': str(row.get('email', '')) if pd.notna(row.get('email')) else '',
            'sitio_web': str(row.get('sitio_web', '')) if pd.notna(row.get('sitio_web')) else '',
            'fecha_constitucion': str(row.get('fecha_constitucion', '')) if pd.notna(row.get('fecha_constitucion')) else '',
            'cnae': str(row.get('cnae', '')) if pd.notna(row.get('cnae')) else '',
            'objeto_social': str(row.get('objeto_social', '')) if pd.notna(row.get('objeto_social')) else '',
            'url_detalles': str(row.get('url_detalles', '')) if pd.notna(row.get('url_detalles')) else ''
        }
        empresas_data.append(empresa)

    # Obtener valores únicos para los filtros
    municipios = sorted(list(set([emp['municipio'] for emp in empresas_data if emp['municipio']])))
    codigos_postales = sorted(list(set([emp['codigo_postal'] for emp in empresas_data if emp['codigo_postal']])))
    cnaes = sorted(list(set([emp['cnae'] for emp in empresas_data if emp['cnae']])))

    # Generar HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualizador de Empresas - Región de Murcia</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
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
            padding: 20px;
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

        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}

        .filters {{
            background: #f8f9fa;
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
        }}

        .filters-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .filter-group {{
            display: flex;
            flex-direction: column;
        }}

        .filter-group label {{
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
        }}

        .filter-group select, .filter-group input {{
            padding: 10px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }}

        .filter-group select:focus, .filter-group input:focus {{
            outline: none;
            border-color: #3498db;
        }}

        .filter-actions {{
            display: flex;
            gap: 15px;
            justify-content: center;
        }}

        .btn {{
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }}

        .btn-primary {{
            background: #3498db;
            color: white;
        }}

        .btn-primary:hover {{
            background: #2980b9;
            transform: translateY(-2px);
        }}

        .btn-secondary {{
            background: #95a5a6;
            color: white;
        }}

        .btn-secondary:hover {{
            background: #7f8c8d;
        }}

        .stats {{
            background: #e8f4fd;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }}

        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 5px;
        }}

        .table-container {{
            padding: 25px;
            max-height: 600px;
            overflow-y: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}

        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}

        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
        }}

        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}

        .badge-info {{
            background: #d1ecf1;
            color: #0c5460;
        }}

        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}

        .link {{
            color: #3498db;
            text-decoration: none;
        }}

        .link:hover {{
            text-decoration: underline;
        }}

        .empty {{
            color: #95a5a6;
            font-style: italic;
        }}

        .loading {{
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }}

        @media (max-width: 768px) {{
            .filters-grid {{
                grid-template-columns: 1fr;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}

            .table-container {{
                overflow-x: auto;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-building"></i> Visualizador de Empresas</h1>
            <p>Región de Murcia - Datos extraídos de Axesor</p>
        </div>

        <div class="filters">
            <div class="filters-grid">
                <div class="filter-group">
                    <label for="municipio-filter"><i class="fas fa-map-marker-alt"></i> Municipio</label>
                    <select id="municipio-filter">
                        <option value="">Todos los municipios</option>
                        {''.join([f'<option value="{municipio}">{municipio}</option>' for municipio in municipios])}
                    </select>
                </div>

                <div class="filter-group">
                    <label for="cp-filter"><i class="fas fa-mail-bulk"></i> Código Postal</label>
                    <select id="cp-filter">
                        <option value="">Todos los códigos postales</option>
                        {''.join([f'<option value="{cp}">{cp}</option>' for cp in codigos_postales])}
                    </select>
                </div>

                <div class="filter-group">
                    <label for="cnae-filter"><i class="fas fa-industry"></i> CNAE</label>
                    <select id="cnae-filter">
                        <option value="">Todos los CNAE</option>
                        {''.join([f'<option value="{cnae}">{cnae}</option>' for cnae in cnaes])}
                    </select>
                </div>

                <div class="filter-group">
                    <label for="fecha-filter"><i class="fas fa-calendar"></i> Año de Constitución</label>
                    <input type="number" id="fecha-filter" placeholder="Ej: 2020" min="1900" max="2030">
                </div>
            </div>

            <div class="filter-actions">
                <button class="btn btn-primary" onclick="aplicarFiltros()">
                    <i class="fas fa-filter"></i> Aplicar Filtros
                </button>
                <button class="btn btn-secondary" onclick="limpiarFiltros()">
                    <i class="fas fa-times"></i> Limpiar Filtros
                </button>
                <button class="btn btn-secondary" onclick="exportarCSV()">
                    <i class="fas fa-download"></i> Exportar CSV
                </button>
            </div>
        </div>

        <div class="stats">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" id="total-empresas">0</div>
                    <div class="stat-label">Total Empresas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="empresas-filtradas">0</div>
                    <div class="stat-label">Empresas Filtradas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="con-cif">0</div>
                    <div class="stat-label">Con CIF</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="con-email">0</div>
                    <div class="stat-label">Con Email</div>
                </div>
            </div>
        </div>

        <div class="table-container">
            <table id="empresas-table">
                <thead>
                    <tr>
                        <th>Razón Social</th>
                        <th>Municipio</th>
                        <th>C.P.</th>
                        <th>CIF</th>
                        <th>Teléfono</th>
                        <th>Email</th>
                        <th>CNAE</th>
                        <th>Fecha Constitución</th>
                        <th>Enlace</th>
                    </tr>
                </thead>
                <tbody id="empresas-tbody">
                    <tr>
                        <td colspan="9" class="loading">
                            <i class="fas fa-spinner fa-spin"></i> Cargando datos...
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Datos de las empresas
        const empresas = {json.dumps(empresas_data, ensure_ascii=False)};
        let empresasFiltradas = [...empresas];

        // Inicializar la página
        document.addEventListener('DOMContentLoaded', function() {{
            mostrarEmpresas(empresas);
            actualizarEstadisticas(empresas);
        }});

        function aplicarFiltros() {{
            const municipio = document.getElementById('municipio-filter').value;
            const codigoPostal = document.getElementById('cp-filter').value;
            const cnae = document.getElementById('cnae-filter').value;
            const fecha = document.getElementById('fecha-filter').value;

            empresasFiltradas = empresas.filter(empresa => {{
                // Filtro por municipio
                if (municipio && empresa.municipio !== municipio) return false;

                // Filtro por código postal
                if (codigoPostal && empresa.codigo_postal !== codigoPostal) return false;

                // Filtro por CNAE
                if (cnae && empresa.cnae !== cnae) return false;

                // Filtro por año de constitución
                if (fecha && empresa.fecha_constitucion) {{
                    const añoEmpresa = empresa.fecha_constitucion.split('/').pop();
                    if (añoEmpresa !== fecha) return false;
                }}

                return true;
            }});

            mostrarEmpresas(empresasFiltradas);
            actualizarEstadisticas(empresasFiltradas);
        }}

        function limpiarFiltros() {{
            document.getElementById('municipio-filter').value = '';
            document.getElementById('cp-filter').value = '';
            document.getElementById('cnae-filter').value = '';
            document.getElementById('fecha-filter').value = '';

            empresasFiltradas = [...empresas];
            mostrarEmpresas(empresasFiltradas);
            actualizarEstadisticas(empresasFiltradas);
        }}

        function mostrarEmpresas(empresasAMostrar) {{
            const tbody = document.getElementById('empresas-tbody');

            if (empresasAMostrar.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="9" class="loading">No se encontraron empresas con los filtros aplicados</td></tr>';
                return;
            }}

            tbody.innerHTML = empresasAMostrar.map(empresa => {{
                return `
                    <tr>
                        <td><strong>${{empresa.razon_social}}</strong></td>
                        <td><span class="badge badge-info">${{empresa.municipio || 'N/A'}}</span></td>
                        <td><span class="badge badge-success">${{empresa.codigo_postal || 'N/A'}}</span></td>
                        <td>${{empresa.cif || '<span class="empty">No disponible</span>'}}</td>
                        <td>${{empresa.telefono || '<span class="empty">No disponible</span>'}}</td>
                        <td>${{empresa.email || '<span class="empty">No disponible</span>'}}</td>
                        <td><span class="badge badge-warning">${{empresa.cnae || 'N/A'}}</span></td>
                        <td>${{empresa.fecha_constitucion || '<span class="empty">No disponible</span>'}}</td>
                        <td>${{empresa.url_detalles ? `<a href="${{empresa.url_detalles}}" target="_blank" class="link"><i class="fas fa-external-link-alt"></i> Ver</a>` : '<span class="empty">No disponible</span>'}}</td>
                    </tr>
                `;
            }}).join('');
        }}

        function actualizarEstadisticas(empresasAMostrar) {{
            document.getElementById('total-empresas').textContent = empresas.length;
            document.getElementById('empresas-filtradas').textContent = empresasAMostrar.length;
            document.getElementById('con-cif').textContent = empresasAMostrar.filter(e => e.cif).length;
            document.getElementById('con-email').textContent = empresasAMostrar.filter(e => e.email).length;
        }}

        function exportarCSV() {{
            const headers = ['Razón Social', 'Municipio', 'Código Postal', 'CIF', 'Dirección', 'Teléfono', 'Email', 'Sitio Web', 'Fecha Constitución', 'CNAE', 'Objeto Social', 'URL Detalles'];
            const csvContent = [
                headers.join(','),
                ...empresasFiltradas.map(empresa => [
                    `"${{empresa.razon_social}}"`,
                    `"${{empresa.municipio}}"`,
                    `"${{empresa.codigo_postal}}"`,
                    `"${{empresa.cif}}"`,
                    `"${{empresa.direccion}}"`,
                    `"${{empresa.telefono}}"`,
                    `"${{empresa.email}}"`,
                    `"${{empresa.sitio_web}}"`,
                    `"${{empresa.fecha_constitucion}}"`,
                    `"${{empresa.cnae}}"`,
                    `"${{empresa.objeto_social}}"`,
                    `"${{empresa.url_detalles}}"`
                ].join(','))
            ].join('\\n');

            const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', `empresas_filtradas_${{new Date().toISOString().split('T')[0]}}.csv`);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }}
    </script>
</body>
</html>
"""

    # Guardar archivo HTML
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"visualizador_empresas_{timestamp}.html"

    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Página generada: {nombre_archivo}")
    print(f"📊 Total de empresas: {len(empresas_data)}")
    print(f"🏘️ Municipios: {len(municipios)}")
    print(f"📮 Códigos postales: {len(codigos_postales)}")
    print(f"🏭 CNAEs: {len(cnaes)}")

    return nombre_archivo

def main():
    """Función principal"""
    # Buscar el archivo CSV más reciente
    archivos_csv = [f for f in os.listdir('.') if f.startswith('detalles_empresas_') and f.endswith('.csv')]

    if not archivos_csv:
        print("❌ No se encontraron archivos CSV de detalles de empresas")
        print("💡 Ejecuta primero el scraper de detalles: py scraper_detalles_empresas.py")
        return

    # Usar el archivo más reciente
    archivo_mas_reciente = max(archivos_csv, key=os.path.getctime)
    print(f"📁 Usando archivo: {archivo_mas_reciente}")

    # Generar página
    archivo_html = generar_pagina_visualizacion(archivo_mas_reciente)

    if archivo_html:
        print(f"\n🎉 ¡Página generada exitosamente!")
        print(f"📂 Archivo: {archivo_html}")
        print(f"🌐 Abre el archivo en tu navegador para visualizar los datos")
        print(f"🔍 Funcionalidades disponibles:")
        print(f"   • Filtrado por municipio, código postal, CNAE y fecha")
        print(f"   • Estadísticas en tiempo real")
        print(f"   • Exportación a CSV")
        print(f"   • Enlaces directos a Axesor")

if __name__ == "__main__":
    main()
