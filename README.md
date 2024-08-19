# StructureSense

StructureSense 是一个用于自动整理和分类文件的工具。它可以将放置在“未归档”文件夹中的文件根据配置文件中的默认结构移动到相应的文件夹中,配合Alist使用会更好，只需要将整理的文件放置在未归档的文件夹中，每30分中会整理一次。

## 功能介绍

- 自动扫描指定目录下的“未归档”文件夹。
- 使用阿里通义千问 API 处理文件并确定其目标位置。
- 根据配置文件中的结构将文件移动到相应的文件夹中。
- 支持通过 Docker 运行，方便部署和管理。

## 使用方法

### 环境准备

1. 确保已经安装了 Docker。
2. 获取阿里通义千问的 API Key，可以在 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/apiKey)获取。

### 配置文件

在项目目录下，需要一个 `config.json` 文件来定义默认的文件结构。这个文件用于指导程序如何组织文件夹结构。

### 运行命令

使用下面的 Docker 命令来运行 StructureSense：

```bash
docker run -d --name StructureSense \
  -v /path/to/your/local/folder:/app/AllFiles \
  --restart=always \
  -e API_KEY=your_api_key_here \
  1269305589/structuresense:1.0.5
```

#### 参数说明

- `-d`: 以后台模式运行 Docker 容器。
- `--name StructureSense`: 为容器指定一个名称，便于管理。
- `-v /path/to/your/local/folder:/app/AllFiles`: 将主机上的本地目录挂载到容器内的 `/app/AllFiles` 目录。需要管理的文件应放在这个目录下。
- `--restart=always`: 设置容器在停止后自动重启。
- `-e API_KEY=your_api_key_here`: 设置环境变量 `API_KEY`，用于存储阿里通义千问的 API Key。
- `1269305589/structuresense:1.0.5`: 指定要使用的 Docker 镜像。

## 日志

日志文件将被存储在 `/app/AllFiles/log.txt` 中，记录了文件处理过程中的详细信息。

## 贡献

欢迎提交问题和功能请求。如果你想贡献代码，请 fork 本仓库并提交 pull request。

## 许可证

本项目采用 MIT 许可证开源。