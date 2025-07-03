#!/usr/bin/env python3
"""
get_measurementsメソッドの動作をテストするスクリプト
"""
from database import WeightDatabase
import pandas as pd

def test_get_measurements():
    """get_measurementsメソッドのテスト"""
    print("🔍 get_measurementsメソッドのテスト")
    print("=" * 60)
    
    db = WeightDatabase("data/data.db")
    
    # 全データを取得
    print("📊 全データを取得:")
    all_data = db.get_measurements()
    print(f"   総件数: {len(all_data)}")
    if not all_data.empty:
        print(f"   日付範囲: {all_data['date'].min()} ~ {all_data['date'].max()}")
    
    # 最新の10件を取得
    print("\n📊 最新の10件を取得:")
    recent_10 = db.get_measurements(10)
    print(f"   件数: {len(recent_10)}")
    if not recent_10.empty:
        print(f"   日付範囲: {recent_10['date'].min()} ~ {recent_10['date'].max()}")
        print("   データ:")
        print(recent_10[['date', 'weight', 'body_fat']].to_string())
    
    # 最新の30件を取得
    print("\n📊 最新の30件を取得:")
    recent_30 = db.get_measurements(30)
    print(f"   件数: {len(recent_30)}")
    if not recent_30.empty:
        print(f"   日付範囲: {recent_30['date'].min()} ~ {recent_30['date'].max()}")
        print("   最初の5件:")
        print(recent_30.head(5)[['date', 'weight', 'body_fat']].to_string())
        print("   最後の5件:")
        print(recent_30.tail(5)[['date', 'weight', 'body_fat']].to_string())

if __name__ == "__main__":
    test_get_measurements() 