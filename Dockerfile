# Streamlit体重トラッカーアプリ実行用Dockerfile
FROM python:3.10-slim

# 環境変数設定
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

# 作業ディレクトリ設定
WORKDIR /app

# システムパッケージの最小限インストール（ヘルスチェック用curl含む）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

# Pythonパッケージの依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY main.py database.py ./

# データディレクトリ作成
RUN mkdir -p data sample_data

# サンプルデータをコピー（存在する場合）
COPY sample_data/ ./sample_data/

# ポート8501を公開（Streamlitデフォルトポート）
EXPOSE 8501

# Streamlitアプリを起動
CMD ["streamlit", "run", "main.py", "--server.address", "0.0.0.0", "--server.port", "8501"] 