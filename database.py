import sqlite3
import pandas as pd
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import os


class WeightDatabase:
    """体重トラッカー用SQLiteデータベース操作クラス"""
    
    def __init__(self, db_path: str = "data/data.db"):
        """
        データベース初期化
        
        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self.ensure_data_directory()
        self.initialize_database()
    
    def ensure_data_directory(self):
        """データディレクトリの存在確認・作成"""
        if self.db_path != ':memory:' and os.path.dirname(self.db_path):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def initialize_database(self) -> None:
        """データベースの初期化とテーブル作成"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # measurements テーブル作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL UNIQUE,
                    weight REAL NOT NULL,
                    body_fat REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # settings テーブル作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # インデックス作成
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_measurements_date 
                ON measurements(date)
            ''')
            
            # 初期設定データの挿入
            cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value) 
                VALUES ('target_weight', 70.0)
            ''')
            cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value) 
                VALUES ('height', 170.0)
            ''')
            
            conn.commit()
    
    def add_measurement(self, date: str, weight: float, body_fat: Optional[float] = None) -> bool:
        """
        体重測定データの追加
        
        Args:
            date: 測定日（YYYY-MM-DD形式）
            weight: 体重（kg）
            body_fat: 体脂肪率（%）
            
        Returns:
            成功時True、失敗時False
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO measurements (date, weight, body_fat, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (date, weight, body_fat))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            return False
    
    def get_measurements(self, days: Optional[int] = None) -> pd.DataFrame:
        """
        体重測定データの取得
        
        Args:
            days: 取得日数（Noneの場合は全期間）
            
        Returns:
            測定データのDataFrame
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                if days is None:
                    query = '''
                        SELECT id, date, weight, body_fat, created_at, updated_at
                        FROM measurements
                        ORDER BY date DESC
                    '''
                    df = pd.read_sql_query(query, conn)
                else:
                    query = '''
                        SELECT id, date, weight, body_fat, created_at, updated_at
                        FROM measurements
                        ORDER BY date DESC
                        LIMIT ?
                    '''
                    df = pd.read_sql_query(query, conn, params=(days,))
                
                if not df.empty:
                    # 日付順に並び替え（昇順）
                    df = df.sort_values('date').reset_index(drop=True)
                    # 日付をdatetime型に変換
                    df['date'] = pd.to_datetime(df['date'])
                
                return df
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            return pd.DataFrame()
    
    def get_measurement_by_date(self, date: str) -> Optional[Dict[str, Any]]:
        """
        指定日の測定データを取得
        
        Args:
            date: 測定日（YYYY-MM-DD形式）
            
        Returns:
            測定データの辞書（存在しない場合None）
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, date, weight, body_fat, created_at, updated_at
                    FROM measurements
                    WHERE date = ?
                ''', (date,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'id': row[0],
                        'date': row[1],
                        'weight': row[2],
                        'body_fat': row[3],
                        'created_at': row[4],
                        'updated_at': row[5]
                    }
                return None
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            return None
    
    def update_measurement(self, id: int, weight: float, body_fat: Optional[float] = None) -> bool:
        """
        測定データの更新
        
        Args:
            id: 測定データID
            weight: 体重（kg）
            body_fat: 体脂肪率（%）
            
        Returns:
            成功時True、失敗時False
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE measurements
                    SET weight = ?, body_fat = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (weight, body_fat, id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            return False
    
    def update_measurement_by_date(self, date: str, weight: float, body_fat: Optional[float] = None) -> bool:
        """
        指定日の測定データを更新
        
        Args:
            date: 測定日（YYYY-MM-DD形式）
            weight: 体重（kg）
            body_fat: 体脂肪率（%）
            
        Returns:
            成功時True、失敗時False
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE measurements
                    SET weight = ?, body_fat = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE date = ?
                ''', (weight, body_fat, date))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            return False
    
    def delete_measurement(self, id: int) -> bool:
        """
        測定データの削除
        
        Args:
            id: 測定データID
            
        Returns:
            成功時True、失敗時False
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM measurements WHERE id = ?', (id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            return False
    
    def get_setting(self, key: str) -> Optional[float]:
        """
        設定値の取得
        
        Args:
            key: 設定キー
            
        Returns:
            設定値（存在しない場合None）
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
                row = cursor.fetchone()
                return row[0] if row else None
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            return None
    
    def set_setting(self, key: str, value: float) -> bool:
        """
        設定値の更新
        
        Args:
            key: 設定キー
            value: 設定値
            
        Returns:
            成功時True、失敗時False
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, value))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            return False
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        統計情報の取得
        
        Args:
            days: 統計対象日数
            
        Returns:
            統計情報の辞書
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 全データを取得して日付で絞り込み
                cursor.execute('''
                    SELECT weight, body_fat, date
                    FROM measurements
                    ORDER BY date DESC
                    LIMIT ?
                ''', (days,))
                rows = cursor.fetchall()
                
                if not rows:
                    return {}
                
                weights = [row[0] for row in rows]
                body_fats = [row[1] for row in rows if row[1] is not None]
                
                stats = {
                    'count': len(weights),
                    'weight_avg': sum(weights) / len(weights),
                    'weight_max': max(weights),
                    'weight_min': min(weights),
                    'weight_latest': weights[0],
                    'weight_oldest': weights[-1],
                    'weight_change': weights[0] - weights[-1],
                    'trend': 'up' if weights[0] > weights[-1] else 'down' if weights[0] < weights[-1] else 'flat'
                }
                
                if body_fats:
                    stats.update({
                        'body_fat_avg': sum(body_fats) / len(body_fats),
                        'body_fat_max': max(body_fats),
                        'body_fat_min': min(body_fats),
                        'body_fat_latest': next((row[1] for row in rows if row[1] is not None), None)
                    })
                
                return stats
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            return {}
    
    def import_from_csv(self, csv_data: pd.DataFrame) -> tuple[int, int]:
        """
        CSVデータからの一括インポート
        
        Args:
            csv_data: CSVデータのDataFrame
            
        Returns:
            (成功件数, 失敗件数)
        """
        success_count = 0
        error_count = 0
        
        for _, row in csv_data.iterrows():
            try:
                date_str = str(row['date'])
                weight = float(row['weight'])
                body_fat = float(row['body_fat']) if pd.notna(row['body_fat']) else None
                
                if self.add_measurement(date_str, weight, body_fat):
                    success_count += 1
                else:
                    error_count += 1
            except (ValueError, KeyError) as e:
                print(f"データ変換エラー: {e}")
                error_count += 1
        
        return success_count, error_count
    
    def export_to_csv(self) -> pd.DataFrame:
        """
        全データをCSV形式で出力
        
        Returns:
            全測定データのDataFrame
        """
        return self.get_measurements()
    
    def get_record_count(self) -> int:
        """
        総レコード数の取得
        
        Returns:
            総レコード数
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM measurements')
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"データベースエラー: {e}")
            return 0


# データベース接続テスト関数
def test_database_connection():
    """データベース接続テスト"""
    print("データベース接続テストを開始...")
    
    try:
        db = WeightDatabase()
        print("✅ データベース初期化成功")
        
        # テストデータの挿入
        test_date = "2024-01-01"
        test_weight = 70.0
        test_body_fat = 18.0
        
        if db.add_measurement(test_date, test_weight, test_body_fat):
            print("✅ データ挿入成功")
        else:
            print("❌ データ挿入失敗")
            return False
        
        # データの取得
        df = db.get_measurements()
        if not df.empty:
            print(f"✅ データ取得成功: {len(df)}件")
            print(f"   最新データ: {df.iloc[-1]['date'].strftime('%Y-%m-%d')}, {df.iloc[-1]['weight']}kg")
        else:
            print("❌ データ取得失敗")
            return False
        
        # 統計情報の取得
        stats = db.get_statistics(30)
        if stats:
            print(f"✅ 統計情報取得成功: 平均体重 {stats['weight_avg']:.1f}kg")
        else:
            print("❌ 統計情報取得失敗")
            return False
        
        # 設定の取得
        target_weight = db.get_setting('target_weight')
        if target_weight:
            print(f"✅ 設定取得成功: 目標体重 {target_weight}kg")
        else:
            print("❌ 設定取得失敗")
            return False
        
        print("✅ データベース接続テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ データベース接続テスト失敗: {e}")
        return False


if __name__ == "__main__":
    # テスト実行
    test_database_connection() 