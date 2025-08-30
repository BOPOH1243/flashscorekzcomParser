import json
import re
from datetime import datetime

def parse_weird_format(data_string):
    """
    Парсит странный формат с разделителями ¬ и ÷
    Возвращает структурированные данные
    """
    blocks = data_string.split('~')
    common_data = {}
    matches = []
    
    for block in blocks:
        if not block:
            continue
            
        fields = block.split('¬')
        block_data = {}
        
        for field in fields:
            if not field:
                continue
                
            key, sep, value = field.partition('÷')
            if sep:
                # Обрабатываем JSON-подобные структуры в BGS
                if key == 'BGS' and value.startswith('{') and value.endswith('}'):
                    try:
                        value = json.loads(value.replace('\\"', '"'))
                    except:
                        pass  # Оставляем как строку если не парсится
                block_data[key] = value
        
        if 'AA' in block_data:
            # Обрабатываем UNIX время для матчей
            if 'AD' in block_data:
                try:
                    timestamp = int(block_data['AD'])
                    dt_object = datetime.fromtimestamp(timestamp)
                    block_data['AD_datetime'] = dt_object.isoformat()
                    block_data['AD_readable'] = dt_object.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    block_data['AD_datetime'] = None
                    block_data['AD_readable'] = None
            matches.append(block_data)
        else:
            common_data.update(block_data)
    
    return {'common': common_data, 'matches': matches}

def main():
    # Читаем данные из файла
    try:
        with open('shit.txt', 'r', encoding='utf-8') as f:
            data_string = f.read().strip()
    except FileNotFoundError:
        print("Ошибка: Файл shit.txt не найден!")
        return
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return
    
    # Парсим данные
    parsed_data = parse_weird_format(data_string)
    
    # Сохраняем в JSON
    try:
        with open('shit.json', 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
        print("Успех! Данные сохранены в shit.json")
        print(f"Найдено матчей: {len(parsed_data['matches'])}")
        print(f"Турнир: {parsed_data['common'].get('ZA', 'Неизвестно')}")
    except Exception as e:
        print(f"Ошибка при сохранении JSON: {e}")

if __name__ == "__main__":
    main()