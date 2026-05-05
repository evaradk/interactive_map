import pandas as pd
import folium
import sys
import colorsys

# ВЫБОР ВАРИАНТА ЗНАЧЕНИЯ
if len(sys.argv) > 1:
    choice = sys.argv[1]
else:
    print("Выберите вариант:")
    print("1 — Лексемы в значении «милый, любимый»")
    print("2 — Лексемы в значении «стоящий больших денег»")
    print("3 — Оба значения")
    choice = input("Введите номер варианта (1/2/3): ").strip()

# Определяем значение, файлы и режим
if choice == '1':
    meaning = "милый, любимый"
    files = ["table_love.xlsx"]
    output_filename = "russia_dialect_map_love.html"
    two_color_mode = False
elif choice == '2':
    meaning = "стоящий больших денег"
    files = ["table_money.xlsx"]
    output_filename = "russia_dialect_map_money.html"
    two_color_mode = False
elif choice == '3':
    meaning = "милый, любимый и стоящий больших денег"
    files = ["table_love.xlsx", "table_money.xlsx"]
    output_filename = "russia_dialect_map_both.html"
    two_color_mode = True
else:
    print("Неверный выбор, используется значение по умолчанию (милый, любимый)")
    meaning = "милый, любимый"
    files = ["table_love.xlsx"]
    output_filename = "russia_dialect_map_love.html"
    two_color_mode = False

print(f"Заголовок карты: «Лексемы в значении \"{meaning}\"»")
print(f"Результат будет сохранён в: {output_filename}")

#ДАННЫЕ
if two_color_mode:
    df_love = pd.read_excel("table_love.xlsx", sheet_name='Лист1')
    df_love['category'] = 'love'
    df_money = pd.read_excel("table_money.xlsx", sheet_name='Лист1')
    df_money['category'] = 'money'
    df = pd.concat([df_love, df_money], ignore_index=True)
else:
    df = pd.read_excel(files[0], sheet_name='Лист1')

df = df.dropna(subset=['LAT', 'LON', 'Лексема']).copy()
df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
df['LON'] = pd.to_numeric(df['LON'], errors='coerce')
df = df.dropna(subset=['LAT', 'LON']).reset_index(drop=True)

print(f'Загружено {len(df)} точек.')

#ЦВЕТА
def hsl_to_hex(h, s, l):
    rgb = colorsys.hls_to_rgb(h/360, l/100, s/100)
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

base_hues = [i * 30 for i in range(12)]
colors_24 = []
for hue in base_hues:
    colors_24.append(hsl_to_hex(hue, 90, 63))   # светлый
    colors_24.append(hsl_to_hex(hue, 88, 37))   # тёмный

#генерация вариаций
color_variants = []

# 1. fill == stroke, сплошная
for c in colors_24:
    color_variants.append({'fill': c, 'color': c, 'dashArray': ''})

# 2. fill != stroke, сплошная
for stroke_c in colors_24:
    for fill_c in colors_24:
        if fill_c != stroke_c:
            color_variants.append({
                'fill': fill_c,
                'color': stroke_c,
                'dashArray': ''
            })

# 3. fill == stroke, пунктир
for c in colors_24:
    color_variants.append({'fill': c, 'color': c, 'dashArray': '5,8'})

# 4. fill != stroke, пунктир
for stroke_c in colors_24:
    for fill_c in colors_24:
        if fill_c != stroke_c:
            color_variants.append({
                'fill': fill_c,
                'color': stroke_c,
                'dashArray': '5,8'
            })

# Цвета для режима с двумя группами
if two_color_mode:
    color_love = {'fill': '#FFB3BA', 'color': '#FF1744', 'dashArray': ''}
    color_money = {'fill': '#B3FFB3', 'color': '#00C853', 'dashArray': ''}
    category_color = {'love': color_love, 'money': color_money}
else:
    unique_lexemes = df['Лексема'].unique()
    color_dict = {}
    for i, lex in enumerate(unique_lexemes):
        variant = color_variants[i % len(color_variants)]
        color_dict[lex] = variant
    print(f"Присвоено цветов для {len(unique_lexemes)} лексем.")

#КАРТА
m = folium.Map(
    location=[55, 60],
    zoom_start=4,
    tiles='cartodb positron',
    max_bounds=[[30, 10], [80, 180]],
    min_zoom=3,
    max_zoom=12,
    attribution_control=False
)

# Предварительная подготовка popup-HTML (оптимизация)
for _, row in df.iterrows():
    lex = row['Лексема']
    if two_color_mode:
        var = category_color[row['category']]
    else:
        var = color_dict.get(lex)
    
    html_parts = []
    fields = [
        ('Источник', row.get('Источник')),
        ('Помета', row.get('Помета')),
        ('Формы', row.get('Формы')),
        ('Варианты ударения, произношения, грамматических форм', row.get('Варианты ударения, произношения, грамматических форм')),
        ('Значение', row.get('Значение')),
        ('Оттенки значения', row.get('Оттенки значения')),
        ('Все значения', row.get('Все значения')),
        ('Пример из словаря', row.get('Пример из словаря')),
        ('Устойчивые сочетания', row.get('Устойчивые сочетания')),
        ('Регион фиксации', row.get('Регион фиксации')),
        ('Год фиксации', row.get('Год фиксации')),
        ('НКРЯ', row.get('НКРЯ')),
        ('Устойчивые сочетания1', row.get('Устойчивые сочетания1'))
    ]
    
    for label, value in fields:
        if pd.notna(value) and str(value).strip() not in ['–', '-', '', 'nan']:
            html_parts.append(f'<b>{label}:</b> {value}<br>')
    
    popup_html = f"""
    <div style="max-width:380px; max-height:420px; overflow-y:auto; font-size:13px; line-height:1.4;">
        <h4 style="margin:0 0 10px 0;">{row.get('ADRESS / PLACE', '')} — {lex}</h4>
        {' '.join(html_parts)}
    </div>
    """
    
    folium.CircleMarker(
        location=[row['LAT'], row['LON']],
        radius=6,
        popup=folium.Popup(popup_html, max_width=400),
        color=var['color'],
        weight=2.5,
        opacity=0.9,
        fill=True,
        fillColor=var['fill'],
        fillOpacity=0.85,
        dashArray=var.get('dashArray'),
        tooltip=lex
    ).add_to(m)

#HTML-СТРУКТУРА
# Заголовок легенды
if two_color_mode:
    legend_title = "Значения (2)"
else:
    legend_title = f"Лексемы ({len(color_dict)})"

full_html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{meaning} — Лексемы из СРНГ</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f9f9f9; }}
        .container {{ max-width: 1300px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 20px; }}
        .map-container {{ 
            border: 3px solid #444; 
            border-radius: 8px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); 
            margin: 20px auto; 
            max-width: 1250px;
        }}
        .legend {{ 
            background: white; 
            padding: 15px; 
            border: 2px solid #ccc; 
            border-radius: 8px; 
            max-height: 280px; 
            overflow-y: auto; 
            margin: 20px auto; 
            width: 95%; 
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin:0; font-size:28px; color:#333;">Интерактивная карта</h1>
            <h2 style="margin:8px 0 0 0; font-size:18px; color:#555;">Лексемы в значении "{meaning}" из "Словаря русских народных говоров"</h2>
        </div>
        
        <div class="map-container">
            {m._repr_html_()}
        </div>
        
        <div class="legend">
            <h4 style="margin:0 0 10px 0; text-align:center;">{legend_title}</h4>
            <div style="columns:3; column-gap:20px; line-height:1.35;">
'''

#Легенда
if two_color_mode:
    legend_items = []
    var_love = category_color['love']
    dash_love = 'dashed' if var_love.get('dashArray') else 'solid'
    legend_items.append(f'''
    <div style="margin-bottom:4px;">
        <span style="display:inline-block; width:16px; height:16px; 
                     background:{var_love['fill']}; 
                     border:2.5px {dash_love} {var_love['color']}; 
                     margin-right:8px; vertical-align:middle; border-radius:50%;"></span>
        милый, любимый
    </div>''')
    var_money = category_color['money']
    dash_money = 'dashed' if var_money.get('dashArray') else 'solid'
    legend_items.append(f'''
    <div style="margin-bottom:4px;">
        <span style="display:inline-block; width:16px; height:16px; 
                     background:{var_money['fill']}; 
                     border:2.5px {dash_money} {var_money['color']}; 
                     margin-right:8px; vertical-align:middle; border-radius:50%;"></span>
        стоящий больших денег
    </div>''')
    full_html += ''.join(legend_items)
else:
    legend_items = []
    for lex, var in color_dict.items():
        dash_style = 'dashed' if var.get('dashArray') else 'solid'
        legend_items.append(f'''
        <div style="margin-bottom:4px;">
            <span style="display:inline-block; width:16px; height:16px; 
                         background:{var['fill']}; 
                         border:2.5px {dash_style} {var['color']}; 
                         margin-right:8px; vertical-align:middle; border-radius:50%;"></span>
            {lex}
        </div>''')
    full_html += ''.join(legend_items)

full_html += '''
            </div>
        </div>
        
        <div class="footer">
            Автор: Радецкая Ева Максимовна, г. Петрозаводск, 2026 г.
        </div>
    </div>
</body>
</html>
'''

with open(output_filename, 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f'Готовая страница успешно сохранена в {output_filename}')