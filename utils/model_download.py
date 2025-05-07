import os
import json
import requests

try:
    from modelscope import snapshot_download
    print("√ modelscope")
except ImportError:
    try:
        from huggingface_hub import snapshot_download
        print("√ huggingface_hub")
    except ImportError:
        raise ImportError(
            "Need modelscope or huggingface_hub\n"
            "pip install modelscope  # or\n"
            "pip install huggingface_hub"
        )

current_dir = os.path.dirname(os.path.abspath(__file__))

# Pdf mineru
def download_json(url):
    # 下载JSON文件
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
def download_and_modify_json(url, local_filename, modifications):
    if os.path.exists(local_filename):
        data = json.load(open(local_filename))
        config_version = data.get('config_version', '0.0.0')
        if config_version < '1.2.0':
            data = download_json(url)
    else:
        data = download_json(url)

    for key, value in modifications.items():
        data[key] = value

    # 保存修改后的内容
    with open(local_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
def download_pdf_model():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_storage = os.path.join(current_dir, "..", "models", "mineru")
    config_path = os.path.join(current_dir, "..", "config")
    os.makedirs(model_storage, exist_ok=True)
    os.makedirs(config_path, exist_ok=True)

    mineru_patterns = [
        # "models/Layout/LayoutLMv3/*",
        "models/Layout/YOLO/*",
        "models/MFD/YOLO/*",
        "models/MFR/unimernet_hf_small_2503/*",
        "models/OCR/paddleocr_torch/*",
        # "models/TabRec/TableMaster/*",
        # "models/TabRec/StructEqTable/*",
    ]
    model_dir = snapshot_download(
        'opendatalab/PDF-Extract-Kit-1.0', 
        local_dir=model_storage,
        allow_patterns=mineru_patterns
        )
    layoutreader_model_dir = snapshot_download(
        'ppaanngggg/layoutreader',
        local_dir=model_storage
        )
    model_dir = model_dir + '/models'
    print(f'model_dir is: {model_dir}')
    print(f'layoutreader_model_dir is: {layoutreader_model_dir}')

    # paddleocr_model_dir = model_dir + '/OCR/paddleocr'
    # user_paddleocr_dir = os.path.expanduser('~/.paddleocr')
    # if os.path.exists(user_paddleocr_dir):
    #     shutil.rmtree(user_paddleocr_dir)
    # shutil.copytree(paddleocr_model_dir, user_paddleocr_dir)

    json_url = 'https://gcore.jsdelivr.net/gh/opendatalab/MinerU@master/magic-pdf.template.json'
    config_file_name = 'magic-pdf.json'
    home_dir = os.path.expanduser('~')
    config_file = os.path.join(home_dir, config_file_name)

    json_mods = {
        'models-dir': model_dir,
        'layoutreader-model-dir': layoutreader_model_dir,
    }

    download_and_modify_json(json_url, config_file, json_mods)
    print(f'The configuration file has been configured successfully, the path is: {config_file}')

# Embedding model
def download_embedding():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_dir = model_name.split("/")[-1]
    download_dir = os.path.join(current_dir, "..", "models", model_dir)

    try:
        snapshot_download(
            repo_id=model_name,
            local_dir=download_dir,
            max_workers=8,
            # allow_patterns="Qwen3-30B-A3B-Q4_K_M.gguf",
            ignore_patterns=["onnx/", "openvino/"],
        )
        print("Model files downloaded successfully.")
        return True
    except Exception as e:
        print(f"Error downloading model files: {e}")
        return False

# Qwen3
def download_model():
    model_name = "lmstudio-community/Qwen3-30B-A3B-GGUF"
    download_dir = os.path.join(current_dir, "..", "models")

    try:
        snapshot_download(
            repo_id=model_name,
            local_dir=download_dir,
            allow_patterns="Qwen3-30B-A3B-Q4_K_M.gguf"
        )
        print("Model files downloaded successfully.")
        return True
    except Exception as e:
        print(f"Error downloading model files: {e}")
        return False

if __name__ == "__main__":
    download_embedding()
    download_model()