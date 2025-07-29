#!/usr/bin/env python3
"""
データベースの状態を確認するデバッグスクリプト
"""
import os
import pandas as pd
from datetime import datetime
from database import WeightDatabase

def check_database_status():
    """データベースの状態を確認"""
    print("🔍 データベース状態確認")
    print("=" * 60)
    
    # 本番データベースのパス
    db_path = "data/data.db"
    
    print(f"📁 データベースファイル: {db_path}")
    print(f"📁 存在確認: {os.path.exists(db_path)}")
    
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        print(f"📁 ファイルサイズ: {file_size} bytes")
        print(f"📁 最終更新: {datetime.fromtimestamp(os.path.getmtime(db_path))}")
    else:
        print("❌ データベースファイルが見つかりません")
        return
    
    # データベースに接続
    try:
        db = WeightDatabase(db_path)
        print("✅ データベース接続成功")
        
        # データ数の確認
        record_count = db.get_record_count()
        print(f"📊 総レコード数: {record_count}件")
        
        if record_count > 0:
            # 最新のデータを取得
            recent_data = db.get_measurements(10)
            print(f"\n📋 最新の10件のデータ:")
            if not recent_data.empty:
                print(recent_data.tail(10)[['date', 'weight', 'body_fat']].to_string())
                
                # 日付範囲の確認
                print(f"\n📅 データの日付範囲:")
                print(f"   最古: {recent_data['date'].min()}")
                print(f"   最新: {recent_data['date'].max()}")
                
                # 統計情報
                print(f"\n📊 統計情報:")
                stats = db.get_statistics(30)
                for key, value in stats.items():
                    print(f"   {key}: {value}")
            else:
                print("❌ データの取得に失敗しました")
        else:
            print("⚠️ データベースにデータがありません")
            
    except Exception as e:
        print(f"❌ データベースエラー: {str(e)}")
        import traceback
        traceback.print_exc()

def check_csv_file():
    """CSVファイルの状態を確認"""
    print(f"\n🔍 CSVファイル状態確認")
    print("=" * 60)
    
    csv_file = "weight_data_20250703.csv"
    
    if os.path.exists(csv_file):
        print(f"📁 CSVファイル: {csv_file}")
        print(f"📁 ファイルサイズ: {os.path.getsize(csv_file)} bytes")
        
        try:
            df = pd.read_csv(csv_file)
            print(f"📊 CSVデータ:")
            print(f"   行数: {len(df)}")
            print(f"   列数: {len(df.columns)}")
            print(f"   列名: {list(df.columns)}")
            
            if len(df) > 0:
                print(f"   日付範囲: {df['date'].min()} ~ {df['date'].max()}")
                print(f"\n📋 先頭5行:")
                print(df.head().to_string())
                
        except Exception as e:
            print(f"❌ CSVファイル読み込みエラー: {str(e)}")
    else:
        print(f"❌ CSVファイル '{csv_file}' が見つかりません")

if __name__ == "__main__":
    check_database_status()
    check_csv_file() 