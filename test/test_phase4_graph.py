#!/usr/bin/env python3
"""
Phase 4 グラフ描画機能 テストスクリプト
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import plotly.graph_objects as go
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import WeightDatabase
from main import create_weight_graph, calculate_moving_average, filter_data_by_period

def test_database_initialization():
    """データベース初期化テスト"""
    print("🧪 データベース初期化テスト...")
    try:
        # テスト用一時データベースファイル
        import tempfile
        temp_db = tempfile.mktemp(suffix='.db')
        db = WeightDatabase(temp_db)
        
        # テーブルの存在確認
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"   作成されたテーブル: {[table[0] for table in tables]}")
        
        print("✅ データベース初期化成功")
        return db
    except Exception as e:
        print(f"❌ データベース初期化失敗: {str(e)}")
        return None

def create_test_data(db):
    """テスト用データの作成"""
    print("🧪 テストデータ作成...")
    
    # 過去30日間のテストデータを作成
    base_date = date.today() - timedelta(days=30)
    base_weight = 70.0
    base_body_fat = 20.0
    
    test_records = []
    for i in range(30):
        # 日付
        test_date = base_date + timedelta(days=i)
        
        # 体重（微小な変動を追加）
        weight_variation = np.random.normal(0, 0.5)  # 標準偏差0.5kgの変動
        trend = -0.05 * i  # 緩やかな減少傾向
        weight = base_weight + trend + weight_variation
        
        # 体脂肪率（体重と相関）
        body_fat_variation = np.random.normal(0, 0.8)
        body_fat = base_body_fat + (weight - base_weight) * 0.2 + body_fat_variation
        
        # データベースに追加
        success = db.add_measurement(
            test_date.strftime("%Y-%m-%d"),
            round(weight, 1),
            round(body_fat, 1)
        )
        
        if success:
            test_records.append({
                'date': test_date,
                'weight': weight,
                'body_fat': body_fat
            })
    
    print(f"✅ {len(test_records)}件のテストデータを作成")
    return test_records

def test_moving_average_calculation():
    """移動平均計算テスト"""
    print("🧪 移動平均計算テスト...")
    
    # サンプルデータ
    test_data = pd.DataFrame({
        'date': pd.date_range('2025-01-01', periods=10, freq='D'),
        'weight': [70.0, 70.5, 69.8, 70.2, 69.5, 70.1, 69.9, 70.3, 69.7, 70.0],
        'body_fat': [20.0, 20.2, 19.8, 20.1, 19.9, 20.0, 19.7, 20.2, 19.8, 20.1]
    })
    
    try:
        result = calculate_moving_average(test_data, window=7)
        
        # 移動平均が計算されているかチェック
        if 'weight_ma' in result.columns and 'body_fat_ma' in result.columns:
            print("✅ 移動平均計算成功")
            print(f"   元データ数: {len(test_data)}")
            print(f"   移動平均データ数: {len(result)}")
            print(f"   体重移動平均範囲: {result['weight_ma'].min():.1f} - {result['weight_ma'].max():.1f}kg")
            print(f"   体脂肪率移動平均範囲: {result['body_fat_ma'].min():.1f} - {result['body_fat_ma'].max():.1f}%")
            return True
        else:
            print("❌ 移動平均カラムが見つかりません")
            return False
    except Exception as e:
        print(f"❌ 移動平均計算失敗: {str(e)}")
        return False

def test_period_filtering():
    """期間フィルタリングテスト"""
    print("🧪 期間フィルタリングテスト...")
    
    # 30日間のサンプルデータ
    test_data = pd.DataFrame({
        'date': pd.date_range('2025-01-01', periods=30, freq='D'),
        'weight': np.random.normal(70, 1, 30),
        'body_fat': np.random.normal(20, 2, 30)
    })
    
    test_cases = [
        ("7日間", 7),
        ("30日間", 30),
        ("全期間", None)
    ]
    
    results = []
    for period_name, period_days in test_cases:
        try:
            filtered_data = filter_data_by_period(test_data, period_days)
            expected_length = period_days if period_days else len(test_data)
            
            if period_days is None:
                actual_length = len(filtered_data)
            else:
                actual_length = len(filtered_data)
            
            print(f"   {period_name}: {actual_length}件のデータ")
            results.append(actual_length > 0)
            
        except Exception as e:
            print(f"   ❌ {period_name}フィルタリング失敗: {str(e)}")
            results.append(False)
    
    if all(results):
        print("✅ 期間フィルタリング成功")
        return True
    else:
        print("❌ 期間フィルタリング失敗")
        return False

def test_graph_creation():
    """グラフ作成テスト"""
    print("🧪 グラフ作成テスト...")
    
    # サンプルデータ
    test_data = pd.DataFrame({
        'date': pd.date_range('2025-01-01', periods=14, freq='D'),
        'weight': np.random.normal(70, 1, 14),
        'body_fat': np.random.normal(20, 2, 14)
    })
    
    test_cases = [
        ("空データ", pd.DataFrame()),
        ("少量データ", test_data.head(3)),
        ("通常データ", test_data),
        ("体脂肪率なし", test_data.drop('body_fat', axis=1))
    ]
    
    results = []
    for case_name, data in test_cases:
        try:
            fig = create_weight_graph(data, 14)
            
            # 基本的なグラフ属性チェック
            has_layout = fig.layout is not None
            
            # 空データの場合は特別扱い
            if case_name == "空データ":
                # 空データでもレイアウトがあればOK
                test_passed = has_layout
            else:
                # 通常データの場合はトレースも必要
                has_data = len(fig.data) > 0
                test_passed = has_data and has_layout
            
            print(f"   {case_name}: トレース数={len(fig.data)}, レイアウト={has_layout}")
            results.append(test_passed)
            
        except Exception as e:
            print(f"   ❌ {case_name}グラフ作成失敗: {str(e)}")
            results.append(False)
    
    if all(results):
        print("✅ グラフ作成成功")
        return True
    else:
        print("❌ グラフ作成失敗")
        return False

def test_graph_features():
    """グラフ機能詳細テスト"""
    print("🧪 グラフ機能詳細テスト...")
    
    # 十分なデータでテスト
    test_data = pd.DataFrame({
        'date': pd.date_range('2025-01-01', periods=20, freq='D'),
        'weight': np.random.normal(70, 1, 20),
        'body_fat': np.random.normal(20, 2, 20)
    })
    
    try:
        fig = create_weight_graph(test_data, 20)
        
        # トレース数の確認
        trace_names = [trace.name for trace in fig.data]
        print(f"   トレース: {trace_names}")
        
        # 期待されるトレース
        expected_traces = ['体重', '7日移動平均', '体脂肪率']
        
        # 体重と移動平均は必須
        required_traces = ['体重', '7日移動平均']
        has_required = all(trace in trace_names for trace in required_traces)
        
        # 体脂肪率トレース（オプション）
        has_body_fat = any('体脂肪率' in trace for trace in trace_names)
        
        # Y軸の確認
        has_dual_y = fig.layout.yaxis2 is not None if has_body_fat else True
        
        print(f"   必須トレース: {has_required}")
        print(f"   体脂肪率トレース: {has_body_fat}")
        print(f"   双軸レイアウト: {has_dual_y}")
        
        if has_required and has_dual_y:
            print("✅ グラフ機能詳細テスト成功")
            return True
        else:
            print("❌ グラフ機能詳細テスト失敗")
            return False
            
    except Exception as e:
        print(f"❌ グラフ機能詳細テスト失敗: {str(e)}")
        return False

def test_database_integration():
    """データベース統合テスト"""
    print("🧪 データベース統合テスト...")
    
    try:
        # テスト用一時データベースファイル
        import tempfile
        temp_db = tempfile.mktemp(suffix='.db')
        db = WeightDatabase(temp_db)
        
        # テストデータ追加
        test_records = create_test_data(db)
        
        # 各期間でのデータ取得テスト
        periods = [7, 30, 90, None]
        
        for period in periods:
            df = db.get_measurements(period)
            
            if not df.empty:
                # グラフ作成テスト
                fig = create_weight_graph(df, period)
                
                period_name = f"{period}日間" if period else "全期間"
                print(f"   {period_name}: {len(df)}件のデータでグラフ作成成功")
            else:
                print(f"   {period}日間: データなし")
        
        print("✅ データベース統合テスト成功")
        return True
        
    except Exception as e:
        print(f"❌ データベース統合テスト失敗: {str(e)}")
        return False

def performance_test():
    """パフォーマンステスト"""
    print("🧪 パフォーマンステスト...")
    
    try:
        # 大量データでのテスト
        large_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=365, freq='D'),
            'weight': np.random.normal(70, 2, 365),
            'body_fat': np.random.normal(20, 3, 365)
        })
        
        import time
        
        # グラフ作成時間測定
        start_time = time.time()
        fig = create_weight_graph(large_data, 365)
        end_time = time.time()
        
        processing_time = end_time - start_time
        print(f"   365日データ: {processing_time:.3f}秒")
        
        # 移動平均計算時間測定
        start_time = time.time()
        df_with_ma = calculate_moving_average(large_data)
        end_time = time.time()
        
        ma_time = end_time - start_time
        print(f"   移動平均計算: {ma_time:.3f}秒")
        
        # 1秒以内であればOK
        if processing_time < 1.0 and ma_time < 1.0:
            print("✅ パフォーマンステスト成功")
            return True
        else:
            print("❌ パフォーマンステスト失敗（処理時間超過）")
            return False
            
    except Exception as e:
        print(f"❌ パフォーマンステスト失敗: {str(e)}")
        return False

def main():
    """メインテスト実行"""
    print("🚀 Phase 4 グラフ描画機能 包括テスト開始\n")
    
    print("=" * 60)
    print("🧪 基本機能テスト")
    print("=" * 60)
    
    # データベース初期化
    db = test_database_initialization()
    if not db:
        print("❌ データベース初期化に失敗しました")
        return
    
    # テストケース実行
    test_results = []
    
    # 1. 移動平均計算テスト
    test_results.append(test_moving_average_calculation())
    
    # 2. 期間フィルタリングテスト
    test_results.append(test_period_filtering())
    
    # 3. グラフ作成テスト
    test_results.append(test_graph_creation())
    
    # 4. グラフ機能詳細テスト
    test_results.append(test_graph_features())
    
    # 5. データベース統合テスト
    test_results.append(test_database_integration())
    
    print("\n" + "=" * 60)
    print("🧪 パフォーマンステスト")
    print("=" * 60)
    
    # 6. パフォーマンステスト
    test_results.append(performance_test())
    
    print("\n" + "=" * 60)
    print("📋 テスト結果サマリー")
    print("=" * 60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"✅ 基本機能テスト: {'成功' if test_results[0:5].count(True) == 5 else '失敗'}")
    print(f"✅ パフォーマンステスト: {'成功' if test_results[5] else '失敗'}")
    print(f"\n📊 総計: {passed}成功, {total-passed}失敗")
    
    if passed == total:
        print("🎉 全てのテストが成功しました！")
    else:
        print("⚠️  一部のテストが失敗しました。")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 