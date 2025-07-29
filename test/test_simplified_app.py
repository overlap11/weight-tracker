#!/usr/bin/env python3
"""
簡略化されたアプリケーションのテストスクリプト
"""

import pandas as pd
from datetime import datetime, date
from database import WeightDatabase
import sys
import os

def test_simplified_app():
    """簡略化されたアプリケーションのテスト"""
    print("🧪 簡略化アプリケーションテストを開始...")
    
    try:
        # データベース初期化
        db = WeightDatabase()
        print("✅ データベース初期化成功")
        
        # 現在のデータ状況確認
        df = db.get_measurements(10)
        print(f"✅ 現在のデータ件数: {len(df)}件")
        
        # 推奨値機能のテスト
        print("\n💡 推奨値機能テスト:")
        
        # main.pyからget_simple_recommendations関数をインポート
        from main import get_simple_recommendations
        
        recommendations = get_simple_recommendations(db)
        
        if recommendations:
            print(f"   ✅ 推奨値取得成功:")
            for key, value in recommendations.items():
                print(f"     - {key}: {value}")
        else:
            print("   ⚠️ 推奨値データが不足")
        
        # 基本バリデーション機能のテスト
        print("\n📝 基本バリデーション機能テスト:")
        
        from main import validate_weight, validate_body_fat, validate_date
        
        # 体重バリデーション
        valid, msg = validate_weight(70.0)
        print(f"   体重70.0kg: {'✅' if valid else '❌'} {msg}")
        
        valid, msg = validate_weight(5.0)
        print(f"   体重5.0kg: {'✅' if valid else '❌'} {msg}")
        
        # 体脂肪率バリデーション
        valid, msg = validate_body_fat(18.0)
        print(f"   体脂肪率18.0%: {'✅' if valid else '❌'} {msg}")
        
        valid, msg = validate_body_fat(110.0)
        print(f"   体脂肪率110.0%: {'✅' if valid else '❌'} {msg}")
        
        # 日付バリデーション
        valid, msg = validate_date(date.today())
        print(f"   今日の日付: {'✅' if valid else '❌'} {msg}")
        
        # データベース操作テスト
        print("\n💾 データベース操作テスト:")
        
        test_date = date.today().strftime("%Y-%m-%d")
        test_weight = 69.0
        test_body_fat = 18.5
        
        # 既存データチェック
        existing = db.get_measurement_by_date(test_date)
        if existing:
            print(f"   既存データ存在: {test_date}")
        else:
            print(f"   新規データとして追加可能: {test_date}")
        
        # 統計情報取得
        stats = db.get_statistics(30)
        if stats:
            print(f"   統計情報取得成功:")
            print(f"     平均体重: {stats['weight_avg']:.1f}kg")
            print(f"     変化量: {stats['weight_change']:+.1f}kg")
            print(f"     トレンド: {stats['trend']}")
        else:
            print("   統計情報取得失敗")
        
        print("\n✅ 簡略化アプリケーションテスト完了")
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_performance():
    """パフォーマンステスト"""
    print("\n⚡ パフォーマンステスト...")
    
    try:
        import time
        from main import get_simple_recommendations
        
        db = WeightDatabase()
        
        # 100回の推奨値取得実行
        start_time = time.time()
        
        for i in range(100):
            get_simple_recommendations(db)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 100
        
        print(f"   📊 100回実行:")
        print(f"     - 総時間: {total_time:.3f}秒")
        print(f"     - 平均時間: {avg_time:.3f}秒")
        print(f"     - 1秒あたり: {1/avg_time:.1f}回")
        
        # パフォーマンス判定
        if avg_time < 0.01:
            print("   ✅ パフォーマンス: 優秀")
        elif avg_time < 0.05:
            print("   ✅ パフォーマンス: 良好")
        else:
            print("   ⚠️ パフォーマンス: 改善が必要")
        
        return True
        
    except Exception as e:
        print(f"❌ パフォーマンステストエラー: {str(e)}")
        return False

def main():
    """メインテスト実行"""
    print("🚀 簡略化アプリケーション テスト開始\n")
    
    tests = [
        ("基本機能テスト", test_simplified_app),
        ("パフォーマンステスト", test_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print("="*60)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}で予期しないエラー: {str(e)}")
            results.append((test_name, False))
    
    # 結果サマリー
    print(f"\n{'='*60}")
    print("📋 テスト結果サマリー")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        if result:
            print(f"✅ {test_name}: 成功")
            passed += 1
        else:
            print(f"❌ {test_name}: 失敗")
            failed += 1
    
    print(f"\n📊 総計: {passed}成功, {failed}失敗")
    
    if failed == 0:
        print("🎉 全てのテストが成功しました！")
        return 0
    else:
        print("⚠️ 一部のテストで問題が発生しました。")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 