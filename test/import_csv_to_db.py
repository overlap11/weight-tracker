#!/usr/bin/env python3
"""
CSVファイルをデータベースにインポートするスクリプト
"""
import os
import pandas as pd
from datetime import datetime
from database import WeightDatabase

def import_csv_to_database():
    """CSVファイルをデータベースにインポート"""
    print("🚀 CSVファイルをデータベースにインポート開始")
    print("=" * 60)
    
    # ファイルパス
    csv_file = "weight_data_20250703.csv"
    db_path = "data/data.db"
    
    # CSVファイルの確認
    if not os.path.exists(csv_file):
        print(f"❌ CSVファイル '{csv_file}' が見つかりません")
        return False
    
    try:
        # CSVファイルを読み込み
        df = pd.read_csv(csv_file)
        print(f"📊 CSVファイル読み込み成功: {len(df)}件")
        
        # データベースに接続
        db = WeightDatabase(db_path)
        print("✅ データベース接続成功")
        
        # インポート前の状態確認
        before_count = db.get_record_count()
        print(f"📊 インポート前のレコード数: {before_count}件")
        
        # データをインポート
        print("\n📥 CSVデータをインポート中...")
        success_count = 0
        error_count = 0
        update_count = 0
        
        for index, row in df.iterrows():
            try:
                date_str = str(row['date'])
                weight = float(row['weight'])
                body_fat = float(row['body_fat']) if pd.notna(row['body_fat']) else None
                
                # 既存データチェック
                existing = db.get_measurement_by_date(date_str)
                
                if existing:
                    # 既存データを更新
                    if db.update_measurement_by_date(date_str, weight, body_fat):
                        update_count += 1
                    else:
                        error_count += 1
                else:
                    # 新規データを追加
                    if db.add_measurement(date_str, weight, body_fat):
                        success_count += 1
                    else:
                        error_count += 1
                
                # 進捗表示
                if (index + 1) % 100 == 0:
                    print(f"   処理済み: {index + 1}/{len(df)}")
                    
            except Exception as e:
                print(f"❌ 行{index + 1}のエラー: {str(e)}")
                error_count += 1
        
        # インポート後の状態確認
        after_count = db.get_record_count()
        print(f"\n📊 インポート完了:")
        print(f"   - 新規追加: {success_count}件")
        print(f"   - 更新: {update_count}件")
        print(f"   - エラー: {error_count}件")
        print(f"   - インポート後レコード数: {after_count}件")
        
        # データ範囲の確認
        all_data = db.get_measurements()
        if not all_data.empty:
            print(f"\n📅 データ範囲:")
            print(f"   最古: {all_data['date'].min()}")
            print(f"   最新: {all_data['date'].max()}")
            
            # 統計情報
            stats = db.get_statistics(30)
            print(f"\n📊 統計情報 (30日):")
            for key, value in stats.items():
                print(f"   {key}: {value}")
        
        return success_count > 0 or update_count > 0
        
    except Exception as e:
        print(f"❌ インポートエラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = import_csv_to_database()
    if success:
        print("\n✅ CSVインポートが完了しました")
    else:
        print("\n❌ CSVインポートに失敗しました") 