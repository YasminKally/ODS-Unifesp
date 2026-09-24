import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('_mpl-gallery-nogrid')

df = pd.read_csv("./Open_Alex_UNIFESP_enriquecido.csv")

colunaods = "SDG"

ods = {
    'No poverty': 'ODS 1',
    'Zero hunger': 'ODS 2',
    'Good health and well-being': 'ODS 3',
    'Quality Education': 'ODS 4',
    'Gender equality': 'ODS 5',
    'Clean water and sanitation': 'ODS 6',
    'Affordable and clean energy': 'ODS 7',
    'Decent work and economic growth': 'ODS 8',
    'Industry, innovation and infrastructure': 'ODS 9',
    'Reduced inequalities': 'ODS 10',
    'Sustainable cities and communities': 'ODS 11',
    'Responsible consumption and production': 'ODS 12',
    'Climate action': 'ODS 13',
    'Life below water': 'ODS 14',
    'Life in Land': 'ODS 15',
    'Peace, Justice and strong institutions': 'ODS 16',
    'Partnerships for the goals': 'ODS 17',
}

contagem = (
    df[colunaods]
    .dropna()
    .astype(str)
    .str.split(r'[.;|\n]')
    .explode()
    .map(ods.get)
    .str.strip()
    .value_counts()
    .reset_index()
)

contagem.columns = ['ODS', 'Total de Artigos']
total_artigos = len(df)
artigos_classificados = df[colunaods].notnull().sum()
artigos_nao_classificados = df[colunaods].isnull().sum()

count = contagem['Total de Artigos']
labels = contagem['ODS']

fig, ax = plt.subplots()

pie = ax.pie(count, radius=3, center=(4, 4), wedgeprops={"linewidth": 1, "edgecolor": "white"}, frame=True)
ax.pie_label(pie, labels, distance=1.1)
ax.pie_label(pie, '{frac:.1%}')
ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
       ylim=(0, 8), yticks=np.arange(1, 8))

plt.show()

print(contagem)
print("total de artigos: %u" % total_artigos)
print("artigos classificados: %u" % artigos_classificados)
print("artigos não classificados: %u" % artigos_nao_classificados)