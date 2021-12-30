from typing import Dict, Any

import __init__
from h1st.model.kgen_model import KGenModel


class MyGeneralizer(KGenModel):
    def preprocess(self, data: Dict[str, Any]) -> Dict[str, Any]:
        raw_data = data['X']
        return {
            'X': self.stats['scaler'].transform(raw_data)
        }

    def predict(self, input_data: Dict) -> Dict:
        preprocess_data = self.preprocess(input_data)
        y = self.base_model.predict(preprocess_data['X'])
        return {'predictions': [self.stats['targets'][item] for item in y]}