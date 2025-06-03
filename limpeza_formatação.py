
# Script para limpeza e formatação dos dados em chunks, evitando problemas de memória

import pandas as pd
import glob
import os

# Diretórios
source_data_dir = "data/raw" # Contém zips e CSVs originais (exceto 2024)
source_tmp_dir = "data/raw/tmp" # Contém CSV original de 2024
output_cleaned_yearly_dir = "data/cleaned_yearly"

# Criar diretório de saída se não existir
os.makedirs(output_cleaned_yearly_dir, exist_ok=True)

# Tamanho do chunk para leitura
chunk_size = 100000  # Processar 100,000 linhas por vez

# Encontrar os arquivos CSV originais nos diretórios corretos
csv_files_main = glob.glob(os.path.join(source_data_dir, "focos_br_todos-sats_*.csv"))
csv_files_tmp = glob.glob(os.path.join(source_tmp_dir, "focos_br_todos-sats_*.csv"))
all_original_csv_files = sorted(csv_files_main + csv_files_tmp)

# Verificar se arquivos foram encontrados
if not all_original_csv_files:
    print("Nenhum arquivo CSV original encontrado nos diretórios especificados.")
else:
    print(f"Arquivos CSV originais encontrados para processamento: {all_original_csv_files}")

    # Processar cada arquivo original individualmente em chunks
    for f in all_original_csv_files:
        print(f"\n--- Processando arquivo em chunks: {f} ---")
        # Definir o caminho do arquivo de saída limpo
        base_name = os.path.basename(f)
        cleaned_file_path = os.path.join(output_cleaned_yearly_dir, f"{os.path.splitext(base_name)[0]}_limpo.csv")
        
        # Verificar se o arquivo limpo já existe para evitar reprocessamento (opcional, mas útil)
        # if os.path.exists(cleaned_file_path):
        #     print(f"Arquivo limpo {cleaned_file_path} já existe. Pulando...")
        #     continue
            
        first_chunk = True # Flag para controlar a escrita do cabeçalho
        total_rows_processed = 0
        
        try:
            # Usar um iterator para ler o arquivo em chunks
            try:
                chunk_iterator = pd.read_csv(f, chunksize=chunk_size, iterator=True, low_memory=False)
                encoding_used = 'utf-8'
            except UnicodeDecodeError:
                print("Falha ao ler com UTF-8, tentando com Latin-1...")
                chunk_iterator = pd.read_csv(f, chunksize=chunk_size, iterator=True, encoding='latin1', low_memory=False)
                encoding_used = 'latin1'
            
            print(f"Iniciando leitura com encoding {encoding_used} e chunksize={chunk_size}")

            for i, chunk in enumerate(chunk_iterator):
                # print(f"  Processando chunk {i+1}...") # Comentado para reduzir output
                rows_in_chunk = len(chunk)
                total_rows_processed += rows_in_chunk

                # --- Início da Limpeza do Chunk --- 
                chunk.drop_duplicates(inplace=True)

                # Padronizar/Converter coluna de data/hora (usar data_pas se datahora não existir)
                date_col_to_use = None
                if 'datahora' in chunk.columns:
                    date_col_to_use = 'datahora'
                elif 'data_pas' in chunk.columns:
                    date_col_to_use = 'data_pas'
                
                if date_col_to_use:
                    try:
                        chunk[date_col_to_use] = pd.to_datetime(chunk[date_col_to_use], errors='coerce')
                    except Exception as e:
                        print(f"    Erro ao converter '{date_col_to_use}' no chunk: {e}")
                
                # Padronizar categorias (bioma, estado, municipio)
                for col in ['bioma', 'estado', 'municipio']:
                    if col in chunk.columns:
                        chunk[col] = chunk[col].fillna('DESCONHECIDO').astype(str).str.upper()

                # --- Fim da Limpeza do Chunk --- 

                # Salvar/Anexar o chunk limpo
                if first_chunk:
                    chunk.to_csv(cleaned_file_path, index=False, mode='w', header=True)
                    first_chunk = False
                else:
                    chunk.to_csv(cleaned_file_path, index=False, mode='a', header=False)
            
            print(f"Arquivo {f} processado. Total de linhas: {total_rows_processed}. Arquivo limpo salvo em: {cleaned_file_path}")

        except Exception as e:
            print(f"Erro GERAL ao processar o arquivo {f}: {e}")
            continue # Pular para o próximo arquivo

    print("\n--- Processamento de todos os arquivos originais concluído ---")
    print(f"Arquivos limpos por ano salvos em: {output_cleaned_yearly_dir}")
    