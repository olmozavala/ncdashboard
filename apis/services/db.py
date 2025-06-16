"""
Database Services Module

This module provides services for managing the application's database.
It handles operations for storing and retrieving datasets and sessions using a JSON-based storage system.
"""

import json
import os
from models import NC_DataBaseType, Session, Dataset
# This is a placeholder for the database connection

# Database configuration
db_json_path = 'db.json'

# Initial database state
db_initial_state: NC_DataBaseType = {
    'datasets': [],
    'sessions': []
}

class NC_DB:
    """
    Database management class for handling datasets and sessions.
    
    This class provides methods for:
    - Loading and saving the database
    - Managing sessions (add, get, update)
    - Managing datasets (add, get, update)
    """
    
    def __init__(self):
        """
        Initialize the database and load existing data.
        """
        self.db: NC_DataBaseType = db_initial_state
        # self.load_db()
    
    def load_db(self):
        """
        Load the database from the JSON file.
        Creates a new database file if it doesn't exist.
        """
        if not os.path.exists(db_json_path):
            with open(db_json_path, 'w') as db_file:
                json.dump(db_initial_state, db_file)
        with open(db_json_path, 'r') as db_file:
            self.db = json.load(db_file)
            
    async def save_db(self):
        """
        Save the current database state to the JSON file.
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        with open(db_json_path, 'w') as db_file:
            json.dump(self.db, db_file, default=str)
            return True
        return False
            
    def add_session(self, session: Session):
        """
        Add a new session or update an existing one.
        
        Args:
            session (Session): The session to add or update
            
        Returns:
            Session: The added/updated session
        """
        if self.get_session(session['id']):
            self.update_session(session['id'], session)
            return session
        self.db['sessions'].append(session)
        return session
    
    def get_session(self, session_id: str):
        """
        Retrieve a session by its ID.
        
        Args:
            session_id (str): The ID of the session to retrieve
            
        Returns:
            Session: The requested session, or None if not found
        """
        for session in self.db['sessions']:
            if session['id'] == session_id:
                return session
        return None
    
    def update_session(self, session_id: str, session: Session):
        """
        Update an existing session.
        
        Args:
            session_id (str): The ID of the session to update
            session (Session): The new session data
            
        Raises:
            Exception: If the session is not found
        """
        for i, s in enumerate(self.db['sessions']):
            if s['id'] == session_id:
                self.db['sessions'][i] = session
                return
        raise Exception('Session not found')
    
    def add_dataset(self, dataset: Dataset):
        """
        Add a new dataset or update an existing one.
        
        Args:
            dataset (Dataset): The dataset to add or update
            
        Returns:
            Dataset: The added/updated dataset
        """
        if dataset in self.db['datasets']:
            self.update_dataset(dataset)
            return dataset
        self.db['datasets'].append(dataset)
        return dataset
    
    def update_dataset(self, dataset: Dataset):
        """
        Update an existing dataset.
        
        Args:
            dataset (Dataset): The new dataset data
            
        Raises:
            Exception: If the dataset is not found
        """
        for i, d in enumerate(self.db['datasets']):
            if d['id'] == dataset['id']:
                self.db['datasets'][i] = dataset
                return
        raise Exception('Dataset not found')
    
    def get_dataset_by_id(self, dataset_id: str):
        """
        Retrieve a dataset by its ID.
        
        Args:
            dataset_id (str): The ID of the dataset to retrieve
            
        Returns:
            Dataset: The requested dataset, or None if not found
        """
        for dataset in self.db['datasets']:
            if dataset['id'] == dataset_id:
                return dataset
        return None
    
    def get_dataset_by_name(self, dataset_name: str):
        """
        Retrieve a dataset by its name.
        
        Args:
            dataset_name (str): The name of the dataset to retrieve
            
        Returns:
            Dataset: The requested dataset, or None if not found
        """
        for dataset in self.db['datasets']:
            if dataset['name'] == dataset_name:
                return dataset
        return None
    
    def get_dataset_by_path(self, dataset_path: str):
        """
        Retrieve a dataset by its file path.
        
        Args:
            dataset_path (str): The path of the dataset to retrieve
            
        Returns:
            Dataset: The requested dataset, or None if not found
        """
        for dataset in self.db['datasets']:
            if dataset['path'] == dataset_path:
                return dataset
        return None
    

# Create a global database instance
nc_db = NC_DB()