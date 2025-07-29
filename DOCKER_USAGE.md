# Docker実行手順

体重トラッカーアプリをDockerで実行する手順です。

## 前提条件

- Docker
- Docker Compose

## 実行方法

### 1. コンテナのビルドと起動

```bash
# プロジェクトディレクトリに移動
cd weight-tracker

# コンテナをビルドして起動
docker-compose up --build
```

### 2. アプリへのアクセス

ブラウザで以下のURLにアクセス：
```
http://localhost:8501
```

### 3. バックグラウンド実行

```bash
# バックグラウンドで起動
docker-compose up -d --build

# ログ確認
docker-compose logs -f weight-tracker

# 停止
docker-compose down
```

## データの永続化

- `./data/` ディレクトリがコンテナの `/app/data` にマウントされます
- SQLiteデータベースがホスト側に保存されるため、コンテナを再起動してもデータが保持されます

## トラブルシューティング

### ポート8501が使用中の場合

`docker-compose.yaml` の ports 設定を変更：
```yaml
ports:
  - "8502:8501"  # 8502など別のポートに変更
```

### コンテナの再ビルド

```bash
# イメージを削除してから再ビルド
docker-compose down
docker rmi weight-tracker_weight-tracker
docker-compose up --build
```

### ログの確認

```bash
# コンテナのログを確認
docker-compose logs weight-tracker

# リアルタイムでログを表示
docker-compose logs -f weight-tracker
```

## コマンド一覧

```bash
# 起動
docker-compose up

# バックグラウンド起動
docker-compose up -d

# 停止
docker-compose down

# 再起動
docker-compose restart

# ログ確認
docker-compose logs weight-tracker

# コンテナ内でbashを実行
docker-compose exec weight-tracker bash
``` 