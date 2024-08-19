from http import HTTPStatus
import dashscope

from utils.folder_structure_utils import move_file


def call_dashscope_api(input_content, api_key):
    dashscope.api_key = api_key

    messages = [
        {'role': 'system', 'content': '''You are an expert file management and classification assistant. Your tasks include:
    1. Analyzing file names and extensions to determine their content and type.
    2. Organizing files into logical folder structures based on their content, type, and relationships.
    3. Utilizing existing folder structures when appropriate.
    4. Creating new folders only when necessary, using clear and descriptive Chinese names.
    5. Maintaining a balance between organization and simplicity, avoiding overly complex directory structures.
    6. Ensuring that the maximum folder depth does not exceed the specified limit.
    7. Providing recommendations in a clear, structured JSON format.

    Your goal is to create an intuitive, efficient, and user-friendly file organization system.'''},
        {'role': 'user', 'content': input_content}
    ]

    response = dashscope.Generation.call(
        dashscope.Generation.Models.qwen_plus,
        messages=messages,
        result_format='message',
    )

    if response.status_code == HTTPStatus.OK:
        # 直接返回 content 内容
        return response.output.choices[0].message.content
    else:
        error_message = f'Request id: {response.request_id}, Status code: {response.status_code}, error code: {response.code}, error message: {response.message}'
        return f"Error: {error_message}"


def generate_user_input(json_structure, file_name):
    return f"""
        任务：根据现有文件结构，为新文件推荐合适的存放位置。

        现有文件结构：
        {json_structure}

        需要整理的文件名如下：
        {file_name}

        请根据以下规则推荐文件存放位置：
        1. 优先使用现有文件夹结构，尽量避免创建新文件夹。
        2. 如果确实需要新文件夹，应在适当位置创建，并确保其名称简洁明了地描述内容。
        3. 所有文件夹名称使用中文。
        4. 识别文件名中的关键信息（如类型、主题、系列、创作者等），据此进行分类。
        5. 对特定内容类型（如视频、音频、文档等）进行适当的细分类。
        6. 保持分类的一致性，相似类型的文件应放在同一层级。
        7. 对于系列内容（如电视剧、系列电影等），创建以系列名称命名的子文件夹，将所有相关文件放入其中。
        8. 如果识别到文件属于某个系列，即使现有结构中没有该系列的文件夹，也应创建相应的文件夹。
        9. 如果现有结构确实没有合适位置，可以在根目录下创建新的文件夹，但应谨慎使用此选项。
        10. 如果实在无法分类，请将文件放在"其他"文件夹下面。

        请提供 JSON 格式的推荐结构，不要输出任何其他解释性文字。JSON 结构应该反映建议的文件位置，例如：
        {{
          "视频": {{
              "电视剧": {{
                  "国产剧": {{
                      "大明王朝1566": ["大明王朝1566HD1080P02.mkv", "大明王朝1566HD1080P09.mkv"]
                  }},
                  "美剧": {{
                      "权力的游戏": ["权力的游戏S01E01.mp4", "权力的游戏S01E02.mp4"]
                  }}
              }},
              "电影": {{
                  "科幻": ["星际穿越.mp4"],
                  "动作": ["速度与激情9.mp4"]
              }},
              "纪录片": {{
                  "自然": ["BBC-蓝色星球.mp4"]
              }}
          }},
          "音频": {{
              "音乐": {{
                  "流行": ["周杰伦 - 稻香.mp3"]
              }},
              "有声书": ["哈利波特与魔法石.mp3"]
          }},
          "文档": {{
              "学习资料": ["Python基础教程.pdf"]
          }},
          "其他": ["未分类文件.txt"]
        }}
        """


def process_file(file_name, json_structure, api_key):
    user_input = generate_user_input(json_structure, file_name)
    return call_dashscope_api(user_input, api_key)
