# Script para agregar os resultados anuais em um resumo global

import glob
import os
import re
from collections import Counter
import pandas as pd

# Diretórios
analysis_dir = "results/analysis"
global_summary_file = os.path.join(analysis_dir, "global_analysis_summary.md")

# Encontrar todos os arquivos de resumo anual
summary_files = sorted(glob.glob(os.path.join(analysis_dir, "analysis_summary_*.txt")))

# Filtrar arquivos válidos (ignorar 'limpo' e erros)
valid_summary_files = [
    f for f in summary_files 
    if re.match(r".*analysis_summary_\d{4}\.txt", f)
]

if not valid_summary_files:
    print(f"Nenhum arquivo de resumo anual válido encontrado em {analysis_dir}")
else:
    print(f"Arquivos de resumo encontrados para agregação: {valid_summary_files}")

    # Dicionários para agregar dados globais
    yearly_foci_count = {}
    global_state_counts = Counter()
    global_biome_counts = Counter()
    global_monthly_counts = Counter()
    yearly_top_state = {}
    yearly_bottom_state = {}

    # Processar cada arquivo de resumo anual
    print("\nIniciando agregação dos resumos anuais...")
    for f in valid_summary_files:
        year_match = re.search(r"analysis_summary_(\d{4})\.txt", f)
        if not year_match:
            print(f"  Aviso: Não foi possível extrair o ano do arquivo {f}. Pulando...")
            continue
        year = year_match.group(1)
        print(f"  Processando resumo do ano {year}...")

        try:
            with open(f, "r", encoding="utf-8") as infile:
                content = infile.read()
                
                # Extrair total de focos
                total_foci_match = re.search(r"Total de focos de queimada registrados: (\d+)", content)
                if total_foci_match:
                    yearly_foci_count[year] = int(total_foci_match.group(1))
                
                # Extrair estado com maior frequência
                top_state_match = re.search(r"Estado com MAIOR frequência: (.*?) \((\d+) focos\)", content)
                if top_state_match:
                    yearly_top_state[year] = (top_state_match.group(1), int(top_state_match.group(2)))

                # Extrair estado com menor frequência
                bottom_state_match = re.search(r"Estado com MENOR frequência: (.*?) \((\d+) focos\)", content)
                if bottom_state_match:
                    yearly_bottom_state[year] = (bottom_state_match.group(1), int(bottom_state_match.group(2)))

                # Extrair contagens por estado
                state_section_match = re.search(r"## Frequência de Focos por Estado:\n(.*?)\n##", content, re.DOTALL)
                if state_section_match:
                    state_lines = state_section_match.group(1).strip().split("\n")
                    for line in state_lines:
                        parts = line.split(":")
                        if len(parts) == 2:
                            state = parts[0].strip()
                            try:
                                count = int(parts[1].strip())
                                global_state_counts[state] += count
                            except ValueError:
                                pass # Ignorar linhas mal formatadas
                                
                # Extrair contagens por bioma
                biome_section_match = re.search(r"## Frequência de Focos por Bioma:\n(.*?)\n##", content, re.DOTALL)
                if biome_section_match:
                    biome_lines = biome_section_match.group(1).strip().split("\n")
                    for line in biome_lines:
                        parts = line.split(":")
                        if len(parts) == 2:
                            biome = parts[0].strip()
                            try:
                                count = int(parts[1].strip())
                                global_biome_counts[biome] += count
                            except ValueError:
                                pass
                                
                # Extrair contagens mensais
                month_section_match = re.search(r"## Distribuição Mensal de Focos:\n(.*?)\n##", content, re.DOTALL)
                if month_section_match:
                    month_lines = month_section_match.group(1).strip().split("\n")
                    for line in month_lines:
                        month_match = re.match(r"Mês (\d+): (\d+)", line)
                        if month_match:
                            month = int(month_match.group(1))
                            count = int(month_match.group(2))
                            global_monthly_counts[month] += count
                            
        except Exception as e:
            print(f"Erro ao processar o arquivo {f}: {e}")

    # Escrever o resumo global agregado
    print(f"\nEscrevendo resumo global em: {global_summary_file}")
    with open(global_summary_file, "w", encoding="utf-8") as outfile:
        outfile.write("# Resumo Global Agregado da Análise de Queimadas (2018-2024)\n\n")
        outfile.write("Este resumo compila os dados dos resumos anuais gerados a partir dos focos de queimadas do INPE.\n\n")

        # Total de Focos por Ano
        outfile.write("## Total de Focos de Queimada por Ano:\n")
        total_geral_focos = 0
        for year in sorted(yearly_foci_count.keys()):
            count = yearly_foci_count[year]
            outfile.write(f"- {year}: {count:,} focos\n")
            total_geral_focos += count
        outfile.write(f"\n**Total Geral (2018-2024): {total_geral_focos:,} focos**\n\n")

        # Frequência Global por Estado
        outfile.write("## Frequência Global de Focos por Estado (Top 15):\n")
        for state, count in global_state_counts.most_common(15):
            outfile.write(f"- {state}: {count:,}\n")
        outfile.write("\n")
        if global_state_counts:
             most_frequent_state_global = global_state_counts.most_common(1)[0]
             outfile.write(f"**Estado com MAIOR frequência geral:** {most_frequent_state_global[0]} ({most_frequent_state_global[1]:,} focos)\n")
             # Encontrar o menos frequente pode ser menos informativo se houver muitos com contagem baixa
             # least_frequent_state_global = min(global_state_counts, key=global_state_counts.get)
             # outfile.write(f"**Estado com MENOR frequência geral:** {least_frequent_state_global} ({global_state_counts[least_frequent_state_global]:,} focos)\n\n")

        # Frequência Global por Bioma
        outfile.write("## Frequência Global de Focos por Bioma:\n")
        for biome, count in global_biome_counts.most_common():
            outfile.write(f"- {biome}: {count:,}\n")
        outfile.write("\n")

        # Distribuição Global Mensal
        outfile.write("## Distribuição Global Mensal de Focos (Total 2018-2024):\n")
        if global_monthly_counts:
            for month in sorted(global_monthly_counts.keys()):
                outfile.write(f"- Mês {month}: {global_monthly_counts[month]:,} focos\n")
        else:
            outfile.write("Não foi possível agregar a distribuição mensal.\n")
        outfile.write("\n")
        
        # Estados com Maior/Menor Frequência Anual
        outfile.write("## Estados com Maior e Menor Frequência Anual:\n")
        outfile.write("| Ano  | Estado com MAIS Focos | Contagem | Estado com MENOS Focos | Contagem |\n")
        outfile.write("|------|-----------------------|----------|------------------------|----------|\n")
        for year in sorted(yearly_top_state.keys()):
            top_state, top_count = yearly_top_state.get(year, ("N/A", 0))
            bottom_state, bottom_count = yearly_bottom_state.get(year, ("N/A", 0))
            outfile.write(f"| {year} | {top_state:<21} | {top_count:<8,} | {bottom_state:<22} | {bottom_count:<8,} |\n")
        outfile.write("\n")

        outfile.write("## Nota sobre Causas:\n")
        outfile.write("Conforme observado nas análises anuais, o dataset do INPE não permite inferir causas (naturais vs. humanas) diretamente.\n")

    print("--- Agregação concluída. Resumo global salvo. ---")
    print("Próximo passo: Criar gráficos representativos.")