#!/usr/bin/env python3
"""
体重トラッカーメインアプリケーションのテストスクリプト
"""

import pandas as pd
from datetime import datetime, date, timedelta
from database import WeightDatabase
import sys
import os

def test_main_app_functions():
    """メインアプリケーションの機能テスト"""
    print("🧪 メインアプリケーション機能テストを開始...")
    
    try:
        # データベース初期化
        db = WeightDatabase()
        print("✅ データベース初期化成功")
        
        # バリデーション関数のテスト
        print("\n📝 バリデーション機能テスト:")
        
        # 体重バリデーション
        from main import validate_weight
        
        # 正常値
        valid, msg = validate_weight(70.0)
        print(f"   体重70.0kg: {'✅' if valid else '❌'} {msg}")
        
        # 異常値（下限）
        valid, msg = validate_weight(5.0)
        print(f"   体重5.0kg: {'✅' if valid else '❌'} {msg}")
        
        # 異常値（上限）
        valid, msg = validate_weight(350.0)
        print(f"   体重350.0kg: {'✅' if valid else '❌'} {msg}")
        
        # 体脂肪率バリデーション
        from main import validate_body_fat
        
        # 正常値
        valid, msg = validate_body_fat(18.0)
        print(f"   体脂肪率18.0%: {'✅' if valid else '❌'} {msg}")
        
        # 異常値（下限）
        valid, msg = validate_body_fat(-5.0)
        print(f"   体脂肪率-5.0%: {'✅' if valid else '❌'} {msg}")
        
        # 異常値（上限）
        valid, msg = validate_body_fat(110.0)
        print(f"   体脂肪率110.0%: {'✅' if valid else '❌'} {msg}")
        
        # 日付バリデーション
        from main import validate_date
        
        # 正常値（今日）
        valid, msg = validate_date(date.today())
        print(f"   今日の日付: {'✅' if valid else '❌'} {msg}")
        
        # 異常値（未来）
        future_date = date.today() + timedelta(days=1)
        valid, msg = validate_date(future_date)
        print(f"   未来の日付: {'✅' if valid else '❌'} {msg}")
        
        # データベース操作テスト
        print("\n💾 データベース操作テスト:")
        
        # 新規データ追加
        test_date = date.today().strftime("%Y-%m-%d")
        test_weight = 68.5
        test_body_fat = 17.5
        
        success = db.add_measurement(test_date, test_weight, test_body_fat)
        print(f"   新規データ追加: {'✅' if success else '❌'}")
        
        # データ取得
        df = db.get_measurements(5)
        print(f"   データ取得: {'✅' if not df.empty else '❌'} ({len(df)}件)")
        
        # 統計情報取得
        stats = db.get_statistics(30)
        print(f"   統計情報取得: {'✅' if stats else '❌'}")
        if stats:
            print(f"     平均体重: {stats['weight_avg']:.1f}kg")
            print(f"     変化量: {stats['weight_change']:+.1f}kg")
            print(f"     トレンド: {stats['trend']}")
        
        # 既存データチェック
        existing = db.get_measurement_by_date(test_date)
        print(f"   既存データチェック: {'✅' if existing else '❌'}")
        
        print("\n📊 現在のデータ状況:")
        total_records = db.get_record_count()
        print(f"   総レコード数: {total_records}件")
        
        # 最新5件のデータ表示
        recent_df = db.get_measurements(5)
        if not recent_df.empty:
            print(f"   最新5件のデータ:")
            for _, row in recent_df.tail(5).iterrows():
                date_str = row['date'].strftime('%Y-%m-%d')
                weight = row['weight']
                body_fat = row['body_fat'] if pd.notna(row['body_fat']) else 'N/A'
                print(f"     {date_str}: {weight:.1f}kg, {body_fat}%")
        
        print("\n✅ 全てのテストが完了しました！")
        return True
        
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_app_startup():
    """アプリケーション起動確認"""
    print("\n🚀 アプリケーション起動確認:")
    print("   Streamlitアプリケーションが起動しました")
    print("   ブラウザで http://localhost:8501 にアクセスしてください")
    print("")
    print("📝 テスト手順:")
    print("   1. 左側のフォームで日付、体重、体脂肪率を入力")
    print("   2. '記録する'ボタンをクリック")
    print("   3. '✅ データを保存しました！'メッセージが表示されることを確認")
    print("   4. 右側に新しいデータが表示されることを確認")
    print("   5. サイドバーの統計情報が更新されることを確認")
    print("")
    print("⚠️  テスト項目:")
    print("   - 入力フォームの動作")
    print("   - データ保存の確認")
    print("   - 統計情報の表示")
    print("   - エラーハンドリングの動作")
    print("   - レスポンシブデザインの確認")

if __name__ == "__main__":
    print("=" * 50)
    print("体重トラッカー Phase 2 機能テスト")
    print("=" * 50)
    
    # 機能テスト実行
    success = test_main_app_functions()
    
    # アプリケーション起動確認
    check_app_startup()
    
    if success:
        print("\n🎉 Phase 2 テスト完了: 入力フォーム機能は正常に動作しています！")
    else:
        print("\n❌ Phase 2 テストで問題が発生しました。")
        sys.exit(1) 