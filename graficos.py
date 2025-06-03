# Script para geração dos gráficos representativos

import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
from collections import Counter
import pandas as pd # Needed for DataFrame manipulation if parsing fails

# Diretórios
analysis_dir = "results/analysis"
global_summary_file = os.path.join(analysis_dir, "global_analysis_summary.md")
plots_output_dir = os.path.join(analysis_dir, "plots")

# Criar diretório de saída para gráficos se não existir
os.makedirs(plots_output_dir, exist_ok=True)

# --- Dados Agregados (Extraídos do Script Anterior ou Parseados) ---
# Tentar parsear o arquivo de resumo global
yearly_foci_count = {}
global_state_counts = Counter()
global_biome_counts = Counter()
global_monthly_counts = Counter()

try:
    with open(global_summary_file, "r", encoding="utf-8") as f:
        content = f.read()

        # Parse Total Focos por Ano
        year_section = re.search(r"## Total de Focos de Queimada por Ano:\n(.*?)\n\n\*\*Total Geral", content, re.DOTALL)
        if year_section:
            for line in year_section.group(1).strip().split("\n"):
                match = re.match(r"- (\d{4}): ([\d,]+) focos", line)
                if match:
                    year = match.group(1)
                    count = int(match.group(2).replace(",", ""))
                    yearly_foci_count[year] = count

        # Parse Frequência Global por Estado
        state_section = re.search(r"## Frequência Global de Focos por Estado \(Top 15\):\n(.*?)\n\n", content, re.DOTALL)
        if state_section:
            for line in state_section.group(1).strip().split("\n"):
                match = re.match(r"- (.*?): ([\d,]+)", line)
                if match:
                    state = match.group(1).strip()
                    count = int(match.group(2).replace(",", ""))
                    global_state_counts[state] = count

        # Parse Frequência Global por Bioma
        biome_section = re.search(r"## Frequência Global de Focos por Bioma:\n(.*?)\n\n", content, re.DOTALL)
        if biome_section:
            for line in biome_section.group(1).strip().split("\n"):
                match = re.match(r"- (.*?): ([\d,]+)", line)
                if match:
                    biome = match.group(1).strip()
                    count = int(match.group(2).replace(",", ""))
                    global_biome_counts[biome] = count

        # Parse Distribuição Global Mensal
        month_section = re.search(r"## Distribuição Global Mensal de Focos \(Total 2018-2024\):\n(.*?)\n\n", content, re.DOTALL)
        if month_section:
            for line in month_section.group(1).strip().split("\n"):
                match = re.match(r"- Mês (\d+): ([\d,]+) focos", line)
                if match:
                    month = int(match.group(1))
                    count = int(match.group(2).replace(",", ""))
                    global_monthly_counts[month] = count

except Exception as e:
    print(f"Erro ao parsear o arquivo de resumo global: {e}. Gráficos não podem ser gerados.")
    exit()

# Verificar se os dados foram carregados
if not yearly_foci_count or not global_state_counts or not global_biome_counts or not global_monthly_counts:
    print("Dados agregados não puderam ser extraídos do resumo. Gráficos não podem ser gerados.")
    exit()

# --- Geração dos Gráficos --- 
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 7)
plt.rcParams["figure.dpi"] = 100

# Gráfico 1: Total de Focos por Ano

years = sorted(yearly_foci_count.keys())
counts_yearly = [yearly_foci_count[y] for y in years]
plt.figure()
ax = sns.barplot(x=years, y=counts_yearly, palette="viridis")
ax.set_title("Total de Focos de Queimada por Ano (Brasil, 2018-2024)", fontsize=16)
ax.set_xlabel("Ano", fontsize=12)
ax.set_ylabel("Número de Focos", fontsize=12)
# Adicionar rótulos de dados formatados
for i, v in enumerate(counts_yearly):
    ax.text(i, v + (max(counts_yearly)*0.01), f"{v:,.0f}".replace(",", "."), ha="center", va="bottom", fontsize=10)
plt.tight_layout()
plot1_path = os.path.join(plots_output_dir, "grafico_focos_por_ano.png")
plt.savefig(plot1_path)
print(f"Gráfico 1 salvo em: {plot1_path}")
plt.close()

# Gráfico 2: Distribuição Mensal Média

months = sorted(global_monthly_counts.keys())
counts_monthly = [global_monthly_counts[m] for m in months]
num_years = len(yearly_foci_count)
counts_monthly_avg = [c / num_years for c in counts_monthly]
month_names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
plt.figure()
ax = sns.barplot(x=month_names, y=counts_monthly_avg, palette="magma")
ax.set_title(f"Distribuição Mensal Média de Focos de Queimada (Brasil, Média {num_years} Anos)", fontsize=16)
ax.set_xlabel("Mês", fontsize=12)
ax.set_ylabel("Número Médio de Focos", fontsize=12)
for i, v in enumerate(counts_monthly_avg):
    ax.text(i, v + (max(counts_monthly_avg)*0.01), f"{v:,.0f}".replace(",", "."), ha="center", va="bottom", fontsize=10)
plt.tight_layout()
plot2_path = os.path.join(plots_output_dir, "grafico_distribuicao_mensal_media.png")
plt.savefig(plot2_path)
print(f"Gráfico 2 salvo em: {plot2_path}")
plt.close()

# Gráfico 3: Focos por Bioma

biomes = [item[0] for item in global_biome_counts.most_common()]
counts_biome = [item[1] for item in global_biome_counts.most_common()]
plt.figure()
ax = sns.barplot(x=counts_biome, y=biomes, palette="crest", orient="h")
ax.set_title("Total de Focos de Queimada por Bioma (Brasil, 2018-2024)", fontsize=16)
ax.set_xlabel("Número de Focos", fontsize=12)
ax.set_ylabel("Bioma", fontsize=12)
# Adicionar rótulos de dados
for i, v in enumerate(counts_biome):
    ax.text(v + (max(counts_biome)*0.01), i, f"{v:,.0f}".replace(",", "."), va="center", fontsize=10)
plt.tight_layout()
plot3_path = os.path.join(plots_output_dir, "grafico_focos_por_bioma.png")
plt.savefig(plot3_path)
print(f"Gráfico 3 salvo em: {plot3_path}")
plt.close()

# Gráfico 4: Focos por Estado (Top 10)

top_n = 10
states_top = [item[0] for item in global_state_counts.most_common(top_n)]
counts_state_top = [item[1] for item in global_state_counts.most_common(top_n)]
plt.figure()
ax = sns.barplot(x=counts_state_top, y=states_top, palette="rocket", orient="h")
ax.set_title(f"Top {top_n} Estados com Mais Focos de Queimada (Brasil, 2018-2024)", fontsize=16)
ax.set_xlabel("Número de Focos", fontsize=12)
ax.set_ylabel("Estado", fontsize=12)
# Adicionar rótulos de dados
for i, v in enumerate(counts_state_top):
    ax.text(v + (max(counts_state_top)*0.01), i, f"{v:,.0f}".replace(",", "."), va="center", fontsize=10)
plt.tight_layout()
plot4_path = os.path.join(plots_output_dir, "grafico_focos_por_estado_top10.png")
plt.savefig(plot4_path)
print(f"Gráfico 4 salvo em: {plot4_path}")
plt.close()