#!/usr/bin/env python3
"""
データベースの全データを詳細に確認するスクリプト
"""
import sqlite3
import pandas as pd
from datetime import datetime

def check_database_details():
    """データベースの詳細を確認"""
    print("🔍 データベース詳細確認")
    print("=" * 60)
    
    db_path = "data/data.db"
    
    try:
        # 直接SQLiteで確認
        conn = sqlite3.connect(db_path)
        
        # 全データを取得
        query = """
        SELECT date, weight, body_fat, created_at, updated_at
        FROM measurements 
        ORDER BY date ASC
        """
        df = pd.read_sql_query(query, conn)
        
        print(f"📊 総レコード数: {len(df)}件")
        
        if len(df) > 0:
            print(f"📅 実際のデータ範囲:")
            print(f"   最古: {df['date'].min()}")
            print(f"   最新: {df['date'].max()}")
            
            # 最初の10件
            print(f"\n📋 最初の10件:")
            print(df.head(10)[['date', 'weight', 'body_fat']].to_string())
            
            # 最後の10件
            print(f"\n📋 最後の10件:")
            print(df.tail(10)[['date', 'weight', 'body_fat']].to_string())
            
            # 年別データ数
            df['year'] = pd.to_datetime(df['date']).dt.year
            year_counts = df['year'].value_counts().sort_index()
            print(f"\n📊 年別データ数:")
            for year, count in year_counts.items():
                print(f"   {year}年: {count}件")
            
            # 2023年のデータをサンプル表示
            df_2023 = df[df['year'] == 2023]
            if len(df_2023) > 0:
                print(f"\n📋 2023年のデータ（最初の5件）:")
                print(df_2023.head(5)[['date', 'weight', 'body_fat']].to_string())
        
        conn.close()
        
    except Exception as e:
        print(f"❌ データベースエラー: {str(e)}")
        import traceback
        traceback.print_exc()

def check_database_schema():
    """データベースのスキーマを確認"""
    print(f"\n🔍 データベーススキーマ確認")
    print("=" * 60)
    
    db_path = "data/data.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # テーブル一覧
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 テーブル一覧: {[table[0] for table in tables]}")
        
        # measurementsテーブルの構造
        cursor.execute("PRAGMA table_info(measurements)")
        columns = cursor.fetchall()
        print(f"\n📊 measurementsテーブル構造:")
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        # インデックス情報
        cursor.execute("PRAGMA index_list(measurements)")
        indexes = cursor.fetchall()
        print(f"\n📊 インデックス: {[idx[1] for idx in indexes]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ スキーマ確認エラー: {str(e)}")

if __name__ == "__main__":
    check_database_details()
    check_database_schema() 