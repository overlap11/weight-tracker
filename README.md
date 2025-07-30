# 体重トラッカー Webアプリ

個人PC内で完結する軽量な体重記録Webアプリケーションです。

## 機能

- **体重・体脂肪率の記録**: 日付、体重、体脂肪率を簡単に記録
- **グラフ表示**: 体重推移と7日移動平均の可視化
- **期間フィルタ**: 7日/30日/90日/全期間での表示切替
- **統計情報**: データ数、直近体重、移動平均、目標差分、体脂肪率
- **データ編集**: 記録したデータの編集・削除機能
- **目標体重設定**: 目標体重の設定と進捗確認
- **CSV管理**: データのインポート・エクスポート機能

## セットアップ

### 1. 必要な環境

- Python 3.10以上
- ブラウザ（Chrome, Firefox, Safari, Edge）

### 2. インストール・実行方法

#### 方法1: Docker実行（推奨）

```bash
# リポジトリをクローン（または展開）
cd weight-tracker

# Dockerコンテナでアプリを起動
docker-compose up --build

# ブラウザで http://localhost:8501 にアクセス
```

詳細な手順は `DOCKER_USAGE.md` を参照してください。

#### 方法2: Python直接実行

```bash
# リポジトリをクローン（または展開）
cd weight-tracker

# 仮想環境を作成
python -m venv venv

# 仮想環境をアクティベート
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt

# アプリケーションを起動
streamlit run main.py
```

ブラウザで `http://localhost:8501` にアクセスしてください。

## ディレクトリ構成

```
weight-tracker/
├── main.py                 # メインアプリケーション
├── database.py             # データベース操作ヘルパー
├── requirements.txt        # 依存関係
├── README.md              # このファイル
├── .gitignore             # Git除外設定
├── Dockerfile             # Dockerイメージ定義
├── docker-compose.yaml    # Docker Compose設定
├── .dockerignore          # Docker除外設定
├── DOCKER_USAGE.md        # Docker実行手順
├── data/                  # データ格納フォルダ
│   ├── .gitkeep          # フォルダ保持用ファイル
│   └── data.db           # SQLiteデータベース（自動生成）
├── sample_data/           # サンプルデータ
│   └── sample_weights.csv # サンプルデータ
└── doc/                   # ドキュメント
    ├── レイアウト修正要件.md
    ├── UI改善実行レポート_2025-01-12.md
    └── Phase1-8_実行レポート.md など
```

## 使用方法

### 基本的な使い方

1. **データの記録**: 
   - 日付を選択（デフォルト：今日）
   - 体重を入力（必須）
   - 体脂肪率を入力（任意）
   - 「記録」ボタンをクリック

2. **目標体重の設定**:
   - 目標体重を入力
   - 進捗バーで現在の達成度を確認

3. **データの確認**:
   - 統計情報で現在の状況を把握
   - 期間選択で表示範囲を調整
   - グラフで体重推移を視覚的に確認

4. **データの編集**:
   - データ編集セクションで過去のデータを修正・削除

5. **データ管理**:
   - CSVエクスポート: 全データをCSVファイルで出力
   - CSVインポート: 既存データをCSVファイルから読み込み

## トラブルシューティング

- **データベースエラー**: `data/data.db`ファイルの権限を確認
- **パッケージエラー**: `pip install -r requirements.txt`を再実行
- **ポートエラー**: 他のポート番号で起動 `streamlit run main.py --server.port 8502`
- **グラフが表示されない**: ブラウザのJavaScriptが有効か確認

## 開発情報

### 技術スタック
- **フレームワーク**: Streamlit 1.35+
- **データベース**: SQLite3
- **グラフライブラリ**: Plotly
- **データ処理**: Pandas

### 開発状況
- **Phase 1-8**: 基本機能実装完了
- **UI改善**: 2025年1月12日完了

### ファイル構成
- `main.py`: メインアプリケーション（1010行）
- `database.py`: データベース操作（449行）
- `doc/`: 開発ドキュメント・実行レポート
- `data/`: SQLiteデータベース格納 