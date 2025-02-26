import json
import os
from models import NC_DataBaseType, Session, Dataset
# This is a placeholder for the database connection

db_json_path = 'db.json'

db_initial_state:NC_DataBaseType = {
    'datasets': [],
    'sessions': []
}

class NC_DB:
    def __init__(self):
        self.db:NC_DataBaseType = db_initial_state
        self.load_db()
    
    def load_db(self):
        if not os.path.exists(db_json_path):
            with open(db_json_path, 'w') as db_file:
                json.dump(db_initial_state, db_file)
        with open(db_json_path, 'r') as db_file:
            self.db = json.load(db_file)
            
    async def save_db(self):
        with open(db_json_path, 'w') as db_file:
            json.dump(self.db, db_file, default=str)
            return True
        return False
            
    def add_session(self, session:Session):
        if self.get_session(session['id']):
            self.update_session(session['id'], session)
            return session
        self.db['sessions'].append(session)
        return session
    
    def get_session(self, session_id:str):
        for session in self.db['sessions']:
            if session['id'] == session_id:
                return session
        return None
    
    def update_session(self, session_id:str, session:Session):
        for i, s in enumerate(self.db['sessions']):
            if s['id'] == session_id:
                self.db['sessions'][i] = session
                return
        raise Exception('Session not found')
    
    def add_dataset(self, dataset:Dataset):
        if dataset in self.db['datasets']:
            self.update_dataset(dataset)
            return dataset
        self.db['datasets'].append(dataset)
        return dataset
    
    def update_dataset(self, dataset:Dataset):
        for i, d in enumerate(self.db['datasets']):
            if d['id'] == dataset['id']:
                self.db['datasets'][i] = dataset
                return
        raise Exception('Dataset not found')
    
    def get_dataset_by_id(self, dataset_id:str):
        for dataset in self.db['datasets']:
            if dataset['id'] == dataset_id:
                return dataset
        return None
    
    def get_dataset_by_name(self, dataset_name:str):
        for dataset in self.db['datasets']:
            if dataset['name'] == dataset_name:
                return dataset
        return None
    

nc_db = NC_DB()