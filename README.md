# 体重トラッカー Webアプリ

個人PC内で完結する軽量な体重記録Webアプリケーションです。

## 機能

- 体重・体脂肪率の日次記録
- 7日移動平均を含む体重推移グラフ
- 期間別フィルタ（7日/30日/90日/全期間）
- データ編集・削除機能
- 目標体重設定と進捗表示
- 統計情報表示
- CSV インポート/エクスポート

## セットアップ

### 1. 必要な環境

- Python 3.10以上
- ブラウザ（Chrome, Firefox, Safari, Edge）

### 2. インストール

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
```

### 3. 実行

```bash
# アプリケーションを起動
streamlit run main.py
```

ブラウザで `http://localhost:8501` にアクセスしてください。

## ディレクトリ構成

```
weight-tracker/
├── main.py                 # メインアプリケーション
├── database.py             # データベース操作ヘルパー
├── utils.py                # ユーティリティ関数
├── requirements.txt        # 依存関係
├── README.md              # このファイル
├── data/                  # データ格納フォルダ
│   └── data.db           # SQLiteデータベース（自動生成）
└── sample_data/           # サンプルデータ
    └── sample_weights.csv # サンプルデータ
```

## 使用方法

1. **データ入力**: 日付、体重、体脂肪率を入力して記録
2. **グラフ表示**: 体重推移と7日移動平均を可視化
3. **期間フィルタ**: 表示期間を選択して確認
4. **データ編集**: 過去のデータを編集・削除
5. **目標設定**: 目標体重を設定して進捗を確認
6. **データ管理**: CSVファイルでデータのインポート/エクスポート

## トラブルシューティング

- **データベースエラー**: `data/data.db`ファイルの権限を確認
- **パッケージエラー**: `pip install -r requirements.txt`を再実行
- **ポートエラー**: 他のポート番号で起動 `streamlit run main.py --server.port 8502`

## 開発情報

- **フレームワーク**: Streamlit
- **データベース**: SQLite3
- **グラフライブラリ**: Plotly
- **データ処理**: Pandas 