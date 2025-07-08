#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor web para servir datos de empresas en tiempo real
"""

from flask import Flask, jsonify, render_template_string, send_from_directory
import sqlite3
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

def get_db_connection():
    """Crea una conexión a la base de datos"""
    conn = sqlite3.connect('empresas_murcia.db')
    return conn

@app.route('/')
def index():
    """Página principal con visualización en tiempo real"""
    html_template = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏢 Empresas de Murcia - Tiempo Real</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        .last-update {
            text-align: center;
            color: white;
            margin-bottom: 20px;
            font-size: 0.9em;
            opacity: 0.8;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }
        .stat-label {
            color: #7f8c8d;
            margin-top: 5px;
        }
        .filters {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .filter-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .filter-group:first-child {
            border-bottom: 1px solid #ecf0f1;
            padding-bottom: 15px;
            margin-bottom: 15px;
        }
        .filter-item {
            display: flex;
            flex-direction: column;
        }
        .filter-item label {
            font-weight: bold;
            margin-bottom: 5px;
            color: #2c3e50;
        }
        .filter-item select, .filter-item input {
            padding: 10px;
            border: 2px solid #ecf0f1;
            border-radius: 5px;
            font-size: 14px;
        }
        .filter-item select:focus, .filter-item input:focus {
            outline: none;
            border-color: #3498db;
        }
        .table-container {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            max-height: 600px;
            overflow-y: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background: #34495e;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
        }
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }
        .btn-primary {
            background: #3498db;
            color: white;
        }
        .btn-success {
            background: #27ae60;
            color: white;
        }
        .btn:hover {
            opacity: 0.9;
            transform: translateY(-2px);
        }
        .objeto-social {
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .objeto-social:hover {
            white-space: normal;
            overflow: visible;
            position: relative;
            z-index: 1000;
            background: white;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            border-radius: 5px;
            padding: 10px;
        }
        .new-company {
            background: #e8f5e8 !important;
            border-left: 4px solid #27ae60;
            animation: highlight 2s ease-in-out;
        }
        @keyframes highlight {
            0% { background: #e8f5e8; }
            50% { background: #d4edda; }
            100% { background: #e8f5e8; }
        }
        .export-buttons {
            text-align: center;
            margin-top: 20px;
        }
        .export-buttons .btn {
            margin: 0 10px;
            padding: 12px 24px;
            font-size: 14px;
        }
        .auto-refresh {
            text-align: center;
            margin-bottom: 20px;
        }
        .auto-refresh button {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        .auto-refresh button.active {
            background: #27ae60;
        }
        .progress-bar {
            width: 100%;
            height: 4px;
            background: #ecf0f1;
            border-radius: 2px;
            overflow: hidden;
            margin-top: 10px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3498db, #27ae60);
            width: 0%;
            transition: width 0.3s ease;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏢 Empresas de Murcia - Tiempo Real</h1>
            <p>Base de datos en tiempo real de empresas registradas en los municipios de Murcia</p>
        </div>

        <div class="last-update" id="last-update">
            Última actualización: Cargando...
        </div>

        <div class="auto-refresh">
            <button id="auto-refresh-btn" onclick="toggleAutoRefresh()">🔄 Auto-refresh: ACTIVADO</button>
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill"></div>
            </div>
        </div>

        <div class="stats" id="stats">
            <div class="loading">
                <div class="spinner"></div>
                Cargando estadísticas...
            </div>
        </div>

        <div class="filters">
            <div class="filter-group">
                <div class="filter-item">
                    <label for="municipio-filter">Municipio:</label>
                    <select id="municipio-filter" onchange="filterTable()">
                        <option value="">Todos los municipios</option>
                    </select>
                </div>
                <div class="filter-item">
                    <label for="cp-filter">Código Postal:</label>
                    <select id="cp-filter" onchange="filterTable()">
                        <option value="">Todos los códigos postales</option>
                    </select>
                </div>
                <div class="filter-item">
                    <label for="cnae-filter">CNAE:</label>
                    <select id="cnae-filter" onchange="filterTable()">
                        <option value="">Todos los CNAEs</option>
                    </select>
                </div>
                <div class="filter-item">
                    <label for="search-filter">Buscar empresa:</label>
                    <input type="text" id="search-filter" placeholder="Nombre de la empresa..." oninput="filterTable()">
                </div>
            </div>
            <div class="filter-group">
                <div class="filter-item">
                    <label for="telefono-filter">Con Teléfono:</label>
                    <select id="telefono-filter" onchange="filterTable()">
                        <option value="">Todas las empresas</option>
                        <option value="si">Solo con teléfono</option>
                        <option value="no">Solo sin teléfono</option>
                    </select>
                </div>
                <div class="filter-item">
                    <label for="email-filter">Con Email:</label>
                    <select id="email-filter" onchange="filterTable()">
                        <option value="">Todas las empresas</option>
                        <option value="si">Solo con email</option>
                        <option value="no">Solo sin email</option>
                    </select>
                </div>
                <div class="filter-item">
                    <label for="web-filter">Con Sitio Web:</label>
                    <select id="web-filter" onchange="filterTable()">
                        <option value="">Todas las empresas</option>
                        <option value="si">Solo con sitio web</option>
                        <option value="no">Solo sin sitio web</option>
                    </select>
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
                <tbody id="empresas-tbody">
                    <tr>
                        <td colspan="11" class="loading">
                            <div class="spinner"></div>
                            Cargando empresas...
                        </td>
                    </tr>
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
        let autoRefreshActive = true;
        let refreshCountdown = 30;
        let empresasData = [];
        let lastUpdate = null;

        // Cargar datos iniciales
        loadData();

        function loadData() {
            fetch('/api/empresas')
                .then(response => response.json())
                .then(data => {
                    empresasData = data.empresas;
                    lastUpdate = data.last_update;
                    updateStats(data.stats);
                    updateTable();
                    updateFilters();
                    updateLastUpdate();
                })
                .catch(error => {
                    console.error('Error cargando datos:', error);
                    document.getElementById('empresas-tbody').innerHTML =
                        '<tr><td colspan="11" style="text-align: center; color: red;">Error cargando datos</td></tr>';
                });
        }

        function updateStats(stats) {
            const statsContainer = document.getElementById('stats');
            statsContainer.innerHTML = `
                <div class="stat-card">
                    <div class="stat-number">${stats.total_empresas}</div>
                    <div class="stat-label">Total Empresas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.municipios_unicos}</div>
                    <div class="stat-label">Municipios</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.cnaes_unicos}</div>
                    <div class="stat-label">CNAEs Únicos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.codigos_postales_unicos}</div>
                    <div class="stat-label">Códigos Postales</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.empresas_con_direccion}</div>
                    <div class="stat-label">Con Dirección (${(stats.empresas_con_direccion/stats.total_empresas*100).toFixed(1)}%)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.empresas_con_telefono}</div>
                    <div class="stat-label">Con Teléfono (${(stats.empresas_con_telefono/stats.total_empresas*100).toFixed(1)}%)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.empresas_con_cif}</div>
                    <div class="stat-label">Con CIF (${(stats.empresas_con_cif/stats.total_empresas*100).toFixed(1)}%)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.empresas_con_web}</div>
                    <div class="stat-label">Con Sitio Web (${(stats.empresas_con_web/stats.total_empresas*100).toFixed(1)}%)</div>
                </div>
            `;
        }

        function updateTable() {
            const tbody = document.getElementById('empresas-tbody');
            tbody.innerHTML = empresasData.map((empresa, index) => `
                <tr class="${index < 5 ? 'new-company' : ''}">
                    <td>${empresa.razon_social}</td>
                    <td>${empresa.municipio || ''}</td>
                    <td>${empresa.codigo_postal || ''}</td>
                    <td>${empresa.cif || ''}</td>
                    <td>${empresa.cnae || ''}</td>
                    <td>${empresa.telefono || ''}</td>
                    <td>${empresa.sitio_web ? `<a href="${empresa.sitio_web}" target="_blank" class="btn btn-success">🌐 Sitio Web</a>` : ''}</td>
                    <td>${empresa.email || ''}</td>
                    <td>${empresa.fecha_constitucion || ''}</td>
                    <td class="objeto-social" title="${empresa.objeto_social || ''}">${(empresa.objeto_social || '').substring(0, 100)}${(empresa.objeto_social || '').length > 100 ? '...' : ''}</td>
                    <td><a href="${empresa.url_detalles}" target="_blank" class="btn btn-primary">Ver</a></td>
                    <td>${empresa.fecha_extraccion ? empresa.fecha_extraccion.substring(0, 19) : ''}</td>
                </tr>
            `).join('');
        }

        function updateFilters() {
            const municipios = [...new Set(empresasData.map(e => e.municipio).filter(Boolean))].sort();
            const codigosPostales = [...new Set(empresasData.map(e => e.codigo_postal).filter(Boolean))].sort();
            const cnaes = [...new Set(empresasData.map(e => e.cnae).filter(Boolean))].sort();

            document.getElementById('municipio-filter').innerHTML =
                '<option value="">Todos los municipios</option>' +
                municipios.map(m => `<option value="${m}">${m}</option>`).join('');

            document.getElementById('cp-filter').innerHTML =
                '<option value="">Todos los códigos postales</option>' +
                codigosPostales.map(cp => `<option value="${cp}">${cp}</option>`).join('');

            document.getElementById('cnae-filter').innerHTML =
                '<option value="">Todos los CNAEs</option>' +
                cnaes.map(cnae => `<option value="${cnae}">${cnae}</option>`).join('');
        }

        function updateLastUpdate() {
            document.getElementById('last-update').textContent =
                `Última actualización: ${lastUpdate}`;
        }

        function filterTable() {
            const municipioFilter = document.getElementById('municipio-filter').value;
            const cpFilter = document.getElementById('cp-filter').value;
            const cnaeFilter = document.getElementById('cnae-filter').value;
            const searchFilter = document.getElementById('search-filter').value.toLowerCase();
            const telefonoFilter = document.getElementById('telefono-filter').value;
            const emailFilter = document.getElementById('email-filter').value;
            const webFilter = document.getElementById('web-filter').value;

            const tbody = document.getElementById('empresas-tbody');
            const rows = tbody.querySelectorAll('tr');

            let visibleCount = 0;

            rows.forEach(row => {
                const empresa = row.cells[0].textContent.toLowerCase();
                const municipio = row.cells[1].textContent;
                const cp = row.cells[2].textContent;
                const cnae = row.cells[4].textContent;
                const telefono = row.cells[5].textContent.trim();
                const web = row.cells[6].textContent.trim();
                const email = row.cells[7].textContent.trim();

                const matchesMunicipio = !municipioFilter || municipio === municipioFilter;
                const matchesCP = !cpFilter || cp === cpFilter;
                const matchesCNAE = !cnaeFilter || cnae === cnaeFilter;
                const matchesSearch = !searchFilter || empresa.includes(searchFilter);

                // Filtros de contacto
                const hasTelefono = telefono !== '';
                const hasWeb = web !== '';
                const hasEmail = email !== '';

                const matchesTelefono = !telefonoFilter ||
                    (telefonoFilter === 'si' && hasTelefono) ||
                    (telefonoFilter === 'no' && !hasTelefono);
                const matchesEmail = !emailFilter ||
                    (emailFilter === 'si' && hasEmail) ||
                    (emailFilter === 'no' && !hasEmail);
                const matchesWeb = !webFilter ||
                    (webFilter === 'si' && hasWeb) ||
                    (webFilter === 'no' && !hasWeb);

                if (matchesMunicipio && matchesCP && matchesCNAE && matchesSearch &&
                    matchesTelefono && matchesEmail && matchesWeb) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            });

            // Actualizar contador
            const statNumbers = document.querySelectorAll('.stat-card .stat-number');
            if (statNumbers.length > 0) {
                statNumbers[0].textContent = visibleCount;
            }
        }

        function toggleAutoRefresh() {
            const btn = document.getElementById('auto-refresh-btn');
            const progressFill = document.getElementById('progress-fill');

            if (autoRefreshActive) {
                clearInterval(autoRefreshInterval);
                autoRefreshActive = false;
                btn.textContent = '🔄 Auto-refresh: DESACTIVADO';
                btn.classList.remove('active');
                progressFill.style.width = '0%';
            } else {
                autoRefreshActive = true;
                btn.textContent = '🔄 Auto-refresh: ACTIVADO';
                btn.classList.add('active');
                refreshCountdown = 30;
                updateProgress();

                autoRefreshInterval = setInterval(() => {
                    refreshCountdown--;
                    updateProgress();

                    if (refreshCountdown <= 0) {
                        loadData();
                        refreshCountdown = 30;
                    }
                }, 1000);
            }
        }

        function updateProgress() {
            const progressFill = document.getElementById('progress-fill');
            const progress = ((30 - refreshCountdown) / 30) * 100;
            progressFill.style.width = progress + '%';
        }

        function exportToCSV() {
            const headers = ['Empresa', 'Municipio', 'C.P.', 'CIF', 'CNAE', 'Teléfono', 'Sitio Web', 'Email', 'Fecha Constitución', 'Objeto Social', 'URL Detalles'];

            let csvContent = headers.join(',') + '\\n';

            empresasData.forEach(row => {
                const values = [
                    `"${row.razon_social}"`,
                    `"${row.municipio || ''}"`,
                    `"${row.codigo_postal || ''}"`,
                    `"${row.cif || ''}"`,
                    `"${row.cnae || ''}"`,
                    `"${row.telefono || ''}"`,
                    `"${row.sitio_web || ''}"`,
                    `"${row.email || ''}"`,
                    `"${row.fecha_constitucion || ''}"`,
                    `"${row.objeto_social || ''}"`,
                    `"${row.url_detalles}"`,
                ];
                csvContent += values.join(',') + '\\n';
            });

            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'empresas_murcia_' + new Date().toISOString().slice(0,10) + '.csv';
            link.click();
        }

        function exportToExcel() {
            alert('Función de exportación a Excel simulada. Usa la exportación a CSV.');
        }

        // Iniciar auto-refresh
        toggleAutoRefresh();
    </script>
</body>
</html>
    """
    return html_template

@app.route('/api/empresas')
def api_empresas():
    """API para obtener datos de empresas"""
    try:
        # Conectar directamente a la base de datos
        conn = sqlite3.connect('empresas_murcia.db')

        # Obtener empresas
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

        # Calcular estadísticas
        stats = {
            'total_empresas': int(len(df)),
            'municipios_unicos': int(df['municipio'].nunique()),
            'cnaes_unicos': int(df['cnae'].nunique()),
            'codigos_postales_unicos': int(df['codigo_postal'].nunique()),
            'empresas_con_direccion': int(df['direccion'].notna().sum()),
            'empresas_con_telefono': int(df['telefono'].notna().sum()),
            'empresas_con_cif': int(df['cif'].notna().sum()),
            'empresas_con_web': int(df['sitio_web'].notna().sum()),
            'empresas_con_email': int(df['email'].notna().sum()),
            'empresas_con_fecha': int(df['fecha_constitucion'].notna().sum()),
            'empresas_con_cnae': int(df['cnae'].notna().sum()),
            'empresas_con_objeto': int(df['objeto_social'].notna().sum())
        }

        return jsonify({
            'empresas': df.to_dict('records'),
            'stats': stats,
            'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        })

    except Exception as e:
        print(f"Error en API: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🌐 Iniciando servidor web en http://localhost:5000")
    print("📊 La página se actualizará automáticamente cada 30 segundos")
    print("🔄 Para detener el servidor, presiona Ctrl+C")
    app.run(debug=True, host='0.0.0.0', port=5000)
