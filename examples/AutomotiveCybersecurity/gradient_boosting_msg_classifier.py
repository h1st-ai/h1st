import h1st as h1
import pandas as pd

import config
import util

FEATURES = config.SENSORS + ["%s_TimeDiff" % s for s in config.SENSORS]

class GradientBoostingMsgClassifierModel(h1.Model):
    def load_data(self, num_files=None):
        return util.load_data(num_files, shuffle=False)

    def prep(self, data):
        def concat_processed_files(files):
            dfs = []
            for f in files:
                z = pd.read_parquet(f)
                z = util.compute_timediff_fillna(z, dropna_subset=FEATURES)
                dfs.append(z)
            df2 = pd.concat(dfs)
            return df2
        split = int(len(data["attack_files"])*0.5)
        train_files = data["attack_files"][:split]
        test_files = data["attack_files"][split:]
        result = {
            "train_files": train_files,
            "test_files": test_files,
            "train_attack_df": concat_processed_files(train_files),
            "test_attack_df": concat_processed_files(test_files)
        }
        print("len train_attack_df = %s" % len(result["train_attack_df"]))
        print("len test_attack_df = %s" % len(result["test_attack_df"]))
        return result

    def train(self, prepared_data):
        df = prepared_data["train_attack_df"]
        from sklearn.experimental import enable_hist_gradient_boosting
        from sklearn.ensemble import HistGradientBoostingClassifier
        X = df[FEATURES]
        y = df.Label == config.ATTACK_LABEL
        self.model = HistGradientBoostingClassifier(max_iter=500).fit(X, y)

    def evaluate(self, prepared_data):
        df = prepared_data["test_attack_df"]
        ypred = self.model.predict(df[FEATURES])
        import sklearn.metrics
        cf = sklearn.metrics.confusion_matrix(df.Label == config.ATTACK_LABEL, ypred)
        acc = sklearn.metrics.accuracy_score(df.Label == config.ATTACK_LABEL, ypred)
        print(cf)
        print("Accuracy = %.4f" % acc)
        self.metrics = {"confusion_matrix": cf, "accuracy": acc}
    
    def predict(self, data):
        df = data["df"].copy()
        df = util.compute_timediff_fillna(df)
        df['MsgIsAttack'] = 0
        df['WindowInAttack'] = 0
        for event_result in data["event_detection_results"]:
            if event_result['WindowInAttack']:
                # print("window %s in attack: event_result = %s" % (event_result['window_start'], event_result))
                in_window = (df.Timestamp >= event_result['window_start']) & (df.Timestamp < event_result['window_start'] + config.WINDOW_SIZE)
                w_df = df[in_window]
                if len(w_df) > 0:
                    ypred = self.model.predict(w_df[FEATURES])
                    df.loc[in_window, "WindowInAttack"] = 1
                    df.loc[in_window, "MsgIsAttack"] = ypred.astype(int)
        return {"injection_window_results": df}