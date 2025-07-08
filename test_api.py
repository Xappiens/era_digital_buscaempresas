#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la API del servidor web
"""

import sqlite3
import pandas as pd
from datetime import datetime

def test_api():
    """Prueba la funcionalidad de la API"""
    try:
        # Conectar a la base de datos
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
        LIMIT 5
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        print("✅ Query ejecutado correctamente")
        print(f"📊 Empresas obtenidas: {len(df)}")
        print(f"📋 Columnas: {df.columns.tolist()}")

        if not df.empty:
            print(f"🏢 Primera empresa: {df.iloc[0]['razon_social']}")

        # Calcular estadísticas
        stats = {
            'total_empresas': len(df),
            'municipios_unicos': df['municipio'].nunique(),
            'cnaes_unicos': df['cnae'].nunique(),
            'codigos_postales_unicos': df['codigo_postal'].nunique(),
            'empresas_con_direccion': df['direccion'].notna().sum(),
            'empresas_con_telefono': df['telefono'].notna().sum(),
            'empresas_con_cif': df['cif'].notna().sum(),
            'empresas_con_web': df['sitio_web'].notna().sum(),
            'empresas_con_email': df['email'].notna().sum(),
            'empresas_con_fecha': df['fecha_constitucion'].notna().sum(),
            'empresas_con_cnae': df['cnae'].notna().sum(),
            'empresas_con_objeto': df['objeto_social'].notna().sum()
        }

        print("📊 Estadísticas calculadas correctamente")
        print(f"   Total empresas: {stats['total_empresas']}")
        print(f"   Municipios: {stats['municipios_unicos']}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_api()
