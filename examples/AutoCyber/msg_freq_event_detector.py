import pandas as pd 
import h1st as h1

import config
import util

class MsgFreqEventDetectorModel(h1.Model):
    def load_data(self, num_files=None):
        return util.load_data(num_files, shuffle=False)
    
    def train(self, prepared_data):
        files = prepared_data["normal_files"]
        
        from collections import defaultdict
        def count_messages(f):
            df = pd.read_parquet(f)
            counts = defaultdict(list)
            
            for window_start in util.gen_windows(df, window_size=config.WINDOW_SIZE, step_size=config.WINDOW_SIZE):
                w_df = df[(df.Timestamp >= window_start) & (df.Timestamp < window_start + config.WINDOW_SIZE)]
                for sensor in config.SENSORS:
                    counts[sensor].append(len(w_df.dropna(subset=[sensor])))

            return pd.DataFrame(counts)
        
        ret = [count_messages(f) for f in files]
        df = pd.concat(ret)

        self.stats = df.describe()
    
    def predict(self, data):
        df = data['df']
        window_starts = data["window_starts"]
        window_results = []
        for window_start in window_starts:
            w_df = df[(df.Timestamp >= window_start) & (df.Timestamp < window_start + config.WINDOW_SIZE)]
            results = {}
            for _, sensor in enumerate(config.SENSORS):
                w_df_sensor = w_df.dropna(subset=[sensor])
                max_normal_message_freq = self.stats.at['max', sensor]
                msg_freq = len(w_df_sensor)
                if msg_freq > (max_normal_message_freq * 1.1):
                    results[sensor] = 1
                else:
                    results[sensor] = 0
                # print("%s => %s" % ((window_start, sensor, msg_freq, max_normal_message_freq), results[sensor]))
                results["WindowInAttack"] = any(results.values())
            results["window_start"] = window_start # information for down-stream
            window_results.append(results)
        return {"event_detection_results": window_results}