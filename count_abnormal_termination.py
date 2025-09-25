#!/usr/bin/env python3
"""
ログファイル内で「※異常終了したため」を含む行の数を数えるスクリプト
"""

import glob
import os

def count_abnormal_terminations(file_path):
    """
    指定されたファイルで「※異常終了したため」を含む行の数を数える
    
    Args:
        file_path (str): 検索対象のファイルパス
        
    Returns:
        int: 異常終了の行数
    """
    count = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                if '※異常終了したため' in line:
                    count += 1
                    print(f"  {line_num}行目: {line.strip()}")
    except FileNotFoundError:
        print(f"ファイルが見つかりません: {file_path}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    
    return count

def main():
    """メイン関数"""
    # 現在のディレクトリのログファイルを検索
    log_files = glob.glob("*.log")
    
    if not log_files:
        print("ログファイルが見つかりませんでした。")
        return
    
    total_count = 0
    file_results = []
    
    print("=" * 60)
    print("異常終了検索結果")
    print("=" * 60)
    
    for log_file in sorted(log_files):
        print(f"\n📄 {log_file}")
        print("-" * 40)
        count = count_abnormal_terminations(log_file)
        file_results.append((log_file, count))
        total_count += count
    
    print("\n" + "=" * 60)
    print("📊 ファイル別集計結果")
    print("=" * 60)
    
    for file_name, count in file_results:
        print(f"  {file_name:<20} : {count:>3}回")
    
    print("-" * 60)
    print(f"  {'合計':<20} : {total_count:>3}回")
    print("=" * 60)

if __name__ == "__main__":
    main()
