import pandas as pd
import os
from pathlib import Path

def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_excel(file_path)
    
    rename_map = {
        'Лексема': 'lemma',
        'word': 'lemma',
        'Год фиксации': 'year',
        'Регион фиксации': 'region',
    }
    
    df = df.rename(columns=rename_map)
    
    if 'year' in df.columns:
        df['year'] = pd.to_numeric(
            df['year'].astype(str).str.extract(r'(\d{4})')[0], 
            errors='coerce'
        )
    return df


def analyze_dataframe(df: pd.DataFrame, title: str):
    print(f"\n=== АНАЛИЗ: {title} ===\n")
    
    # 1. Лексемы
    print(f"Общее количество уникальных лексем: {df['lemma'].nunique()}")
    
    print("\n--- Частотный анализ лексем ---")
    word_counts = df['lemma'].value_counts()
    most_common = word_counts.idxmax()
    print(f"Наиболее частотная лексема: {most_common} ({word_counts.max()} фиксаций)")
    
    rare = word_counts[word_counts == 1]
    print(f"Лексем с единичными фиксациями: {len(rare)}")
    if not rare.empty:
        print(f"Примеры лексем с единичными фиксациями: {', '.join(rare.index[:5])}")
    
    # 2. Временной анализ
    print("\n--- Временной анализ ---")
    if 'year' in df.columns and df['year'].notna().any():
        print(f"Самая ранняя фиксация: {int(df['year'].min())}")
        print(f"Самая поздняя фиксация:  {int(df['year'].max())}")
    else:
        print("Информация о годе отсутствует")
    
    # 3. География
    print("\n--- Географическое распределение ---")
    place_col = 'region' if 'region' in df.columns else df.columns[0]
    region_counts = df[place_col].value_counts()
    
    print(f"Всего регионов/мест: {df[place_col].nunique()}")
    if not region_counts.empty:
        top = region_counts.iloc[0]
        print(f"Самый представленный регион: {region_counts.index[0]} ({top} фиксаций)")


def main():
    print("\n=== АНАЛИЗ ДИАЛЕКТНОГО ЛЕКСИЧЕСКОГО ДАТАСЕТА ===\n")
    
    money_file = Path("table_money.xlsx")
    love_file = Path("table_love.xlsx")
    
    if not money_file.exists() and not love_file.exists():
        print("Файлы table_money.xlsx и/или table_love.xlsx не найдены в папке!")
        print("Поместите их рядом со скриптом.")
        return
    
    print("Выберите вариант анализа:")
    print("1 — «Милый, любимый» (table_love.xlsx)")
    print("2 — «Стоящий больших денег» (table_money.xlsx)")
    print("3 — Оба значения")
    
    choice = input("\nВаш выбор (1/2/3): ").strip()
    
    if choice == "1" and love_file.exists():
        df = load_data(love_file)
        analyze_dataframe(df, "Милый, любимый")
    
    elif choice == "2" and money_file.exists():
        df = load_data(money_file)
        analyze_dataframe(df, "Стоящий больших денег")
        
    elif choice == "3":
        print("\n" + "="*60)
        if money_file.exists():
            df_money = load_data(money_file)
            analyze_dataframe(df_money, "Стоящий больших денег")
        if love_file.exists():
            df_love = load_data(love_file)
            analyze_dataframe(df_love, "Милый, любимый")
    else:
        print("Неверный выбор или файл отсутствует.")


if __name__ == "__main__":
    main()