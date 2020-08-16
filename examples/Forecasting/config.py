import pandas as pd
from typing import List

MODEL_REPO_PATH = "models"

NODE_VALIDATION_SCHEMA = {
    'ForecastModel': {
        'test_input': pd.DataFrame({
            'Open': [],
            'Promo': [],
            'StateHoliday': [],
            'SchoolHoliday': [],
            'DayOfWeek': [],
            'DayOfMonth': [],
            'Month': [],
            'StoreType': [],
            'Assortment': [],
            'CompetitionDistance': [],
            'CompetitionOpenSinceMonth': [],
            'CompetitionOpenSinceYear': [],
            'Promo2': [],
            'Promo2SinceWeek': [],
            'Promo2SinceYear': []
        }),
        'expected_output': {
            'type': dict,
            'fields':  {
                'window_indices': List[float]
            }
        }
    }
}

FORECAST_DATA_PATH = './data'
