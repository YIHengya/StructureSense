import os
import json
import shutil


def get_folder_structure(path, max_depth, folders_only=False):
    def traverse(current_path, current_depth):
        if current_depth > max_depth:
            return None
        structure = {}
        try:
            with os.scandir(current_path) as entries:
                for entry in entries:
                    if entry.is_dir():
                        sub_structure = traverse(entry.path, current_depth + 1)
                        if sub_structure is not None:
                            structure[entry.name] = sub_structure
                    elif not folders_only:
                        structure[entry.name] = None
        except PermissionError:
            return "Permission denied"
        except FileNotFoundError:
            return "Path not found"

        return structure

    result = traverse(path, 1)
    return json.dumps(result, indent=2, ensure_ascii=False)


def create_and_merge_folder_structure(json_structure, base_path):
    def scan_directory(path):
        structure = {}
        for entry in os.scandir(path):
            if entry.is_file():
                structure[entry.name] = None
            elif entry.is_dir():
                structure[entry.name] = scan_directory(entry.path)
        return structure

    def merge_structures(existing, new):
        for key, value in new.items():
            if key not in existing:
                existing[key] = value
            elif isinstance(existing[key], dict) and isinstance(value, dict):
                merge_structures(existing[key], value)
        return existing

    def create_structure(structure, current_path):
        for name, content in structure.items():
            path = os.path.join(current_path, name)
            if content is None:
                # 这是一个文件
                if not os.path.exists(path):
                    open(path, 'a').close()
                    print(f"Created file: {path}")
                else:
                    print(f"File already exists: {path}")
            else:
                # 这是一个文件夹
                if not os.path.exists(path):
                    os.makedirs(path)
                    print(f"Created directory: {path}")
                else:
                    print(f"Directory already exists: {path}")
                if isinstance(content, dict):
                    create_structure(content, path)

    # 确保base_path存在
    if not os.path.exists(base_path):
        os.makedirs(base_path)
        print(f"Created base directory: {base_path}")

    # 如果输入是JSON字符串，先解析它
    if isinstance(json_structure, str):
        new_structure = json.loads(json_structure)
    else:
        new_structure = json_structure

    # 扫描现有的文件结构
    existing_structure = scan_directory(base_path)

    # 合并新旧结构
    merged_structure = merge_structures(existing_structure, new_structure)

    # 创建新的文件和文件夹
    create_structure(new_structure, base_path)

    # 返回合并后的完整结构
    return json.dumps(merged_structure, indent=2, ensure_ascii=False)


def load_config(config_path='config.json'):
    try:
        with open(config_path, 'r', encoding='utf-8') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Invalid JSON in config file: {config_path}")
        return {}
    except UnicodeDecodeError:
        print(f"Encoding error in config file: {config_path}. Please ensure the file is saved in UTF-8 format.")
        return {}


def extract_filenames(json_str):
    # 解析 JSON 字符串
    parsed = json.loads(json_str)

    # 提取所有键名（文件名）
    filenames = []
    for item in parsed:
        if isinstance(item, dict):
            filenames.extend(item.keys())
        else:
            filenames.append(item)

    return filenames


def move_file(source_path, destination_folder):
    try:
        # 确保目标文件夹存在，如果不存在就创建
        os.makedirs(destination_folder, exist_ok=True)

        # 获取文件名
        file_name = os.path.basename(source_path)

        # 构建目标文件的完整路径
        destination_path = os.path.join(destination_folder, file_name)

        # 移动文件
        shutil.move(source_path, destination_path)

        print(f"文件 '{file_name}' 已成功移动到 '{destination_folder}'")
    except FileNotFoundError:
        print(f"错误：源文件 '{source_path}' 不存在")
    except PermissionError:
        print(f"错误：没有权限移动文件 '{source_path}'")
    except shutil.Error as e:
        print(f"移动文件时发生错误：{e}")
    except Exception as e:
        print(f"发生未知错误：{e}")


def json_to_path_list(json_data, current_path=""):
    path_list = []

    for key, value in json_data.items():
        new_path = f"{current_path}/{key}" if current_path else key

        if isinstance(value, dict):
            if value:  # If the dictionary is not empty
                path_list.extend(json_to_path_list(value, new_path))
            else:  # If it's an empty dictionary, it's a file
                path_list.append(new_path)
        else:  # If it's not a dictionary, it's a file
            path_list.append(new_path)

    return path_list
