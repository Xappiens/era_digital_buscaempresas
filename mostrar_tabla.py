import pandas as pd

# Cargar los resultados
df = pd.read_csv('detalles_empresas_20250706_223756.csv')

print('📊 RESULTADOS DE LA PRUEBA CON 10 EMPRESAS')
print('='*80)

# Mostrar tabla principal con datos clave
tabla_principal = df[['razon_social', 'municipio', 'cif', 'cnae', 'fecha_constitucion']].copy()
tabla_principal.columns = ['Empresa', 'Municipio', 'CIF', 'CNAE', 'Fecha Constitución']

print('\n🏢 TABLA PRINCIPAL DE EMPRESAS:')
print(tabla_principal.to_string(index=False))

print('\n📞 INFORMACIÓN DE CONTACTO:')
print('-'*80)

# Tabla de contacto
tabla_contacto = df[['razon_social', 'telefono', 'email', 'sitio_web']].copy()
tabla_contacto.columns = ['Empresa', 'Teléfono', 'Email', 'Sitio Web']

# Limpiar datos para mejor visualización
for col in ['Teléfono', 'Email', 'Sitio Web']:
    tabla_contacto[col] = tabla_contacto[col].fillna('No disponible')
    tabla_contacto[col] = tabla_contacto[col].astype(str).str[:30] + '...' if tabla_contacto[col].astype(str).str.len() > 30 else tabla_contacto[col]

print(tabla_contacto.to_string(index=False))

print('\n📍 DIRECCIONES:')
print('-'*80)

# Tabla de direcciones
tabla_direcciones = df[['razon_social', 'direccion']].copy()
tabla_direcciones.columns = ['Empresa', 'Dirección']

# Limpiar direcciones
tabla_direcciones['Dirección'] = tabla_direcciones['Dirección'].fillna('No disponible')
tabla_direcciones['Dirección'] = tabla_direcciones['Dirección'].astype(str).str[:50] + '...' if tabla_direcciones['Dirección'].astype(str).str.len() > 50 else tabla_direcciones['Dirección']

print(tabla_direcciones.to_string(index=False))

print('\n📋 OBJETO SOCIAL (primeras 80 caracteres):')
print('-'*80)

# Tabla de objeto social
tabla_objeto = df[['razon_social', 'objeto_social']].copy()
tabla_objeto.columns = ['Empresa', 'Objeto Social']

# Limpiar objeto social
tabla_objeto['Objeto Social'] = tabla_objeto['Objeto Social'].fillna('No disponible')
tabla_objeto['Objeto Social'] = tabla_objeto['Objeto Social'].astype(str).str[:80] + '...' if tabla_objeto['Objeto Social'].astype(str).str.len() > 80 else tabla_objeto['Objeto Social']

print(tabla_objeto.to_string(index=False))

print('\n📈 ESTADÍSTICAS DE EXTRACCIÓN:')
print('='*80)

# Estadísticas
campos = ['direccion', 'telefono', 'cif', 'sitio_web', 'email', 'fecha_constitucion', 'cnae', 'objeto_social']
nombres_campos = ['Dirección', 'Teléfono', 'CIF', 'Sitio Web', 'Email', 'Fecha Constitución', 'CNAE', 'Objeto Social']

estadisticas = []
for campo, nombre in zip(campos, nombres_campos):
    empresas_con_campo = df[campo].notna().sum()
    porcentaje = (empresas_con_campo / len(df)) * 100
    estadisticas.append([nombre, empresas_con_campo, f"{porcentaje:.1f}%"])

df_estadisticas = pd.DataFrame(estadisticas, columns=['Campo', 'Empresas con datos', 'Porcentaje'])
print(df_estadisticas.to_string(index=False))
