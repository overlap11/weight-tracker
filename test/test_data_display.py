#!/usr/bin/env python3
"""
修正後のデータ取得とフィルタリング処理をテストするスクリプト
"""
import pandas as pd
from datetime import datetime
from database import WeightDatabase

def filter_data_by_period(df: pd.DataFrame, period_days: int) -> pd.DataFrame:
    """期間でデータをフィルタリング"""
    if df.empty or period_days is None:
        return df
    
    # 最新の日付から指定日数分を取得
    end_date = df['date'].max()
    start_date = end_date - pd.Timedelta(days=period_days - 1)
    
    return df[df['date'] >= start_date]

def test_data_filtering():
    """データフィルタリングのテスト"""
    print("🔍 修正後のデータ取得テスト")
    print("=" * 60)
    
    db = WeightDatabase("data/data.db")
    
    # 全データを取得
    print("📊 全データを取得:")
    all_data = db.get_measurements()
    print(f"   総件数: {len(all_data)}")
    if not all_data.empty:
        print(f"   日付範囲: {all_data['date'].min()} ~ {all_data['date'].max()}")
    
    # 期間別フィルタリングテスト
    periods = [7, 30, 90]
    
    for period in periods:
        print(f"\n📊 過去{period}日間のデータ:")
        filtered_data = filter_data_by_period(all_data, period)
        
        if not filtered_data.empty:
            print(f"   件数: {len(filtered_data)}")
            print(f"   日付範囲: {filtered_data['date'].min()} ~ {filtered_data['date'].max()}")
            print(f"   体重範囲: {filtered_data['weight'].min():.1f}kg ~ {filtered_data['weight'].max():.1f}kg")
            
            # 最初と最後のデータを表示
            print("   最初の3件:")
            print(filtered_data.head(3)[['date', 'weight', 'body_fat']].to_string())
            print("   最後の3件:")
            print(filtered_data.tail(3)[['date', 'weight', 'body_fat']].to_string())
        else:
            print(f"   ⚠️ データなし")
    
    # 2023年のデータがフィルタリングに含まれるかテスト
    print(f"\n🔍 2023年データの確認:")
    data_2023 = all_data[all_data['date'].dt.year == 2023]
    print(f"   2023年データ数: {len(data_2023)}件")
    
    if len(data_2023) > 0:
        print(f"   2023年の日付範囲: {data_2023['date'].min()} ~ {data_2023['date'].max()}")
        
        # 90日間フィルタリングに2023年データが含まれるか
        filtered_90d = filter_data_by_period(all_data, 90)
        data_2023_in_90d = filtered_90d[filtered_90d['date'].dt.year == 2023]
        print(f"   90日間フィルタリング内の2023年データ: {len(data_2023_in_90d)}件")
        
        # 365日間フィルタリングに2023年データが含まれるか
        filtered_365d = filter_data_by_period(all_data, 365)
        data_2023_in_365d = filtered_365d[filtered_365d['date'].dt.year == 2023]
        print(f"   365日間フィルタリング内の2023年データ: {len(data_2023_in_365d)}件")

def test_graph_data():
    """グラフ用データ取得のテスト"""
    print(f"\n🔍 グラフ用データ取得テスト")
    print("=" * 60)
    
    db = WeightDatabase("data/data.db")
    
    # 修正前の方法（期間指定で最新N件を取得）
    print("📊 修正前の方法（最新30件）:")
    old_method_data = db.get_measurements(30)
    if not old_method_data.empty:
        print(f"   件数: {len(old_method_data)}")
        print(f"   日付範囲: {old_method_data['date'].min()} ~ {old_method_data['date'].max()}")
    
    # 修正後の方法（全データ取得 + 期間フィルタリング）
    print("\n📊 修正後の方法（全データ + 30日フィルタリング）:")
    all_data = db.get_measurements()
    new_method_data = filter_data_by_period(all_data, 30)
    if not new_method_data.empty:
        print(f"   件数: {len(new_method_data)}")
        print(f"   日付範囲: {new_method_data['date'].min()} ~ {new_method_data['date'].max()}")
        
        # データの違いを比較
        print(f"\n🔍 データの違い:")
        print(f"   修正前: {len(old_method_data)}件")
        print(f"   修正後: {len(new_method_data)}件")
        print(f"   差分: {len(new_method_data) - len(old_method_data)}件")

if __name__ == "__main__":
    test_data_filtering()
    test_graph_data() 