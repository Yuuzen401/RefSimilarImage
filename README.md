# RefSimilarImage
RefSimilarImageはblenderのアドオンです。

View3D内のスクリーン または 指定の画像ファイルを使用して、
ローカルディレクトリの画像を参照し、類似度が高い画像を複数取得します。

![image](https://user-images.githubusercontent.com/124477558/226545964-4e0d0bbd-3f6b-49aa-85de-09566885b060.png)

## Usage

1. 前提として自身の環境の python と cv2 を使用します。
cv2（OpenCV）の性能はGPUに依存するため処理に時間がかかる場合があります。

また、「BlendRef」というblenderのアドオンが必要です。
複数の画像出力する仕組みとして、Sreeraj氏が制作したBlendRefのノードに対して外部から画像追加します。
以下からダウンロードが必要です。
https://theunnecessarythings.gumroad.com/l/YoCr

<br>

2. 画像検証にはPythonモジュールのCV2を使用しますが、これはblenderのPythonには内臓されていないため、外部参照する必要があります。
外部参照先は自身のホストのpythonになります。

```
$ pip install opencv-python

Collecting opencv-python
  Downloading opencv_python-4.7.0.72-cp37-abi3-win_amd64.whl (38.2 MB)
     ---------------------------------------- 38.2/38.2 MB 6.4 MB/s eta 0:00:00
Requirement already satisfied: numpy>=1.21.2 in c:\python311\lib\site-packages (from opencv-python) (1.24.2)
Installing collected packages: opencv-python
Successfully installed opencv-python-4.7.0.72

# pip の インストール先を覚えておく
c:\python311\lib\site-packages
```
<br>

3. RefSimilarImage のインストール後、アドオンがインストールされたフォルダにて、.env.exampleからファイルコピーし、.envファイルを作成後、CV2を参照する外部パスをenvに設定する。

```
# アドオンの場所の例
C:\Users\{Users}\AppData\Roaming\Blender Foundation\Blender\3.4\scripts\addons\RefSimilarImage

# 変名
.env.example
↓↓↓
.env

# envの設定例
PYTHON_MODULE_CV2_PATH=C:\Python311\Lib\site-packages\cv2
```

#### 動作
versionは3.4でのみ確認を行っています。
