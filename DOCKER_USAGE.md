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

- **Named Volume使用**: `weight-tracker_data` というnamed volumeでSQLiteデータベースを永続化
- **自動作成**: 初回起動時にDockerが自動でボリュームを作成
- **データ保持**: コンテナを削除してもデータが保持されます
- **Sample Data**: `./sample_data` ディレクトリは引き続きバインドマウント

## ボリューム管理

### ボリューム確認
```bash
# 作成されたボリューム一覧を確認
docker volume ls

# weight-tracker_dataボリュームの詳細確認
docker volume inspect weight-tracker_data
```

### ホストでの保存場所
Named volumeの実際のデータ保存場所（Windows WSL2環境）：
```
\\wsl.localhost\docker-desktop\mnt\docker-desktop-disk\data\docker\volumes\weight-tracker_data\_data
```

**注意**: 
- この場所への直接アクセスは推奨されません
- データの操作は以下のDockerコマンドを使用してください
- パスはDocker Desktop の設定やOSによって異なる場合があります

### データのバックアップ・復元
```bash
# データをバックアップ
docker run --rm -v weight-tracker_data:/data -v $(pwd):/backup alpine tar czf /backup/weight_tracker_backup.tar.gz -C /data .

# データを復元
docker run --rm -v weight-tracker_data:/data -v $(pwd):/backup alpine tar xzf /backup/weight_tracker_backup.tar.gz -C /data
```

### データのリセット
```bash
# アプリを停止
docker-compose down

# ボリュームを削除（データが完全に削除されます）
docker volume rm weight-tracker_data

# 再起動（新しいボリュームが作成されます）
docker-compose up --build
```

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

### データボリュームの問題

```bash
# ボリュームの状態確認
docker volume inspect weight-tracker_data

# ボリュームの使用状況確認
docker system df -v
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

# ボリューム管理
docker volume ls
docker volume inspect weight-tracker_data
docker volume rm weight-tracker_data
``` 