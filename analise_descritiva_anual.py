# Script para análise descritiva dos dados anuais

import pandas as pd
import glob
import os

# Diretórios
cleaned_yearly_dir = "data/cleaned_yearly"
analysis_output_dir = "results/analysis"

# Criar diretório de saída para análise se não existir
os.makedirs(analysis_output_dir, exist_ok=True)

# Encontrar todos os arquivos CSV limpos anuais
all_cleaned_files = sorted(glob.glob(os.path.join(cleaned_yearly_dir, "*_limpo.csv")))

# Verificar se arquivos foram encontrados
if not all_cleaned_files:
    print(f"Nenhum arquivo CSV limpo encontrado em {cleaned_yearly_dir}")
else:
    print(f"Arquivos CSV limpos encontrados para análise anual: {all_cleaned_files}")

    # Processar cada arquivo anual limpo
    for f in all_cleaned_files:
        year = f.split("_")[-2] # Extrair ano do nome do arquivo
        print(f"\n--- Analisando dados para o ano: {year} (Arquivo: {f}) ---")
        output_summary_file = os.path.join(analysis_output_dir, f"analysis_summary_{year}.txt")
        
        try:
            # Carregar o arquivo limpo
            print("  Carregando dados...")
            df = pd.read_csv(f, low_memory=False, parse_dates=["data_pas"]) # Tentar parsear data na leitura
            print(f"  Dados carregados. Total de focos: {len(df)}")

            # Abrir arquivo de resumo para escrita
            with open(output_summary_file, "w", encoding="utf-8") as summary_file:
                summary_file.write(f"# Resumo da Análise Descritiva - Ano {year}\n\n")
                summary_file.write(f"Arquivo fonte: {f}\n")
                summary_file.write(f"Total de focos de queimada registrados: {len(df)}\n\n")

                # 1. Análise por Estado
                print("  Analisando frequência por estado...")
                state_counts = df["estado"].value_counts()
                summary_file.write("## Frequência de Focos por Estado:\n")
                summary_file.write(state_counts.to_string())
                summary_file.write("\n\n")
                # Identificar estados com maior e menor frequência
                summary_file.write(f"Estado com MAIOR frequência: {state_counts.idxmax()} ({state_counts.max()} focos)\n")
                summary_file.write(f"Estado com MENOR frequência: {state_counts.idxmin()} ({state_counts.min()} focos)\n\n")

                # 2. Análise por Bioma
                print("  Analisando frequência por bioma...")
                biome_counts = df["bioma"].value_counts()
                summary_file.write("## Frequência de Focos por Bioma:\n")
                summary_file.write(biome_counts.to_string())
                summary_file.write("\n\n")

                # 3. Análise Temporal (Mensal)
                print("  Analisando distribuição mensal...")
                if "data_pas" in df.columns and pd.api.types.is_datetime64_any_dtype(df["data_pas"]):
                    df["mes"] = df["data_pas"].dt.month
                    monthly_counts = df["mes"].value_counts().sort_index()
                    summary_file.write("## Distribuição Mensal de Focos:\n")
                    summary_file.write(monthly_counts.to_string())
                    summary_file.write("\n\n")
                else:
                    summary_file.write("## Distribuição Mensal de Focos:\n")
                    summary_file.write("Coluna de data (")
                    summary_file.write("data_pas")
                    summary_file.write(") não encontrada ou não está no formato datetime.\n\n")

                # 4. Estatísticas Descritivas de Colunas Numéricas
                print("  Calculando estatísticas descritivas...")
                numeric_cols = ["latitude", "longitude", "numero_dias_sem_chuva", "precipitacao", "risco_fogo", "frp"]
                available_numeric_cols = [col for col in numeric_cols if col in df.columns]
                if available_numeric_cols:
                    desc_stats = df[available_numeric_cols].describe()
                    summary_file.write("## Estatísticas Descritivas (Colunas Numéricas):\n")
                    summary_file.write(desc_stats.to_string())
                    summary_file.write("\n\n")
                    # Verificar contagem de nulos nessas colunas
                    summary_file.write("Contagem de Nulos (Colunas Numéricas Selecionadas):\n")
                    summary_file.write(df[available_numeric_cols].isnull().sum().to_string())
                    summary_file.write("\n\n")
                else:
                    summary_file.write("## Estatísticas Descritivas (Colunas Numéricas):\n")
                    summary_file.write("Nenhuma das colunas numéricas esperadas foi encontrada.\n\n")
                
                # 5. Nota sobre Causas
                summary_file.write("## Nota sobre Causas:\n")
                summary_file.write("O dataset do INPE não contém informações explícitas sobre a causa dos focos (natural vs. humana). Análises de causa não são possíveis com estes dados.\n")

            print(f"  Análise descritiva para {year} concluída. Resumo salvo em: {output_summary_file}")

        except Exception as e:
            print(f"Erro ao analisar o arquivo {f}: {e}")
            # Salvar um arquivo de erro
            error_file_path = os.path.join(analysis_output_dir, f"error_analysis_{year}.txt")
            with open(error_file_path, "w") as error_file:
                error_file.write(f"Erro ao processar {f}:\n{str(e)}")
            continue # Pular para o próximo arquivo

    print("\n--- Análise descritiva anual concluída para todos os arquivos ---")
    print(f"Resumos salvos em: {analysis_output_dir}")
    