# Script para análise do ano de 2024 em chunks devido ao grande volume de dados

import pandas as pd
import glob
import os
from collections import Counter
import numpy as np # Import numpy for infinity

# Diretórios
cleaned_yearly_dir = "data/cleaned_yearly"
analysis_output_dir = "results/analysis"

# Criar diretório de saída para análise se não existir
os.makedirs(analysis_output_dir, exist_ok=True)

# Arquivo problemático (2024)
file_to_analyze_chunked = os.path.join(cleaned_yearly_dir, "focos_br_todos-sats_2024_limpo.csv")
year = "2024"
output_summary_file = os.path.join(analysis_output_dir, f"analysis_summary_{year}.txt")
chunk_size = 100000 # Mesmo chunk size da limpeza

print(f"--- Analisando dados para o ano: {year} em CHUNKS (Arquivo: {file_to_analyze_chunked}) ---")

# Inicializar contadores e agregadores
total_focos = 0
state_counts = Counter()
biome_counts = Counter()
monthly_counts = Counter()

# Inicializar agregadores para estatísticas descritivas (simplificado)
numeric_cols = ["latitude", "longitude", "numero_dias_sem_chuva", "precipitacao", "risco_fogo", "frp"]
available_numeric_cols = [] # Será preenchido com as colunas encontradas no primeiro chunk
numeric_stats = {}

try:
    print("  Iniciando leitura e análise em chunks...")
    first_chunk = True
    chunk_iterator = pd.read_csv(file_to_analyze_chunked, chunksize=chunk_size, iterator=True, low_memory=False, parse_dates=["data_pas"])

    for i, chunk in enumerate(chunk_iterator):
        # print(f"    Processando chunk {i+1}...") # Comentado para reduzir output
        total_focos += len(chunk)

        if first_chunk:
            # Identificar colunas numéricas disponíveis no primeiro chunk
            available_numeric_cols = [col for col in numeric_cols if col in chunk.columns and pd.api.types.is_numeric_dtype(chunk[col])]
            for col in available_numeric_cols:
                # Correção da inicialização de min/max
                numeric_stats[col] = {"count": 0, "sum": 0, "min": np.inf, "max": -np.inf}
            first_chunk = False

        # 1. Contagem por Estado
        state_counts.update(chunk["estado"].dropna())

        # 2. Contagem por Bioma
        biome_counts.update(chunk["bioma"].dropna())

        # 3. Contagem Temporal (Mensal)
        if "data_pas" in chunk.columns and pd.api.types.is_datetime64_any_dtype(chunk["data_pas"]):
            monthly_counts.update(chunk["data_pas"].dt.month.dropna().astype(int))
            
        # 4. Estatísticas Descritivas (Agregação Simplificada)
        for col in available_numeric_cols:
            valid_data = chunk[col].dropna()
            if not valid_data.empty:
                numeric_stats[col]["count"] += valid_data.count()
                numeric_stats[col]["sum"] += valid_data.sum()
                # Correção da atualização de min/max
                numeric_stats[col]["min"] = min(numeric_stats[col]["min"], valid_data.min())
                numeric_stats[col]["max"] = max(numeric_stats[col]["max"], valid_data.max())

    print("  Leitura e agregação de chunks concluída.")

    # Escrever o resumo agregado
    print(f"  Salvando resumo agregado em: {output_summary_file}")
    with open(output_summary_file, "w", encoding="utf-8") as summary_file:
        summary_file.write(f"# Resumo da Análise Descritiva - Ano {year} (Processado em Chunks)\n\n")
        summary_file.write(f"Arquivo fonte: {file_to_analyze_chunked}\n")
        summary_file.write(f"Total de focos de queimada registrados: {total_focos}\n\n")

        # Frequência por Estado
        summary_file.write("## Frequência de Focos por Estado:\n")
        for state, count in sorted(state_counts.items(), key=lambda item: item[1], reverse=True):
            summary_file.write(f"{state}: {count}\n")
        summary_file.write("\n")
        if state_counts:
            most_frequent_state = max(state_counts, key=state_counts.get)
            least_frequent_state = min(state_counts, key=state_counts.get)
            summary_file.write(f"Estado com MAIOR frequência: {most_frequent_state} ({state_counts[most_frequent_state]} focos)\n")
            summary_file.write(f"Estado com MENOR frequência: {least_frequent_state} ({state_counts[least_frequent_state]} focos)\n\n")

        # Frequência por Bioma
        summary_file.write("## Frequência de Focos por Bioma:\n")
        for biome, count in sorted(biome_counts.items(), key=lambda item: item[1], reverse=True):
            summary_file.write(f"{biome}: {count}\n")
        summary_file.write("\n")

        # Distribuição Mensal
        summary_file.write("## Distribuição Mensal de Focos:\n")
        if monthly_counts:
            for month in sorted(monthly_counts.keys()):
                summary_file.write(f"Mês {month}: {monthly_counts[month]}\n")
        else:
            summary_file.write("Não foi possível calcular a distribuição mensal (verificar coluna de data).\n")
        summary_file.write("\n")

        # Estatísticas Descritivas (Simplificado)
        summary_file.write("## Estatísticas Descritivas (Colunas Numéricas - Agregado de Chunks):\n")
        if available_numeric_cols:
            summary_file.write("| Coluna                | Count      | Mean       | Min        | Max        |\n")
            summary_file.write("|-----------------------|------------|------------|------------|------------|\n")
            for col in available_numeric_cols:
                stats = numeric_stats[col]
                count = stats["count"]
                mean = stats["sum"] / count if count > 0 else 0
                # Correção da exibição de min/max
                min_val = stats["min"] if stats["min"] != np.inf else np.nan 
                max_val = stats["max"] if stats["max"] != -np.inf else np.nan
                summary_file.write(f"| {col:<21} | {count:<10} | {mean:<10.2f} | {min_val:<10.2f} | {max_val:<10.2f} |\n")
            summary_file.write("\nNota: Média, Mínimo e Máximo calculados pela agregação de chunks. Desvio padrão e percentis não calculados devido à complexidade da agregação.\n\n")
        else:
            summary_file.write("Nenhuma das colunas numéricas esperadas foi encontrada ou processada.\n\n")
            
        # Nota sobre Causas
        summary_file.write("## Nota sobre Causas:\n")
        summary_file.write("O dataset do INPE não contém informações explícitas sobre a causa dos focos (natural vs. humana). Análises de causa não são possíveis com estes dados.\n")

    print(f"--- Análise em chunks para {year} concluída. ---")

except FileNotFoundError:
    print(f"Erro: Arquivo {file_to_analyze_chunked} não encontrado.")
except Exception as e:
    print(f"Erro GERAL ao analisar o arquivo {file_to_analyze_chunked} em chunks: {e}")
    # Salvar um arquivo de erro
    error_file_path = os.path.join(analysis_output_dir, f"error_analysis_chunked_{year}.txt")
    with open(error_file_path, "w") as error_file:
        error_file.write(f"Erro ao processar {file_to_analyze_chunked} em chunks:\n{str(e)}")

print("\nPróximo passo: Agregar resultados de todos os anos e criar gráficos.")