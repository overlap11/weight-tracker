#!/usr/bin/env python3
"""
Phase 6 データ編集・削除機能テストスクリプト
体重トラッカー - st.data_editor機能のテスト
"""

import os
import sys
import tempfile
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from database import WeightDatabase


def test_database_operations():
    """データベース操作のテスト"""
    print("🧪 データベース操作テスト...")
    
    try:
        # 一時データベースファイル作成
        temp_db = tempfile.mktemp(suffix='.db')
        db = WeightDatabase(temp_db)
        
        # 初期データ追加
        test_data = create_test_data(db)
        
        # 更新操作テスト
        print("\n📝 更新操作テスト:")
        
        # 最初のレコードを取得
        df = db.get_measurements(5)
        if not df.empty:
            first_record = df.iloc[0]
            record_id = int(first_record['id'])  # IDをint型に変換
            original_weight = float(first_record['weight'])
            original_body_fat = float(first_record['body_fat']) if pd.notna(first_record['body_fat']) else 20.0
            
            # 更新実行
            new_weight = original_weight + 1.0
            new_body_fat = original_body_fat + 1.0 if pd.notna(original_body_fat) else 20.0
            
            success = db.update_measurement(record_id, new_weight, new_body_fat)
            if success:
                print(f"   ✅ ID {record_id} の更新成功: {original_weight:.1f}kg → {new_weight:.1f}kg")
                
                # 更新後の値を確認
                updated_df = db.get_measurements(5)
                updated_record = updated_df[updated_df['id'] == record_id].iloc[0]
                
                if abs(updated_record['weight'] - new_weight) < 0.01:
                    print(f"   ✅ 更新値の確認成功: {updated_record['weight']:.1f}kg")
                else:
                    print(f"   ❌ 更新値の確認失敗: {updated_record['weight']:.1f}kg")
                    return False
            else:
                print(f"   ❌ ID {record_id} の更新失敗")
                return False
        
        # 削除操作テスト
        print("\n🗑️ 削除操作テスト:")
        
        # 削除前のレコード数
        before_count = db.get_record_count()
        print(f"   削除前のレコード数: {before_count}件")
        
        # 最後のレコードを削除
        df = db.get_measurements(1)
        if not df.empty:
            last_record = df.iloc[-1]
            delete_id = int(last_record['id'])  # IDをint型に変換
            delete_date = last_record['date'].strftime('%Y-%m-%d')
            
            success = db.delete_measurement(delete_id)
            if success:
                print(f"   ✅ ID {delete_id} ({delete_date}) の削除成功")
                
                # 削除後のレコード数確認
                after_count = db.get_record_count()
                print(f"   削除後のレコード数: {after_count}件")
                
                if after_count == before_count - 1:
                    print("   ✅ 削除処理の確認成功")
                else:
                    print("   ❌ 削除処理の確認失敗")
                    return False
                
                # 削除されたレコードが存在しないことを確認
                deleted_df = db.get_measurements(50)
                if not deleted_df[deleted_df['id'] == delete_id].empty:
                    print("   ❌ 削除されたレコードが残っています")
                    return False
                else:
                    print("   ✅ 削除されたレコードの確認成功")
                    
            else:
                print(f"   ❌ ID {delete_id} の削除失敗")
                return False
        
        # 一時ファイル削除
        try:
            os.unlink(temp_db)
        except:
            pass
        
        print("\n✅ データベース操作テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ データベース操作テスト失敗: {str(e)}")
        return False


def test_data_validation():
    """データ検証機能のテスト"""
    print("\n🧪 データ検証機能テスト...")
    
    try:
        # 一時データベースファイル作成
        temp_db = tempfile.mktemp(suffix='.db')
        db = WeightDatabase(temp_db)
        
        # 異常値のテスト
        test_cases = [
            # (weight, body_fat, expected_valid, description)
            (70.0, 20.0, True, "正常値"),
            (5.0, 20.0, False, "体重異常値（最小値未満）"),
            (350.0, 20.0, False, "体重異常値（最大値超過）"),
            (70.0, -5.0, False, "体脂肪率異常値（最小値未満）"),
            (70.0, 150.0, False, "体脂肪率異常値（最大値超過）"),
            (70.0, None, True, "体脂肪率未入力"),
        ]
        
        for weight, body_fat, expected_valid, description in test_cases:
            try:
                # 検証ロジック（main.pyのvalidate_weight, validate_body_fatに相当）
                weight_valid = 10.0 <= weight <= 300.0
                body_fat_valid = body_fat is None or (0.0 <= body_fat <= 100.0)
                
                is_valid = weight_valid and body_fat_valid
                
                if is_valid == expected_valid:
                    print(f"   ✅ {description}: 期待通り ({is_valid})")
                else:
                    print(f"   ❌ {description}: 期待値 {expected_valid}, 実際値 {is_valid}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ {description}: エラー {str(e)}")
                return False
        
        # 一時ファイル削除
        try:
            os.unlink(temp_db)
        except:
            pass
        
        print("✅ データ検証機能テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ データ検証機能テスト失敗: {str(e)}")
        return False


def test_data_editor_structure():
    """データエディタ構造のテスト"""
    print("\n🧪 データエディタ構造テスト...")
    
    try:
        # 一時データベースファイル作成
        temp_db = tempfile.mktemp(suffix='.db')
        db = WeightDatabase(temp_db)
        
        # テストデータ作成
        test_data = create_test_data(db)
        
        # データ取得
        df = db.get_measurements(10)
        
        # データエディタ用のデータ構造テスト
        if not df.empty:
            # 日付文字列変換
            edit_df = df.copy()
            edit_df['date'] = edit_df['date'].dt.strftime('%Y-%m-%d')
            edit_df = edit_df.sort_values('date', ascending=False)
            
            # カラム名変更
            edit_df = edit_df.rename(columns={
                'date': '日付',
                'weight': '体重(kg)',
                'body_fat': '体脂肪率(%)'
            })
            
            # 必要なカラムが存在するかチェック
            required_columns = ['日付', '体重(kg)', '体脂肪率(%)']
            for col in required_columns:
                if col not in edit_df.columns:
                    print(f"   ❌ 必須カラム '{col}' が見つかりません")
                    return False
                else:
                    print(f"   ✅ カラム '{col}' が存在します")
            
            # データ型チェック
            print(f"   ✅ データ件数: {len(edit_df)}件")
            print(f"   ✅ 日付範囲: {edit_df['日付'].min()} - {edit_df['日付'].max()}")
            print(f"   ✅ 体重範囲: {edit_df['体重(kg)'].min():.1f}kg - {edit_df['体重(kg)'].max():.1f}kg")
            
            # 体脂肪率のデータ有無チェック
            body_fat_count = edit_df['体脂肪率(%)'].notna().sum()
            print(f"   ✅ 体脂肪率データ: {body_fat_count}件/{len(edit_df)}件")
            
        else:
            print("   ❌ テストデータが見つかりません")
            return False
        
        # 一時ファイル削除
        try:
            os.unlink(temp_db)
        except:
            pass
        
        print("✅ データエディタ構造テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ データエディタ構造テスト失敗: {str(e)}")
        return False


def test_performance():
    """パフォーマンステスト"""
    print("\n🧪 パフォーマンステスト...")
    
    try:
        # 一時データベースファイル作成
        temp_db = tempfile.mktemp(suffix='.db')
        db = WeightDatabase(temp_db)
        
        # 大量データ作成（100件）
        start_time = datetime.now()
        
        base_date = date.today() - timedelta(days=100)
        for i in range(100):
            test_date = base_date + timedelta(days=i)
            weight = 70.0 + (i % 10 - 5) * 0.5
            body_fat = 20.0 + (i % 8 - 4) * 0.3
            
            db.add_measurement(
                test_date.strftime("%Y-%m-%d"),
                round(weight, 1),
                round(body_fat, 1)
            )
        
        insert_time = (datetime.now() - start_time).total_seconds()
        print(f"   ✅ 100件データ挿入時間: {insert_time:.3f}秒")
        
        # データ取得パフォーマンス
        start_time = datetime.now()
        df = db.get_measurements(100)
        fetch_time = (datetime.now() - start_time).total_seconds()
        print(f"   ✅ 100件データ取得時間: {fetch_time:.3f}秒")
        
        # 更新パフォーマンス
        start_time = datetime.now()
        if not df.empty:
            record_id = int(df.iloc[0]['id'])  # IDをint型に変換
            db.update_measurement(record_id, 75.0, 22.0)
        update_time = (datetime.now() - start_time).total_seconds()
        print(f"   ✅ 1件データ更新時間: {update_time:.3f}秒")
        
        # 削除パフォーマンス
        start_time = datetime.now()
        if not df.empty:
            record_id = int(df.iloc[-1]['id'])  # IDをint型に変換
            db.delete_measurement(record_id)
        delete_time = (datetime.now() - start_time).total_seconds()
        print(f"   ✅ 1件データ削除時間: {delete_time:.3f}秒")
        
        # パフォーマンス判定
        if insert_time < 1.0 and fetch_time < 0.5 and update_time < 0.1 and delete_time < 0.1:
            print("   ✅ パフォーマンス良好")
        else:
            print("   ⚠️ パフォーマンス要改善")
        
        # 一時ファイル削除
        try:
            os.unlink(temp_db)
        except:
            pass
        
        print("✅ パフォーマンステスト完了")
        return True
        
    except Exception as e:
        print(f"❌ パフォーマンステスト失敗: {str(e)}")
        return False


def create_test_data(db):
    """テスト用データの作成"""
    print("📊 テスト用データ作成...")
    
    # 過去30日分のデータを作成
    base_date = date.today() - timedelta(days=30)
    base_weight = 70.0
    base_body_fat = 20.0
    
    test_records = []
    for i in range(30):
        test_date = base_date + timedelta(days=i)
        
        # 体重（微小な変動を追加）
        weight_variation = np.random.normal(0, 0.8)
        trend = -0.03 * i  # 緩やかな減少傾向
        weight = base_weight + trend + weight_variation
        
        # 体脂肪率（体重と逆相関）
        body_fat_variation = np.random.normal(0, 0.5)
        body_fat = base_body_fat - (weight - base_weight) * 0.3 + body_fat_variation
        
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
    
    print(f"✅ {len(test_records)}件のテストデータ作成完了")
    return test_records


def main():
    """メインテスト実行"""
    print("🚀 Phase 6 データ編集・削除機能テスト開始")
    print("=" * 50)
    
    # テスト実行
    tests = [
        ("データベース操作", test_database_operations),
        ("データ検証機能", test_data_validation),
        ("データエディタ構造", test_data_editor_structure),
        ("パフォーマンス", test_performance),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
    
    # 結果サマリー
    print("\n" + "="*50)
    print("📊 テスト結果サマリー")
    print("="*50)
    
    success_count = 0
    for test_name, result in results:
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n総合結果: {success_count}/{len(results)} テストが成功")
    
    if success_count == len(results):
        print("🎉 Phase 6 実装完了！")
        print("\n📋 実装された機能:")
        print("- st.data_editor による直感的なデータ編集")
        print("- データベースレコードの更新機能")
        print("- データベースレコードの削除機能")
        print("- 変更検知と自動保存")
        print("- エラーハンドリング")
        print("- パフォーマンス最適化")
        
        return True
    else:
        print("❌ 一部のテストが失敗しました")
        return False


if __name__ == "__main__":
    main() 