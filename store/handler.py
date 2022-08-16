import os

from datetime import datetime
from json import load, dump


class Handler:

    def __init__(self, db_location=None):

        self._db = db_location or 'store/db.json'

    def get(self):
        '''returns entire database'''

        with open(self._db) as db:
            return load(db)
    
    def get_keys(self):
        '''returns all non-nested keys within database'''

        return self.get().keys()
    
    def get_value(self, key, default=None):
        ''' returns the value of a provided key within database'''

        return self.get().get(key, default)

    def get_nested_value(self, keys=[], default=None):
        '''traverse the database for the desired nested value'''

        if len(keys) == 0:
            return

        first_key = keys[0]
        traversed = self.get_value(key=first_key, default=default)

        if len(keys) > 1:
            for key in keys[1:]:
                if traversed == default:
                    return traversed
                
                traversed = traversed.get(key, default)
        
        return traversed

    def write_all(self, new_db):
        '''re-writes over existing database with new database'''

        with open(self._db, 'w') as db:
            return dump(new_db, db, indent=4)        
    
    def overwrite(self, db_key, db_value):
        '''re-writes the record within database for key with new value'''

        db = self.get()

        db[db_key] = db_value

        return self.write_all(new_db=db)
    
    def snapshot(self):
        '''take snapshot of existing database'''

        try:
            os.mkdir('snapshots')
        except OSError:
            pass

        timestamp = datetime.now().strftime("%d%m%y")
        snapshot = 'snapshots/db_snapshot_{}'.format(timestamp)
        
        with open(snapshot, 'w') as snapshot_db:
            return dump(self.get(), snapshot_db, indent=4)