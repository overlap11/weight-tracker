#!/usr/bin/env python3
"""
体重トラッカー - 拡張バリデーション機能
Phase 3: データバリデーション強化
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum

class ValidationLevel(Enum):
    """バリデーションレベル"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

@dataclass
class ValidationResult:
    """バリデーション結果"""
    level: ValidationLevel
    message: str
    suggestion: Optional[str] = None
    value: Optional[float] = None

class AdvancedValidator:
    """拡張バリデーション機能"""
    
    def __init__(self, db_instance):
        self.db = db_instance
        
    def validate_weight_change(self, date_str: str, weight: float, body_fat: Optional[float] = None) -> List[ValidationResult]:
        """体重変化の妥当性チェック"""
        results = []
        
        # 前回データの取得
        recent_data = self.db.get_measurements(7)  # 過去7日分
        if recent_data.empty:
            results.append(ValidationResult(
                level=ValidationLevel.INFO,
                message="初回データです。継続的な記録をお勧めします。",
                suggestion="毎日同じ時間帯に測定すると正確な変化がわかります"
            ))
            return results
        
        # 前回との比較
        latest_record = recent_data.iloc[-1]
        latest_date = pd.to_datetime(latest_record['date']).date()
        input_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # 日付の連続性チェック
        days_gap = (input_date - latest_date).days
        if days_gap > 7:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"前回記録から{days_gap}日間が経過しています。",
                suggestion="継続的な記録で正確な変化を把握できます"
            ))
        
        # 体重変化の分析
        weight_diff = weight - latest_record['weight']
        daily_change = weight_diff / max(days_gap, 1)
        
        # 異常な変化の検出
        if abs(daily_change) > 1.0:  # 1日1kg以上の変化
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"体重が{weight_diff:+.1f}kg変化しています（1日あたり{daily_change:+.1f}kg）",
                suggestion="大きな変化の場合は測定条件を確認してください"
            ))
        elif abs(weight_diff) > 5.0:  # 5kg以上の変化
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"体重が{weight_diff:+.1f}kg変化しています。測定値を確認してください。",
                suggestion="測定条件（時間帯、服装、測定前の食事など）を確認してください"
            ))
        
        # 体脂肪率の変化チェック
        if body_fat is not None and pd.notna(latest_record['body_fat']):
            body_fat_diff = body_fat - latest_record['body_fat']
            if abs(body_fat_diff) > 5.0:  # 5%以上の変化
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"体脂肪率が{body_fat_diff:+.1f}%変化しています。",
                    suggestion="体脂肪率は日内変動が大きいため、同じ時間帯での測定をお勧めします"
                ))
        
        return results
    
    def validate_statistical_outlier(self, date_str: str, weight: float, body_fat: Optional[float] = None) -> List[ValidationResult]:
        """統計的異常値の検出"""
        results = []
        
        # 過去30日のデータ取得
        historical_data = self.db.get_measurements(30)
        if len(historical_data) < 7:  # データが少ない場合はスキップ
            return results
        
        # 体重の統計分析
        weight_stats = historical_data['weight'].describe()
        weight_mean = weight_stats['mean']
        weight_std = weight_stats['std']
        
        # Z-score計算
        z_score = abs(weight - weight_mean) / weight_std if weight_std > 0 else 0
        
        if z_score > 2.5:  # 2.5σ以上
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"入力値が過去30日の平均から大きく外れています（{weight:.1f}kg vs 平均{weight_mean:.1f}kg）",
                suggestion=f"通常の範囲: {weight_mean - 2*weight_std:.1f}kg - {weight_mean + 2*weight_std:.1f}kg"
            ))
        
        # 体脂肪率の統計分析
        if body_fat is not None:
            body_fat_data = historical_data['body_fat'].dropna()
            if len(body_fat_data) >= 7:
                body_fat_stats = body_fat_data.describe()
                body_fat_mean = body_fat_stats['mean']
                body_fat_std = body_fat_stats['std']
                
                z_score_bf = abs(body_fat - body_fat_mean) / body_fat_std if body_fat_std > 0 else 0
                
                if z_score_bf > 2.5:
                    results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        message=f"体脂肪率が過去30日の平均から大きく外れています（{body_fat:.1f}% vs 平均{body_fat_mean:.1f}%）",
                        suggestion=f"通常の範囲: {body_fat_mean - 2*body_fat_std:.1f}% - {body_fat_mean + 2*body_fat_std:.1f}%"
                    ))
        
        return results
    
    def validate_trend_consistency(self, date_str: str, weight: float) -> List[ValidationResult]:
        """トレンドの一貫性チェック"""
        results = []
        
        # 過去14日のデータ取得
        recent_data = self.db.get_measurements(14)
        if len(recent_data) < 5:
            return results
        
        # 移動平均計算
        recent_data['weight_ma'] = recent_data['weight'].rolling(window=3, center=True).mean()
        
        # トレンド分析
        if len(recent_data) >= 7:
            first_half = recent_data.iloc[:len(recent_data)//2]['weight'].mean()
            second_half = recent_data.iloc[len(recent_data)//2:]['weight'].mean()
            
            trend_direction = "減少" if second_half < first_half else "増加"
            
            # 新しい値がトレンドに合致するかチェック
            latest_weight = recent_data.iloc[-1]['weight']
            if trend_direction == "減少" and weight > latest_weight + 0.5:
                results.append(ValidationResult(
                    level=ValidationLevel.INFO,
                    message=f"最近の減少トレンドに対して増加しています（{weight:.1f}kg vs 前回{latest_weight:.1f}kg）",
                    suggestion="体重は日々変動するため、トレンドで判断することが重要です"
                ))
            elif trend_direction == "増加" and weight < latest_weight - 0.5:
                results.append(ValidationResult(
                    level=ValidationLevel.INFO,
                    message=f"最近の増加トレンドに対して減少しています（{weight:.1f}kg vs 前回{latest_weight:.1f}kg）",
                    suggestion="体重は日々変動するため、トレンドで判断することが重要です"
                ))
        
        return results
    
    def get_recommended_values(self, date_str: str) -> Dict[str, float]:
        """推奨値の提案"""
        recent_data = self.db.get_measurements(7)
        if recent_data.empty:
            return {}
        
        # 最近の平均値を推奨値として提案
        recent_avg_weight = recent_data['weight'].mean()
        recent_avg_body_fat = recent_data['body_fat'].mean() if recent_data['body_fat'].notna().any() else None
        
        recommendations = {
            'weight': round(recent_avg_weight, 1)
        }
        
        if recent_avg_body_fat is not None:
            recommendations['body_fat'] = round(recent_avg_body_fat, 1)
        
        return recommendations
    
    def validate_measurement_conditions(self, date_str: str, weight: float, body_fat: Optional[float] = None) -> List[ValidationResult]:
        """測定条件の妥当性チェック"""
        results = []
        
        # 日付が今日の場合、測定時間の提案
        input_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if input_date == date.today():
            current_time = datetime.now().hour
            if current_time < 6 or current_time > 22:
                results.append(ValidationResult(
                    level=ValidationLevel.INFO,
                    message="深夜・早朝の測定ですね。",
                    suggestion="朝起床後トイレ後の測定が最も正確です"
                ))
        
        # 週末の測定パターンチェック
        if input_date.weekday() in [5, 6]:  # 土日
            recent_data = self.db.get_measurements(30)
            if not recent_data.empty:
                weekend_data = recent_data[pd.to_datetime(recent_data['date']).dt.weekday.isin([5, 6])]
                if len(weekend_data) < 2:
                    results.append(ValidationResult(
                        level=ValidationLevel.INFO,
                        message="週末の測定記録ですね。",
                        suggestion="週末も継続的に測定することで正確な変化を把握できます"
                    ))
        
        return results
    
    def comprehensive_validation(self, date_str: str, weight: float, body_fat: Optional[float] = None) -> Dict[str, List[ValidationResult]]:
        """包括的なバリデーション"""
        validation_results = {}
        
        # 各種バリデーションを実行
        validation_results['change_analysis'] = self.validate_weight_change(date_str, weight, body_fat)
        validation_results['statistical_analysis'] = self.validate_statistical_outlier(date_str, weight, body_fat)
        validation_results['trend_analysis'] = self.validate_trend_consistency(date_str, weight)
        validation_results['measurement_conditions'] = self.validate_measurement_conditions(date_str, weight, body_fat)
        
        return validation_results
    
    def get_validation_summary(self, validation_results: Dict[str, List[ValidationResult]]) -> Dict[str, int]:
        """バリデーション結果のサマリー"""
        summary = {
            'total_checks': 0,
            'info_count': 0,
            'warning_count': 0,
            'error_count': 0
        }
        
        for category, results in validation_results.items():
            for result in results:
                summary['total_checks'] += 1
                if result.level == ValidationLevel.INFO:
                    summary['info_count'] += 1
                elif result.level == ValidationLevel.WARNING:
                    summary['warning_count'] += 1
                elif result.level == ValidationLevel.ERROR:
                    summary['error_count'] += 1
        
        return summary 