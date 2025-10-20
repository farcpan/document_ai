# AWS Lambda Python 3.11ベース
FROM public.ecr.aws/lambda/python:3.11

# 必要なライブラリをインストール
RUN yum install -y gcc gcc-c++ make
RUN yum install -y mesa-libGL ffmpeg libsm6 libxext6 cmake
RUN pip install --upgrade pip setuptools wheel

# 作業ディレクトリ
WORKDIR /var/task

# 依存ライブラリをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# コードとモデルをコピー
COPY . .

# Lambdaハンドラ設定
CMD ["app.handler"]
