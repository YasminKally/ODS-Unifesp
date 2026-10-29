# ==================================================================
# Analise: Acesso Aberto vs. Fechado por ODS - UNIFESP (OpenAlex)
# ==================================================================
import os
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

colunaods = "SDG"

# ------------------------------------------------------------------
# 2. Mapeamento ODS
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

# Pega o PRIMEIRO ODS de cada artigo (ODS principal)
df['ODS_principal'] = (
    df[colunaods].astype(str)
    .str.split(r'[|;\n]').str[0]
    .str.strip().str.lower()
    .map(ods_map)
)

df_ods = df.dropna(subset=['ODS_principal']).copy()
print("Artigos com ODS principal definido:", len(df_ods))

# Normaliza coluna de OA
df_ods['OA'] = df_ods['Open access'].astype(str).str.strip()

pasta = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()

ordem_ods = [f"ODS {i}" for i in range(1, 18)]

# ==================================================================
# GRAFICO 1 - Taxa de OA por ODS
# ==================================================================
tabela_oa = (
    df_ods.groupby(['ODS_principal', 'OA'])
    .size().unstack(fill_value=0)
    .reindex(ordem_ods, fill_value=0)
)
tabela_oa.columns = ['Fechado', 'Aberto']  # NOT Open Access, Open Access
tabela_oa['Total'] = tabela_oa.sum(axis=1)
tabela_oa['% OA'] = (tabela_oa['Aberto'] / tabela_oa['Total'] * 100).round(1)
tabela_oa = tabela_oa[tabela_oa['Total'] > 0]

print("\n=== Taxa de OA por ODS ===")
print(tabela_oa.to_string())

taxa_media = df_ods['OA'].eq('Open Access').mean() * 100

fig, ax = plt.subplots(figsize=(12, 8))
cores = ['#2a9d8f' if v >= taxa_media else '#e76f51' for v in tabela_oa['% OA']]
barras = ax.barh(tabela_oa.index, tabela_oa['% OA'], color=cores, edgecolor='white')
ax.axvline(taxa_media, color='black', linestyle='--', linewidth=1,
           label=f'Média geral: {taxa_media:.1f}%')

for barra, valor in zip(barras, tabela_oa['% OA']):
    ax.text(valor + 1, barra.get_y() + barra.get_height()/2,
            f'{valor:.1f}%', va='center', fontsize=9)

ax.set_xlabel('Percentual de Acesso Aberto (%)', fontsize=11)
ax.set_title('Taxa de Acesso Aberto por ODS — UNIFESP',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlim(0, 105)
ax.spines[['top', 'right']].set_visible(False)
ax.grid(axis='x', linestyle='--', alpha=0.4)
ax.legend(loc='lower right', frameon=False)

plt.tight_layout()
caminho1 = os.path.join(pasta, "oa_por_ods.png")
plt.savefig(caminho1, dpi=150, bbox_inches='tight')
plt.close()
print("\nGrafico 1 salvo em:", caminho1)

# ==================================================================
# GRAFICO 2 - Composicao OA vs Fechado por ODS (barras empilhadas %)
# ==================================================================
dados_pct = tabela_oa[['Aberto', 'Fechado']].div(tabela_oa['Total'], axis=0) * 100
dados_pct = dados_pct.sort_values('Aberto', ascending=True)

fig, ax = plt.subplots(figsize=(12, 8))
ax.barh(dados_pct.index, dados_pct['Aberto'], color='#2a9d8f',
        edgecolor='white', label='Acesso Aberto')
ax.barh(dados_pct.index, dados_pct['Fechado'], left=dados_pct['Aberto'],
        color='#e76f51', edgecolor='white', label='Fechado')

for i, (idx, row) in enumerate(dados_pct.iterrows()):
    ax.text(row['Aberto']/2, i, f"{row['Aberto']:.0f}%",
            va='center', ha='center', color='white', fontsize=9, fontweight='bold')
    ax.text(row['Aberto'] + row['Fechado']/2, i, f"{row['Fechado']:.0f}%",
            va='center', ha='center', color='white', fontsize=9, fontweight='bold')

ax.set_xlabel('Percentual (%)', fontsize=11)
ax.set_title('Composição Acesso Aberto vs. Fechado por ODS — UNIFESP',
             fontsize=14, fontweight='bold', pad=12)
ax.set_xlim(0, 100)
ax.spines[['top', 'right']].set_visible(False)
ax.legend(loc='lower right', frameon=False)

plt.tight_layout()
caminho2 = os.path.join(pasta, "composicao_oa_ods.png")
plt.savefig(caminho2, dpi=150, bbox_inches='tight')
plt.close()
print("Grafico 2 salvo em:", caminho2)

# ==================================================================
# GRAFICO 3 - Citacoes (mediana) OA vs Fechado por ODS
# ==================================================================
df_ods['Citacoes'] = pd.to_numeric(df_ods['Cited by'], errors='coerce')

med_cit = (
    df_ods.groupby(['ODS_principal', 'OA'])['Citacoes']
    .median().unstack()
    .reindex(ordem_ods)
)
med_cit.columns = ['Fechado', 'Aberto']
med_cit = med_cit.dropna(how='all')
med_cit = med_cit.sort_values('Aberto', ascending=True)

print("\n=== Mediana de citacoes por ODS ===")
print(med_cit.to_string())

x = np.arange(len(med_cit))
largura = 0.4

fig, ax = plt.subplots(figsize=(12, 8))
ax.barh(x + largura/2, med_cit['Aberto'], largura,
        color='#2a9d8f', edgecolor='white', label='Acesso Aberto')
ax.barh(x - largura/2, med_cit['Fechado'], largura,
        color='#e76f51', edgecolor='white', label='Fechado')

ax.set_yticks(x)
ax.set_yticklabels(med_cit.index)
ax.set_xlabel('Mediana de citações', fontsize=11)
ax.set_title('Impacto (mediana de citações) — OA vs. Fechado por ODS',
             fontsize=14, fontweight='bold', pad=12)
ax.spines[['top', 'right']].set_visible(False)
ax.grid(axis='x', linestyle='--', alpha=0.4)
ax.legend(loc='lower right', frameon=False)

plt.tight_layout()
caminho3 = os.path.join(pasta, "citacoes_oa_ods.png")
plt.savefig(caminho3, dpi=150, bbox_inches='tight')
plt.close()
print("Grafico 3 salvo em:", caminho3)

# ==================================================================
# RESUMO NO TERMINAL
# ==================================================================
print("\n" + "="*60)
print("RESUMO")
print("="*60)
print(f"Artigos com ODS principal: {len(df_ods)}")
print(f"Taxa de OA (base ODS):     {taxa_media:.1f}%")
print(f"Mediana geral de citacoes:")
print(f"  OA:      {df_ods[df_ods['OA']=='Open Access']['Citacoes'].median():.0f}")
print(f"  Fechado: {df_ods[df_ods['OA']!='Open Access']['Citacoes'].median():.0f}")

print("\nGerados 3 graficos:")
print("  1.", caminho1)
print("  2.", caminho2)
print("  3.", caminho3)

# Abre os 3
import subprocess, sys
if sys.platform == 'darwin':
    for c in [caminho1, caminho2, caminho3]:
        subprocess.run(['open', c])