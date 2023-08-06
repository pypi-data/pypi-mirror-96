import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CUR_DIR = os.path.dirname(os.path.abspath(__file__))

terminals_dir = os.path.join(CUR_DIR, 'terminals')

# Код, который попадает в weight_list, если весовой терминал вдруг отключился
scale_disconnected_code = '17'

# Код, который попадает в weight_list, если парсинг не удался
fail_parse_code = '4'
