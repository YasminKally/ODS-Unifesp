# ==================================================================
# Analise: SciELO x nao-SciELO - UNIFESP (OpenAlex)
# ==================================================================
import os
import sys
import subprocess
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ------------------------------------------------------------------
# 1. Leitura
# ------------------------------------------------------------------
df = pd.read_csv(
    "./Open_Alex_UNIFESP_enriquecido.csv",
    sep=",", engine="python", on_bad_lines="skip", encoding="utf-8",
)
print("Linhas lidas:", len(df))

# ------------------------------------------------------------------
# 2. Mapeamento ODS (primeiro ODS da lista = ODS principal)
# ------------------------------------------------------------------
ods_map = {
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

df['ODS_principal'] = (
    df['SDG'].astype(str)
    .str.split(r'[|;\n]').str[0]
    .str.strip().str.lower()
    .map(ods_map)
)

# ------------------------------------------------------------------
# 3. Marca SciELO e normaliza colunas
# ------------------------------------------------------------------
df['SciELO'] = df['DOI'].astype(str).str.contains('10.1590/', na=False)
df['OA'] = df['Open access'].astype(str).str.strip()
df['Citacoes'] = pd.to_numeric(df['Cited by'], errors='coerce')

print("Artigos SciELO:", df['SciELO'].sum())
print("Artigos nao-SciELO:", (~df['SciELO']).sum())
print("Taxa SciELO:", round(df['SciELO'].mean() * 100, 1), "%")

pasta = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
ordem_ods = [f"ODS {i}" for i in range(1, 18)]

# ==================================================================
# GRAFICO 1 - Composicao SciELO x nao-SciELO por ODS
# ==================================================================
df_ods = df.dropna(subset=['ODS_principal']).copy()

tab = (
    df_ods.groupby(['ODS_principal', 'SciELO'])
    .size().unstack(fill_value=0)
    .reindex(ordem_ods, fill_value=0)
)
tab.columns = ['Nao-SciELO', 'SciELO']
tab['Total'] = tab.sum(axis=1)
tab['% SciELO'] = (tab['SciELO'] / tab['Total'] * 100).round(1)
tab = tab[tab['Total'] > 0]

print("\n=== SciELO por ODS ===")
print(tab.to_string())

taxa_geral = df_ods['SciELO'].mean() * 100

fig, ax = plt.subplots(figsize=(12, 8))
cores = ['#2a9d8f' if v >= taxa_geral else '#e76f51' for v in tab['% SciELO']]
barras = ax.barh(tab.index, tab['% SciELO'], color=cores, edgecolor='white')
ax.axvline(taxa_geral, color='black', linestyle='--', linewidth=1,
           label=f'Media geral: {taxa_geral:.1f}%')

for barra, valor in zip(barras, tab['% SciELO']):
    ax.text(valor + 0.5, barra.get_y() + barra.get_height()/2,
            f'{valor:.1f}%', va='center', fontsize=9)

ax.set_xlabel('Percentual de artigos SciELO (%)', fontsize=11)
ax.set_title('Presenca SciELO por ODS - UNIFESP',
             fontsize=14, fontweight='bold', pad=12)
ax.spines[['top', 'right']].set_visible(False)
ax.grid(axis='x', linestyle='--', alpha=0.4)
ax.legend(loc='lower right', frameon=False)

plt.tight_layout()
caminho1 = os.path.join(pasta, "scielo_por_ods.png")
plt.savefig(caminho1, dpi=150, bbox_inches='tight')
plt.close()
print("\nGrafico 1 salvo em:", caminho1)

# ==================================================================
# GRAFICO 2 - Composicao 100% empilhada SciELO x nao-SciELO
# ==================================================================
dados_pct = tab[['SciELO', 'Nao-SciELO']].div(tab['Total'], axis=0) * 100
dados_pct = dados_pct.sort_values('SciELO', ascending=True)

fig, ax = plt.subplots(figsize=(12, 8))
ax.barh(dados_pct.index, dados_pct['SciELO'], color='#2a9d8f',
        edgecolor='white', label='SciELO')
ax.barh(dados_pct.index, dados_pct['Nao-SciELO'], left=dados_pct['SciELO'],
        color='#adb5bd', edgecolor='white', label='Nao-SciELO')

for i, (idx, row) in enumerate(dados_pct.iterrows()):
    ax.text(row['SciELO']/2, i, f"{row['SciELO']:.0f}%",
            va='center', ha='center', color='white', fontsize=9, fontweight='bold')

ax.set_xlabel('Percentual (%)', fontsize=11)
ax.set_title('Composicao SciELO vs. Nao-SciELO por ODS - UNIFESP',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlim(0, 100)
ax.spines[['top', 'right']].set_visible(False)
ax.legend(loc='lower right', frameon=False)

plt.tight_layout()
caminho2 = os.path.join(pasta, "scielo_composicao_ods.png")
plt.savefig(caminho2, dpi=150, bbox_inches='tight')
plt.close()
print("Grafico 2 salvo em:", caminho2)

# ==================================================================
# GRAFICO 3 - Mediana de citacoes: SciELO vs. nao-SciELO por ODS
# ==================================================================
med = (
    df_ods.groupby(['ODS_principal', 'SciELO'])['Citacoes']
    .median().unstack().reindex(ordem_ods)
)
med.columns = ['Nao-SciELO', 'SciELO']
med = med.dropna(how='all').sort_values('SciELO', ascending=True)

print("\n=== Mediana de citacoes por ODS ===")
print(med.to_string())

x = np.arange(len(med))
largura = 0.4

fig, ax = plt.subplots(figsize=(12, 8))
ax.barh(x + largura/2, med['SciELO'], largura,
        color='#2a9d8f', edgecolor='white', label='SciELO')
ax.barh(x - largura/2, med['Nao-SciELO'], largura,
        color='#adb5bd', edgecolor='white', label='Nao-SciELO')

ax.set_yticks(x)
ax.set_yticklabels(med.index)
ax.set_xlabel('Mediana de citacoes', fontsize=11)
ax.set_title('Impacto (mediana de citacoes) - SciELO vs. Nao-SciELO',
             fontsize=14, fontweight='bold', pad=12)
ax.spines[['top', 'right']].set_visible(False)
ax.grid(axis='x', linestyle='--', alpha=0.4)
ax.legend(loc='lower right', frameon=False)

plt.tight_layout()
caminho3 = os.path.join(pasta, "scielo_citacoes_ods.png")
plt.savefig(caminho3, dpi=150, bbox_inches='tight')
plt.close()
print("Grafico 3 salvo em:", caminho3)

# ==================================================================
# RESUMO
# ==================================================================
print("\n" + "="*60)
print("RESUMO SciELO")
print("="*60)
print(f"Total de artigos: {len(df)}")
print(f"Artigos SciELO:   {df['SciELO'].sum()} ({df['SciELO'].mean()*100:.1f}%)")
print(f"Artigos nao-SciELO: {(~df['SciELO']).sum()}")

print(f"\nSciELO x Acesso Aberto:")
cross = pd.crosstab(df['SciELO'], df['OA'])
print(cross.to_string())

print(f"\nMediana geral de citacoes:")
print(f"  SciELO:     {df[df['SciELO']]['Citacoes'].median():.0f}")
print(f"  Nao-SciELO: {df[~df['SciELO']]['Citacoes'].median():.0f}")

print("\nTop 5 ODS com mais SciELO (em numeros absolutos):")
print(tab.sort_values('SciELO', ascending=False).head()[['SciELO', 'Total']].to_string())

# Abre
if sys.platform == 'darwin':
    for c in [caminho1, caminho2, caminho3]:
        subprocess.run(['open', c])