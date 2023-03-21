import os

current = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, '/')
env_path = current + "/.env"

PYTHON_MODULE_CV2_PATH = "PYTHON_MODULE_CV2_PATH"

if os.path.exists(env_path) :
    with open(env_path) as f:
        for line in f:
            key, value = line.strip().split("=")
            os.environ[key] = value
else :
    print(env_path + "が存在しません。")

def get_cv2_path() :
    cv_path = os.getenv(PYTHON_MODULE_CV2_PATH)
    if cv_path is None :
        print(env_path + "に" + PYTHON_MODULE_CV2_PATH + "が設定されていません。")
        return None
    elif cv_path == "" :
        print(env_path + "の" + PYTHON_MODULE_CV2_PATH + "にパスが設定されていません。")
        return None
    else :
        return cv_path