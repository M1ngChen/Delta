import pandas as pd







class PandasMapping:
    def __init__(self,mapping_datas:dict):
        super().__init__()
        self.data_frame = pd.DataFrame(mapping_datas)
    
    def query(self,key,value):
        return self.data_frame[self.data_frame[key] == value].to_dict(orient='records')

    def insert(self,data:list):
        self.data_frame.loc[len(self.data_frame)] = data

    def delete(self,index):
        self.data_frame.drop(index=index)
    
    def update(self,index,key,value):
        self.data_frame.loc[index,[key]] = [value]
    
    def query_key(self,key:str) ->list:
        try:
            return self.data_frame[key].to_list()
        except Exception as e:
            print(f"dont exist key:{key}")
            return []


    


