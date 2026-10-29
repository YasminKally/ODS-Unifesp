import os, sys, subprocess
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

df = pd.read_csv(
    "./Open_Alex_UNIFESP_enriquecido.csv",
    sep=",", engine="python", on_bad_lines="skip", encoding="utf-8",
)
print("Linhas lidas:", len(df))
print("Colunas:", df.columns.tolist())

colunaods = "SDG"
if colunaods not in df.columns:
    raise SystemExit("Coluna SDG nao encontrada.")

ods = {
    'no poverty': 'ODS 1', 'zero hunger': 'ODS 2',
    'good health and well-being': 'ODS 3', 'quality education': 'ODS 4',
    'gender equality': 'ODS 5', 'clean water and sanitation': 'ODS 6',
    'affordable and clean energy': 'ODS 7',
    'decent work and economic growth': 'ODS 8',
    'industry, innovation and infrastructure': 'ODS 9',
    'reduced inequalities': 'ODS 10',
    'sustainable cities and communities': 'ODS 11',
    'responsible consumption and production': 'ODS 12',
    'climate action': 'ODS 13', 'life below water': 'ODS 14',
    'life in land': 'ODS 15',
    'peace, justice and strong institutions': 'ODS 16',
    'partnerships for the goals': 'ODS 17',
}

dimensoes = {
    'ODS 1': 'Social', 'ODS 2': 'Social', 'ODS 3': 'Social',
    'ODS 4': 'Social', 'ODS 5': 'Social', 'ODS 10': 'Social',
    'ODS 16': 'Social',
    'ODS 6': 'Ambiental', 'ODS 13': 'Ambiental',
    'ODS 14': 'Ambiental', 'ODS 15': 'Ambiental',
    'ODS 7': 'Economica', 'ODS 8': 'Economica', 'ODS 9': 'Economica',
    'ODS 11': 'Economica', 'ODS 12': 'Economica',
    'ODS 17': 'Institucional',
}

cores_dim = {
    'Social': '#e63946', 'Ambiental': '#2a9d8f',
    'Economica': '#e9c46a', 'Institucional': '#457b9d',
}

serie = (
    df[colunaods].dropna().astype(str)
    .str.split(r'[|;\n]').explode().str.strip().str.lower()
)

nao_mapeados = sorted(set(serie.dropna().unique()) - set(ods.keys()))
if nao_mapeados:
    print("\nValores nao mapeados:", nao_mapeados)
else:
    print("\nTodos os valores foram mapeados.")

contagem = (
    serie.map(ods).dropna()
    .value_counts()
    .reindex([f"ODS {i}" for i in range(1, 18)], fill_value=0)
    .reset_index()
)
contagem.columns = ['ODS', 'Total de Artigos']

total_artigos = len(df)
artigos_classificados = df[colunaods].notnull().sum()
artigos_nao_classificados = df[colunaods].isnull().sum()

df_bar = contagem.sort_values('Total de Artigos', ascending=True)
cores = [cores_dim[dimensoes[o]] for o in df_bar['ODS']]

fig, ax = plt.subplots(figsize=(12, 8))
bars = ax.barh(df_bar['ODS'], df_bar['Total de Artigos'],
               color=cores, edgecolor='white')
ax.set_xlabel('Numero de artigos', fontsize=11)
ax.set_title('Artigos por ODS - UNIFESP (OpenAlex)',
             fontsize=14, fontweight='bold', pad=12)
ax.spines[['top', 'right']].set_visible(False)
ax.grid(axis='x', linestyle='--', alpha=0.4)

for bar in bars:
    largura = bar.get_width()
    ax.text(largura + max(df_bar['Total de Artigos']) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f'{int(largura)}', va='center', fontsize=9)

legenda = [Patch(facecolor=c, label=d) for d, c in cores_dim.items()]
ax.legend(handles=legenda, title='Dimensao', loc='lower right', frameon=False)

plt.tight_layout()

pasta_script = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
caminho_png = os.path.join(pasta_script, "grafico_ods.png")
plt.savefig(caminho_png, dpi=150, bbox_inches='tight')
print("\nGrafico salvo em:", caminho_png)

print("\nDistribuicao por ODS:")
print(contagem.sort_values('Total de Artigos', ascending=False).to_string(index=False))
print(f"\nTotal de artigos: {total_artigos}")
print(f"Artigos classificados: {artigos_classificados}")
print(f"Artigos nao classificados: {artigos_nao_classificados}")

try:
    if sys.platform == 'darwin':
        subprocess.run(['open', caminho_png])
except Exception as e:
    print("(Nao foi possivel abrir:", e, ")")