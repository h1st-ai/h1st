import h1st as h1
import pandas as pd
import os
import sklearn
import sklearn.metrics
import subprocess
import pathlib
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import OneHotEncoder
from Forecasting import config


class ForecastModel(h1.MLModel):
    def __init__(self):
        super().__init__()
        self.base_model = None
        self.feature_cols = ['Open', 'Promo', 'StateHoliday', 'SchoolHoliday', 
                            'DayOfWeek', 'DayOfMonth', 'Month',
                            'StoreType', 'Assortment', 'CompetitionDistance', 
                            'CompetitionOpenSinceMonth', 'CompetitionOpenSinceYear', 
                            'Promo2', 'Promo2SinceWeek', 'Promo2SinceYear']
        self.data_dir = config.FORECAST_DATA_PATH
    
    def load_data(self):
        # needs to have kaggle tools, and user credentials, and agreed to competition rules etc.
        pathlib.Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        if not os.path.isfile(os.path.join(self.data_dir, "train.csv")):
            print("Using `kaggle` command to download data from rossmann-store-sales competition.")
            print("You'll need https://pypi.org/project/kaggle/ tool and agrees to the terms of the competition at https://www.kaggle.com/c/rossmann-store-sales/")
            subprocess.run("kaggle competitions download -c rossmann-store-sales -p {data}/".format(data=self.data_dir), shell=True, check=True)
            subprocess.run("cd {data}; unzip rossmann-store-sales.zip".format(data=self.data_dir), shell=True, check=True)

        df = pd.read_csv(os.path.join(self.data_dir, "train.csv"), low_memory=False)

        store_info = pd.read_csv(os.path.join(self.data_dir, "store.csv"))
        df = df.merge(store_info, on="Store")

        return df
    
    def explore(self):
        df = self.load_data()
        import seaborn
        print(df.count()) # count NA
        seaborn.distplot(df.Sales) # Sales distribution

    def prep(self, loaded_data):
        """
        Prepare data for modelling
        :param loaded_data: data return from load_data method
        :returns: dictionary contains train data and validation data
        """

        df = loaded_data
        df.fillna(0, inplace=True) # safe to fill, see countNA table below:
        # Store                        1017209
        # DayOfWeek                    1017209
        # Date                         1017209
        # Sales                        1017209
        # Customers                    1017209
        # Open                         1017209
        # Promo                        1017209
        # StateHoliday                 1017209
        # SchoolHoliday                1017209
        # StoreType                    1017209
        # Assortment                   1017209
        # CompetitionDistance          1014567
        # CompetitionOpenSinceMonth     693861
        # CompetitionOpenSinceYear      693861
        # Promo2                       1017209
        # Promo2SinceWeek               509178
        # Promo2SinceYear               509178
        # PromoInterval                 509178
        # dtype: int64

        df["Date"] = pd.to_datetime(df.Date)
        df["DayOfWeek"] = df.Date.dt.dayofweek
        df["DayOfMonth"] = df.Date.dt.day
        df["Month"] = df.Date.dt.month
        
        train_df = df[df["Date"] < "2015-06-01"]
        val_df = df[df["Date"] >= "2015-06-01"]
        print(len(train_df), len(val_df))
        # sales only should get 949194 68015
        # after dropNA on storeinfo: 302061 22265
        
        return {
            'train_df': train_df,
            'val_df': val_df,
            'len_train_val': (len(train_df), len(val_df))
        }

    def train(self, prepared_data):
        train_df = prepared_data['train_df'][self.feature_cols]
        sales = prepared_data['train_df']["Sales"]
        transformer = make_column_transformer(
            (OneHotEncoder(handle_unknown="ignore"), ['StateHoliday', "StoreType", "Assortment"]),
            remainder="passthrough")
        
        transformer.fit(train_df[self.feature_cols])
        model = Pipeline([('transform', transformer),
                          ('model', RandomForestRegressor(max_depth=10, n_estimators=200))])

        model.fit(train_df, sales)
        self.base_model = model

    def evaluate(self, prepared_data):
        val_df = prepared_data['val_df']
        y_pred = self.base_model.predict(val_df[self.feature_cols])
        y_true = val_df['Sales']
        self.metrics = {'mae': sklearn.metrics.mean_absolute_error(y_true, y_pred),
                        }

    def predict(self, input_data):
        # repeat this because input_data might not be "prepared" e.g. come from another test file
        store_info = pd.read_csv(os.path.join(self.data_dir, "store.csv"))
        input_data = input_data.merge(store_info, on="Store")

        input_data.fillna(0, inplace=True)
        
        input_data["Date"] = pd.to_datetime(input_data.Date)
        input_data["DayOfWeek"] = input_data.Date.dt.dayofweek
        input_data["DayOfMonth"] = input_data.Date.dt.day
        input_data["Month"] = input_data.Date.dt.month

        input_data = input_data[self.feature_cols]
        result = self.base_model.predict(input_data)
        
        return result
