# ベースイメージとして軽量なPython 3.11を使用
FROM python:3.11-slim

# OSレベルで ffmpeg をインストールし、クリーンアップしてイメージサイズを抑える（Render/Railway対策の要）
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# ライブラリの要件ファイルをコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのすべてのファイルをコピー
COPY . .

# 公開するポート
EXPOSE 8080

# 本番用サーバー(gunicorn)で起動するコマンド。少し長めのタイムアウトを設定。
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app", "--timeout", "120"]
