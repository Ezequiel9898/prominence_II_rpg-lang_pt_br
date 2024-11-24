import zipfile
import os
import shutil
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_and_copy_lang_folders():
    # Diretório temporário curto para evitar limites de comprimento de caminho no Windows
    temp_dir = r'C:\temp\extracted'
    current_dir = os.getcwd()
    lang_dir = os.path.join(current_dir, 'lang_folders')

    # Cria o diretório temporário e o diretório de destino 'lang_folders' se não existirem
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(lang_dir, exist_ok=True)

    # Percorre todos os arquivos no diretório atual
    for file_name in os.listdir(current_dir):
        if file_name.endswith(".jar"):
            try:
                file_path = os.path.join(current_dir, file_name)
                extract_path = os.path.join(temp_dir, file_name[:-4])  # Remove a extensão .jar

                logging.info(f'Extraindo o arquivo {file_name}')

                # Extrai o conteúdo do arquivo .jar usando o prefixo \\?\ para suportar caminhos longos
                with zipfile.ZipFile(file_path, 'r') as jar_file:
                    jar_file.extractall(f'\\\\?\\{extract_path}')

                # Flag para verificar se ao menos uma pasta 'lang' foi encontrada
                lang_found = False

                # Percorre todos os diretórios extraídos
                for root, dirs, files in os.walk(extract_path):
                    if 'lang' in dirs:
                        lang_path = os.path.join(root, 'lang')

                        # Nome da pasta que contém a pasta 'lang'
                        parent_folder_name = os.path.basename(root)

                        # Caminho de destino para os arquivos 'lang'
                        target_path = os.path.join(lang_dir, parent_folder_name, 'lang')
                        os.makedirs(target_path, exist_ok=True)

                        logging.info(f'Copiando arquivos de {lang_path} para {target_path}')

                        # Copia apenas os arquivos pt_br.json e en_us.json
                        for lang_file in os.listdir(lang_path):
                            if lang_file in ['pt_br.json', 'en_us.json']:
                                shutil.copy2(os.path.join(lang_path, lang_file), os.path.join(target_path, lang_file))
                                logging.info(f'Arquivo {lang_file} copiado para {target_path}')
                            else:
                                logging.info(f'Arquivo {lang_file} ignorado')

                        lang_found = True  # Marca que ao menos uma pasta lang foi processada

                # Remove o diretório extraído se a pasta 'lang' não foi encontrada
                if not lang_found:
                    logging.warning(f'Pasta "lang" não encontrada em {file_name}, removendo arquivos extraídos')
                    shutil.rmtree(extract_path)

            except (zipfile.BadZipFile, zipfile.LargeZipFile) as e:
                logging.error(f'Erro ao extrair o arquivo {file_name}: {e}')
            except PermissionError as e:
                logging.error(f'Erro de permissão ao processar o arquivo {file_name}: {e}')
            except FileNotFoundError as e:
                logging.error(f'Arquivo ou caminho não encontrado para {file_name}: {e}')
            except Exception as e:
                logging.error(f'Ocorreu um erro inesperado ao processar o arquivo {file_name}: {e}')
                if os.path.exists(extract_path):
                    shutil.rmtree(extract_path)

if __name__ == "__main__":
    extract_and_copy_lang_folders()