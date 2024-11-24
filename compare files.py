import os
import json
from collections import defaultdict

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Erro ao ler o arquivo {file_path}: {e}")
        return None

def compare_files(file1_content, file2_content):
    return file1_content != file2_content

def walk_directory(base_dir):
    files_by_root = defaultdict(list)
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(('.json', '.snbt', '.txt', '.mcfunction', '.js')) and file != "pt_br.json":
                relative_path = os.path.relpath(os.path.join(root, file), base_dir)
                root_folder = relative_path.split(os.sep)[0]
                files_by_root[root_folder].append(relative_path)
    return files_by_root

def group_by_subfolders(file_paths):
    grouped = defaultdict(lambda: defaultdict(list))
    root_files = []
    for path in file_paths:
        parts = path.split(os.sep)
        if len(parts) > 2:
            grouped[parts[0]][parts[1]].append(os.sep.join(parts[2:]))
        elif len(parts) == 2:
            grouped[parts[0]][parts[1]].append(parts[1])
        else:
            root_files.append(parts[0])  # Arquivo na raiz
    return grouped, root_files

def flatten_mods(file_paths):
    # Modifica os caminhos para não incluir 'mods' como prefixo
    return [os.sep.join(path.split(os.sep)[1:]) for path in file_paths]

def compare_directories(new_dir, old_dir):
    new_files = walk_directory(new_dir)
    old_files = walk_directory(old_dir)

    all_roots = set(new_files.keys()).union(set(old_files.keys()))

    result = {}
    root_files = {"different": [], "added": [], "removed": []}

    for root in sorted(all_roots):
        new_files_in_root = set(new_files.get(root, []))
        old_files_in_root = set(old_files.get(root, []))

        common_files = new_files_in_root.intersection(old_files_in_root)
        added_files = new_files_in_root - old_files_in_root
        removed_files = old_files_in_root - new_files_in_root

        different_files = []

        for relative_path in common_files:
            new_file_path = os.path.join(new_dir, relative_path)
            old_file_path = os.path.join(old_dir, relative_path)

            new_content = read_file(new_file_path)
            old_content = read_file(old_file_path)

            if new_content is not None and old_content is not None:
                if compare_files(new_content, old_content):
                    different_files.append(relative_path)

        # Tratamento especial para a pasta "mods"
        if root == "mods":
            result[root] = {
                "different": flatten_mods(different_files),
                "added": flatten_mods(added_files),
                "removed": flatten_mods(removed_files)
            }
        else:
            grouped_different, diff_root = group_by_subfolders(different_files)
            grouped_added, add_root = group_by_subfolders(added_files)
            grouped_removed, rem_root = group_by_subfolders(removed_files)

            # Adiciona os arquivos "root" na categoria específica
            root_files["different"].extend(diff_root)
            root_files["added"].extend(add_root)
            root_files["removed"].extend(rem_root)

            if grouped_different or grouped_added or grouped_removed:
                result[root] = {
                    "different": grouped_different[root],
                    "added": grouped_added[root],
                    "removed": grouped_removed[root]
                }

    # Se houver arquivos "root", adiciona ao final do JSON
    if any(root_files.values()):
        result["root_files"] = root_files

    return result

def main():
    new_directory = "novo"
    old_directory = "velho"
    output_file = "output.json"

    comparison_result = compare_directories(new_directory, old_directory)

    with open(output_file, 'w', encoding='utf-8') as out:
        json.dump(comparison_result, out, indent=4, ensure_ascii=False)

    print(f"Resultados salvos em {output_file}")

if __name__ == "__main__":
    main()

