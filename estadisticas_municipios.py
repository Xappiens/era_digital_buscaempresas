import pandas as pd

# Cargar el archivo CSV
df = pd.read_csv('empresas_axesor_20250706_221604.csv')

# Obtener estadísticas por municipio
stats = df['municipio'].value_counts().sort_values(ascending=False)

print('📊 ESTADÍSTICAS DE EMPRESAS POR MUNICIPIO')
print('='*60)
print(f'Total de empresas: {len(df)}')
print(f'Municipios únicos: {df["municipio"].nunique()}')
print()

print('🏢 EMPRESAS POR MUNICIPIO:')
print('-'*60)
for municipio, count in stats.items():
    print(f'{municipio:<30} {count:>5} empresas')

print()
print('📈 RESUMEN:')
print(f'Municipio con más empresas: {stats.index[0]} ({stats.iloc[0]} empresas)')
print(f'Municipio con menos empresas: {stats.index[-1]} ({stats.iloc[-1]} empresas)')
print(f'Promedio por municipio: {stats.mean():.1f} empresas')
print(f'Mediana por municipio: {stats.median():.1f} empresas')

print()
print('🏆 TOP 5 MUNICIPIOS:')
print('-'*30)
for i, (municipio, count) in enumerate(stats.head(5).items(), 1):
    porcentaje = (count / len(df)) * 100
    print(f'{i}. {municipio:<25} {count:>5} empresas ({porcentaje:.1f}%)')
