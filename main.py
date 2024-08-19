# -*- coding: utf-8 -*-
import os
import json
import logging
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from functools import lru_cache
from utils.dashscope_api_helper import process_file
from utils.folder_structure_utils import (
    get_folder_structure, load_config, extract_filenames, move_file,
    json_to_path_list, create_and_merge_folder_structure
)

# 设置控制台编码（仅在 Windows 环境下需要）
if sys.platform.startswith('win'):
    import codecs
    import locale

    if sys.version_info[0] < 3:
        sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
    else:
        sys.stdout.reconfigure(encoding='utf-8')

# 日志目录和文件路径
log_directory = '/app/AllFiles'
log_file_path = os.path.join(log_directory, "log.txt")

# 检查日志目录是否存在，如果不存在则创建
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)


@lru_cache(maxsize=None)
def load_folder_structure(base_path, max_depth):
    return get_folder_structure(base_path, max_depth, True)


def get_other_files_list(base_path):
    other_files_json = get_folder_structure(os.path.join(base_path, "未归档"), 1)
    return extract_filenames(other_files_json)


def initialize_folder_structure(config):
    folder_path = '/app/AllFiles'  # 使用挂载的路径
    depth = config.get('max_depth', 3)

    json_structure = get_folder_structure(folder_path, depth)
    logging.info("Current folder structure:")
    logging.info(json_structure)

    new_structure = config.get('default_structure', {})
    new_structure_json = json.dumps(new_structure, indent=2)
    merged_structure = create_and_merge_folder_structure(new_structure_json, folder_path)
    logging.info("Merged structure:")
    logging.info(merged_structure)


def process_and_move_files():
    config = load_config()
    base_path = '/app/AllFiles'
    max_depth = config.get('max_depth', 4)
    api_key = os.environ.get('API_KEY', "sk-98696fd339be4ba7a33eee8e4b14ce42")

    other_files_list = get_other_files_list(base_path)
    json_structure = load_folder_structure(base_path, max_depth)
    for file_name in other_files_list:
        try:
            # 调用 process_file 并打印结果
            result = process_file(file_name, json_structure, api_key)
            if not result:
                logging.error(f"Empty result from process_file for {file_name}")
                continue

            # 打印返回的 JSON 字符串
            logging.info(f"Result from process_file for {file_name}: {result}")

            result_json = json.loads(result)
            result_list = json_to_path_list(result_json)

            logging.info(f"Recommended structure for {file_name}:")
            for path in result_list:
                source = os.path.join(base_path, "未归档", file_name)
                destination = os.path.join(base_path, path)
                move_file(source, destination)
                logging.info(f"Moved {file_name} to {path}")
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error for {file_name}: {str(e)}")
        except Exception as e:
            logging.error(f"Error processing {file_name}: {str(e)}")


def main():
    # 加载配置
    config = load_config()

    # 初始化文件夹结构
    initialize_folder_structure(config)

    # 创建调度器
    scheduler = BlockingScheduler()

    # 添加定时任务
    scheduler.add_job(process_and_move_files, 'interval', minutes=30)

    # 启动调度器
    logging.info("Starting scheduler...")
    scheduler.start()


if __name__ == '__main__':
    main()
