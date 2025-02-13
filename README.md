# 项目介绍

`img-immigrate` 是一个用于将 Markdown 文件中的本地图片上传到 OSS（对象存储服务）并更新图片路径的工具。它还支持从云端下载图片并重新上传到指定的 OSS。

## 功能

- 上传本地 Markdown 文件中的图片到 OSS 并更新路径
- 从云端下载图片并上传到指定的 OSS
- 支持排除特定文件夹
- 支持调试模式和日志记录

## 使用说明

### 环境配置

1. 确保已安装 Python 3.x。
2. 安装所需的 Python 库：
    ```bash
    pip install requests
    ```

### 配置文件

在项目根目录下创建 `oss-config.json` 文件，内容如下：
```json
{
    "access_key_id": "your_access_key_id",
    "access_key_secret": "your_access_key_secret",
    "endpoint": "your_oss_endpoint",
    "bucket_name": "your_bucket_name"
}
```

### 运行脚本

1. 修改 `md_image_to_oss.py` 文件中的配置项：
    ```python
    config_path = r"E:\root\oss\oss-config.json"
    old_md_folder_path = r"E:\temp\agiantii-notebook-local-gitee"
    target_md_folder_path = r"E:\temp\anote"
    oss_directory = "anote/"
    ```

2. 运行脚本：
    ```bash
    python md_image_to_oss.py
    ```

### 调试模式

如果需要启用调试模式，可以将 `is_debug` 设置为 `True`：
```python
is_debug = True
```

### 日志记录

脚本会在当前目录下生成 `img_log.txt` 和 `md_log.txt` 文件，记录处理过的图片和 Markdown 文件。

### 注意事项

- 请确保 OSS 配置文件中的信息正确无误。
- 请确保本地文件路径和目标文件路径存在且可写。

