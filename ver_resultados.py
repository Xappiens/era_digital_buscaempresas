import pandas as pd

# Cargar los resultados
df = pd.read_csv('detalles_empresas_20250706_223756.csv')

print('📊 RESULTADOS DE LA PRUEBA CON 10 EMPRESAS')
print('='*60)
print(f'Total procesadas: {len(df)}')

print('\n🏢 PRIMERAS 3 EMPRESAS CON SUS DATOS:')
print('-'*60)

for i, row in df.head(3).iterrows():
    print(f'\n{i+1}. {row["razon_social"]}')
    print(f'   Municipio: {row["municipio"]}')
    print(f'   CIF: {row["cif"]}')
    print(f'   Dirección: {row["direccion"]}')
    print(f'   Teléfono: {row["telefono"]}')
    print(f'   Email: {row["email"]}')
    print(f'   Sitio web: {row["sitio_web"]}')
    print(f'   CNAE: {row["cnae"]}')
    print(f'   Fecha constitución: {row["fecha_constitucion"]}')

    objeto_social = str(row["objeto_social"])
    if len(objeto_social) > 100:
        print(f'   Objeto social: {objeto_social[:100]}...')
    else:
        print(f'   Objeto social: {objeto_social}')

print('\n📈 ESTADÍSTICAS DETALLADAS:')
print('-'*30)
campos = ['direccion', 'telefono', 'cif', 'sitio_web', 'email', 'fecha_constitucion', 'cnae', 'objeto_social']

for campo in campos:
    empresas_con_campo = df[campo].notna().sum()
    porcentaje = (empresas_con_campo / len(df)) * 100
    print(f'{campo}: {empresas_con_campo}/10 ({porcentaje:.1f}%)')
