#!/usr/bin/env python3
"""
体重トラッカーアプリケーション状態チェックスクリプト
"""

import os
import sys
import pandas as pd
from datetime import datetime, date
from database import WeightDatabase
import requests
import time

def check_database_status():
    """データベース状態の詳細チェック"""
    print("🗄️  データベース状態チェック")
    print("-" * 40)
    
    try:
        db = WeightDatabase()
        
        # 基本情報
        total_records = db.get_record_count()
        print(f"📊 総レコード数: {total_records}件")
        
        # データベースファイル情報
        db_path = "data/data.db"
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path)
            print(f"💾 ファイルサイズ: {file_size:,} bytes ({file_size/1024:.1f}KB)")
        
        # 最新データ
        df = db.get_measurements(10)
        if not df.empty:
            latest = df.iloc[-1]
            print(f"📅 最新データ日付: {latest['date'].strftime('%Y-%m-%d')}")
            print(f"⚖️  最新体重: {latest['weight']:.1f}kg")
            if pd.notna(latest['body_fat']):
                print(f"📈 最新体脂肪率: {latest['body_fat']:.1f}%")
        
        # 統計情報
        stats = db.get_statistics(30)
        if stats:
            print(f"📊 30日平均体重: {stats['weight_avg']:.1f}kg")
            print(f"📊 最大体重: {stats['weight_max']:.1f}kg")
            print(f"📊 最小体重: {stats['weight_min']:.1f}kg")
            print(f"📊 変化量: {stats['weight_change']:+.1f}kg")
            
            trend_emoji = "📈" if stats['trend'] == 'up' else "📉" if stats['trend'] == 'down' else "➡️"
            print(f"📊 トレンド: {trend_emoji} {stats['trend']}")
        
        # データ期間
        if not df.empty:
            date_range = (df['date'].max() - df['date'].min()).days
            print(f"📅 データ期間: {date_range}日間")
        
        return True
        
    except Exception as e:
        print(f"❌ データベースエラー: {str(e)}")
        return False

def check_web_server_status():
    """Webサーバー状態チェック"""
    print("\n🌐 Webサーバー状態チェック")
    print("-" * 40)
    
    try:
        # Streamlitアプリへの接続テスト
        start_time = time.time()
        response = requests.get("http://localhost:8501", timeout=5)
        response_time = time.time() - start_time
        
        print(f"🌐 HTTP ステータス: {response.status_code}")
        print(f"⏱️  レスポンス時間: {response_time:.3f}秒")
        
        if response.status_code == 200:
            print("✅ アプリケーション正常稼働中")
            
            # HTMLコンテンツの基本チェック
            content = response.text
            if "体重トラッカー" in content:
                print("✅ アプリケーションタイトル確認")
            if "streamlit" in content.lower():
                print("✅ Streamlit フレームワーク確認")
                
            return True
        else:
            print(f"❌ 異常なHTTPステータス: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 接続エラー: アプリケーションが起動していない可能性があります")
        return False
    except requests.exceptions.Timeout:
        print("❌ タイムアウト: アプリケーションの応答が遅すぎます")
        return False
    except Exception as e:
        print(f"❌ Webサーバーエラー: {str(e)}")
        return False

def check_file_structure():
    """ファイル構造チェック"""
    print("\n📁 ファイル構造チェック")
    print("-" * 40)
    
    required_files = {
        "main.py": "メインアプリケーション",
        "database.py": "データベース操作",
        "requirements.txt": "依存関係",
        "data/data.db": "データベースファイル",
        "sample_data/sample_weights.csv": "サンプルデータ"
    }
    
    all_files_exist = True
    
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {description}: {file_path} ({file_size:,} bytes)")
        else:
            print(f"❌ {description}: {file_path} (ファイルが見つかりません)")
            all_files_exist = False
    
    # 追加ファイルチェック
    additional_files = [
        "Phase1_実行レポート.md",
        "Phase2_実行レポート.md",
        "test_main_app.py"
    ]
    
    print("\n📄 追加ファイル:")
    for file_path in additional_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({file_size:,} bytes)")
    
    return all_files_exist

def check_process_status():
    """プロセス状態チェック"""
    print("\n🔄 プロセス状態チェック")
    print("-" * 40)
    
    try:
        # psコマンドでStreamlitプロセスを確認
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        streamlit_processes = []
        for line in result.stdout.split('\n'):
            if 'streamlit' in line and 'main.py' in line:
                streamlit_processes.append(line.strip())
        
        if streamlit_processes:
            print(f"✅ Streamlitプロセス発見: {len(streamlit_processes)}個")
            for process in streamlit_processes:
                # プロセス情報を簡潔に表示
                parts = process.split()
                if len(parts) >= 2:
                    pid = parts[1]
                    print(f"   PID: {pid}")
        else:
            print("❌ Streamlitプロセスが見つかりません")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ プロセスチェックエラー: {str(e)}")
        return False

def main():
    """メインチェック実行"""
    print("=" * 50)
    print("🔍 体重トラッカー アプリケーション状態チェック")
    print(f"🕐 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    checks = [
        ("データベース", check_database_status),
        ("ファイル構造", check_file_structure),
        ("プロセス状態", check_process_status),
        ("Webサーバー", check_web_server_status),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name}チェック中にエラー: {str(e)}")
            results.append((check_name, False))
    
    # 総合結果
    print("\n" + "=" * 50)
    print("📋 チェック結果サマリー")
    print("=" * 50)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ 正常" if result else "❌ 異常"
        print(f"{status} {check_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 体重トラッカーアプリケーションは正常に動作しています！")
        print("🌐 アクセス URL: http://localhost:8501")
        print("📱 または: http://192.168.108.175:8501")
    else:
        print("⚠️  いくつかの問題が検出されました。上記の詳細を確認してください。")
    print("=" * 50)

if __name__ == "__main__":
    main() 