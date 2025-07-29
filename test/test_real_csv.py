#!/usr/bin/env python3
"""
実際のCSVファイルを使用したCSV機能テスト
weight_data_20250703.csv（621行）を使用してテスト
"""
import sqlite3
import os
import pandas as pd
from datetime import datetime
import sys

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# データベースクラスをインポート
from database import WeightDatabase

def test_real_csv_import():
    """実際のCSVファイルを使用してインポート機能をテスト"""
    print("=" * 60)
    print("実際のCSVファイル（weight_data_20250703.csv）を使用したテスト")
    print("=" * 60)
    
    # テスト用データベースファイル
    test_db = "test_real_csv.db"
    
    # 既存のテストDBがあれば削除
    if os.path.exists(test_db):
        os.remove(test_db)
    
    # データベース初期化
    db = WeightDatabase(test_db)
    print(f"✅ テストデータベース '{test_db}' を初期化しました")
    
    # CSVファイルのパス
    csv_file = "weight_data_20250703.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSVファイル '{csv_file}' が見つかりません")
        return False
    
    # CSVファイルの基本情報を確認
    df = pd.read_csv(csv_file)
    print(f"📊 CSVファイル情報:")
    print(f"   - 行数: {len(df)}")
    print(f"   - 列数: {len(df.columns)}")
    print(f"   - 列名: {list(df.columns)}")
    print(f"   - 期間: {df['date'].min()} ~ {df['date'].max()}")
    
    # 現在のデータベース状態を確認
    existing_data = db.get_measurements()
    print(f"🗄️  既存データ数: {len(existing_data)}件")
    
    # CSVデータをインポート
    print("\n📥 CSVデータをインポート中...")
    try:
        # CSVファイルを読み込み
        csv_df = pd.read_csv(csv_file)
        
        # カラム名を確認してマッピング
        print(f"📋 CSVカラム: {list(csv_df.columns)}")
        
        # body_fat列がない場合の処理
        if 'body_fat' not in csv_df.columns:
            csv_df['body_fat'] = None
        
        # データベースにインポート
        success_count, duplicate_count = db.import_from_csv(csv_df)
        
        print(f"✅ CSVインポート完了:")
        print(f"   - 成功: {success_count}件")
        print(f"   - 重複: {duplicate_count}件")
        
        # インポート後のデータベース状態を確認
        all_data = db.get_measurements()
        print(f"🗄️  インポート後データ数: {len(all_data)}件")
        
        # 統計情報を表示
        if len(all_data) > 0:
            print("\n📊 統計情報:")
            stats_7d = db.get_statistics(7)
            stats_30d = db.get_statistics(30)
            stats_90d = db.get_statistics(90)
            
            print(f"   - 7日間統計: {stats_7d}")
            print(f"   - 30日間統計: {stats_30d}")
            print(f"   - 90日間統計: {stats_90d}")
        
        return True
        
    except Exception as e:
        print(f"❌ CSVインポートエラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_csv_export():
    """CSVエクスポート機能をテスト"""
    print("\n" + "=" * 60)
    print("CSVエクスポート機能テスト")
    print("=" * 60)
    
    test_db = "test_real_csv.db"
    
    if not os.path.exists(test_db):
        print("❌ テストデータベースが見つかりません")
        return False
    
    # エクスポート実行
    try:
        db = WeightDatabase(test_db)
        export_df = db.export_to_csv()
        
        if not export_df.empty:
            # エクスポートファイルとして保存
            export_file = f"exported_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            export_df.to_csv(export_file, index=False)
            
            print(f"✅ CSVエクスポート成功:")
            print(f"   - ファイル: {export_file}")
            print(f"   - 行数: {len(export_df)}")
            print(f"   - 列数: {len(export_df.columns)}")
            print(f"   - ファイルサイズ: {os.path.getsize(export_file)} bytes")
            
            # 最初の5行を表示
            print("\n📋 エクスポートデータ（最初の5行）:")
            print(export_df.head().to_string())
            
            # ファイルを削除
            os.remove(export_file)
            print(f"🗑️  テストファイル '{export_file}' を削除しました")
            
            return True
        else:
            print("❌ エクスポートデータがありません")
            return False
            
    except Exception as e:
        print(f"❌ CSVエクスポートエラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_duplicate_handling():
    """重複データ処理のテスト"""
    print("\n" + "=" * 60)
    print("重複データ処理テスト")
    print("=" * 60)
    
    test_db = "test_real_csv.db"
    csv_file = "weight_data_20250703.csv"
    
    if not os.path.exists(test_db):
        print("❌ テストデータベースが見つかりません")
        return False
    
    # 現在のデータ数を確認
    db = WeightDatabase(test_db)
    existing_data = db.get_measurements()
    print(f"🗄️  既存データ数: {len(existing_data)}件")
    
    # 同じCSVファイルを再度インポート（重複チェック）
    print("\n📥 同じCSVファイルを再度インポート（重複チェック）...")
    try:
        # CSVファイルを読み込み
        csv_df = pd.read_csv(csv_file)
        
        # body_fat列がない場合の処理
        if 'body_fat' not in csv_df.columns:
            csv_df['body_fat'] = None
        
        # データベースにインポート
        success_count, duplicate_count = db.import_from_csv(csv_df)
        
        print(f"✅ 重複チェック結果:")
        print(f"   - 成功: {success_count}件")
        print(f"   - 重複: {duplicate_count}件")
        
        # データ数が変わっていないことを確認
        after_data = db.get_measurements()
        print(f"🗄️  重複チェック後データ数: {len(after_data)}件")
        
        if len(existing_data) == len(after_data):
            print("✅ 重複処理が正常に動作しています")
            return True
        else:
            print("❌ 重複処理に問題があります")
            return False
            
    except Exception as e:
        print(f"❌ 重複チェックエラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def cleanup():
    """テストファイルの削除"""
    test_db = "test_real_csv.db"
    if os.path.exists(test_db):
        os.remove(test_db)
        print(f"🗑️  テストデータベース '{test_db}' を削除しました")

def main():
    """メインテスト実行"""
    print("🚀 実際のCSVファイルを使用したCSV機能テスト開始")
    print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    try:
        # テスト1: CSVインポート
        result1 = test_real_csv_import()
        test_results.append(("CSVインポート", result1))
        
        # テスト2: CSVエクスポート
        result2 = test_csv_export()
        test_results.append(("CSVエクスポート", result2))
        
        # テスト3: 重複データ処理
        result3 = test_duplicate_handling()
        test_results.append(("重複データ処理", result3))
        
        # 結果サマリー
        print("\n" + "=" * 60)
        print("テスト結果サマリー")
        print("=" * 60)
        
        success_count = 0
        for test_name, result in test_results:
            status = "✅ 成功" if result else "❌ 失敗"
            print(f"{test_name}: {status}")
            if result:
                success_count += 1
        
        print(f"\n総合結果: {success_count}/{len(test_results)}件成功")
        
        if success_count == len(test_results):
            print("🎉 全テストが成功しました！")
        else:
            print("⚠️  一部テストが失敗しました")
            
    except Exception as e:
        print(f"❌ テスト実行エラー: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # クリーンアップ
        cleanup()
        print(f"⏰ 終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 