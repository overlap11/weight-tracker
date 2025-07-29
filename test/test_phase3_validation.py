#!/usr/bin/env python3
"""
Phase 3: 拡張バリデーション機能のテストスクリプト
"""

import pandas as pd
from datetime import datetime, date, timedelta
from database import WeightDatabase
from advanced_validation import AdvancedValidator, ValidationLevel
import sys
import os

def test_advanced_validation():
    """拡張バリデーション機能のテスト"""
    print("🧪 Phase 3: 拡張バリデーション機能テストを開始...")
    
    try:
        # データベース初期化
        db = WeightDatabase()
        validator = AdvancedValidator(db)
        print("✅ データベース・バリデーター初期化成功")
        
        # 現在のデータ状況確認
        df = db.get_measurements(10)
        print(f"✅ 現在のデータ件数: {len(df)}件")
        
        if df.empty:
            print("⚠️ テストデータがありません。サンプルデータを作成します...")
            create_test_data(db)
            df = db.get_measurements(10)
        
        # テストケース1: 体重変化分析
        print("\n📊 テストケース1: 体重変化分析")
        test_date = date.today().strftime("%Y-%m-%d")
        
        # 正常な変化
        normal_weight = 70.0
        results = validator.validate_weight_change(test_date, normal_weight, 18.0)
        print(f"   正常な体重変化: {len(results)}件の結果")
        for result in results:
            print(f"   - {result.level.value}: {result.message}")
        
        # 異常な変化（大幅増加）
        abnormal_weight = 80.0
        results = validator.validate_weight_change(test_date, abnormal_weight, 18.0)
        print(f"   異常な体重変化: {len(results)}件の結果")
        for result in results:
            print(f"   - {result.level.value}: {result.message}")
        
        # テストケース2: 統計的異常値検出
        print("\n📈 テストケース2: 統計的異常値検出")
        
        # 正常値
        normal_weight = 70.0
        results = validator.validate_statistical_outlier(test_date, normal_weight, 18.0)
        print(f"   正常値: {len(results)}件の結果")
        for result in results:
            print(f"   - {result.level.value}: {result.message}")
        
        # 異常値
        outlier_weight = 50.0
        results = validator.validate_statistical_outlier(test_date, outlier_weight, 18.0)
        print(f"   異常値: {len(results)}件の結果")
        for result in results:
            print(f"   - {result.level.value}: {result.message}")
        
        # テストケース3: トレンド一貫性
        print("\n📉 テストケース3: トレンド一貫性チェック")
        
        normal_weight = 69.0
        results = validator.validate_trend_consistency(test_date, normal_weight)
        print(f"   トレンド一貫性: {len(results)}件の結果")
        for result in results:
            print(f"   - {result.level.value}: {result.message}")
        
        # テストケース4: 測定条件チェック
        print("\n🕐 テストケース4: 測定条件チェック")
        
        results = validator.validate_measurement_conditions(test_date, 70.0, 18.0)
        print(f"   測定条件: {len(results)}件の結果")
        for result in results:
            print(f"   - {result.level.value}: {result.message}")
        
        # テストケース5: 推奨値取得
        print("\n💡 テストケース5: 推奨値取得")
        
        recommendations = validator.get_recommended_values(test_date)
        print(f"   推奨値: {len(recommendations)}項目")
        for key, value in recommendations.items():
            print(f"   - {key}: {value}")
        
        # テストケース6: 包括的バリデーション
        print("\n🔍 テストケース6: 包括的バリデーション")
        
        validation_results = validator.comprehensive_validation(test_date, 70.0, 18.0)
        summary = validator.get_validation_summary(validation_results)
        
        print(f"   総チェック数: {summary['total_checks']}")
        print(f"   情報: {summary['info_count']}")
        print(f"   警告: {summary['warning_count']}")
        print(f"   エラー: {summary['error_count']}")
        
        # 詳細結果表示
        print("\n📋 詳細バリデーション結果:")
        for category, results in validation_results.items():
            if results:
                print(f"   {category}:")
                for result in results:
                    print(f"     - {result.level.value}: {result.message}")
                    if result.suggestion:
                        print(f"       💡 {result.suggestion}")
        
        print("\n✅ 拡張バリデーション機能テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_test_data(db):
    """テスト用のサンプルデータを作成"""
    print("📊 テスト用サンプルデータを作成中...")
    
    # 30日分のデータを作成
    base_date = date.today() - timedelta(days=30)
    base_weight = 70.0
    base_body_fat = 18.0
    
    for i in range(30):
        test_date = base_date + timedelta(days=i)
        
        # 微妙な変動を加える
        weight_variation = (i % 7 - 3) * 0.2  # ±0.6kg程度の変動
        body_fat_variation = (i % 5 - 2) * 0.3  # ±0.6%程度の変動
        
        test_weight = base_weight + weight_variation + (i * -0.05)  # 全体的に微減
        test_body_fat = base_body_fat + body_fat_variation
        
        db.add_measurement(
            test_date.strftime("%Y-%m-%d"),
            round(test_weight, 1),
            round(test_body_fat, 1)
        )
    
    print(f"✅ テスト用データ作成完了: 30件")

def test_validation_edge_cases():
    """バリデーションのエッジケースをテスト"""
    print("\n🔍 エッジケーステスト...")
    
    try:
        db = WeightDatabase()
        validator = AdvancedValidator(db)
        
        # 空のデータベースでのテスト
        empty_db = WeightDatabase(':memory:')
        empty_validator = AdvancedValidator(empty_db)
        
        test_date = date.today().strftime("%Y-%m-%d")
        
        # 空のデータベース
        print("   📊 空のデータベースでのテスト:")
        results = empty_validator.validate_weight_change(test_date, 70.0, 18.0)
        print(f"     - 体重変化分析: {len(results)}件")
        
        results = empty_validator.validate_statistical_outlier(test_date, 70.0, 18.0)
        print(f"     - 統計的異常値: {len(results)}件")
        
        # 極端な値でのテスト
        print("   🔥 極端な値でのテスト:")
        results = validator.validate_weight_change(test_date, 50.0, 5.0)
        print(f"     - 極端な体重変化: {len(results)}件")
        
        results = validator.validate_statistical_outlier(test_date, 90.0, 30.0)
        print(f"     - 極端な統計的異常: {len(results)}件")
        
        print("✅ エッジケーステスト完了")
        return True
        
    except Exception as e:
        print(f"❌ エッジケーステストエラー: {str(e)}")
        return False

def test_performance():
    """パフォーマンステスト"""
    print("\n⚡ パフォーマンステスト...")
    
    try:
        import time
        
        db = WeightDatabase()
        validator = AdvancedValidator(db)
        
        test_date = date.today().strftime("%Y-%m-%d")
        
        # 100回の包括的バリデーション実行
        start_time = time.time()
        
        for i in range(100):
            validator.comprehensive_validation(test_date, 70.0 + i * 0.01, 18.0)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 100
        
        print(f"   📊 100回実行:")
        print(f"     - 総時間: {total_time:.3f}秒")
        print(f"     - 平均時間: {avg_time:.3f}秒")
        print(f"     - 1秒あたり: {1/avg_time:.1f}回")
        
        # パフォーマンス判定
        if avg_time < 0.1:
            print("   ✅ パフォーマンス: 優秀")
        elif avg_time < 0.5:
            print("   ✅ パフォーマンス: 良好")
        else:
            print("   ⚠️ パフォーマンス: 改善が必要")
        
        return True
        
    except Exception as e:
        print(f"❌ パフォーマンステストエラー: {str(e)}")
        return False

def main():
    """メインテスト実行"""
    print("🚀 Phase 3 拡張バリデーション機能 包括テスト開始\n")
    
    tests = [
        ("基本機能テスト", test_advanced_validation),
        ("エッジケーステスト", test_validation_edge_cases),
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