# reviews.py
import os
import sqlite3
import unittest

from sql30 import db

DB_NAME = './review.db'
BACKUP_DB = './review_backup.db'


class Reviews(db.Model):
    TABLE = 'reviews'
    PKEY = 'rid'
    DB_SCHEMA = {
        'db_name': DB_NAME,
        'tables': [
            {
                'name': TABLE,
                'fields': {
                    'rid': 'uuid',
                    'header': 'text',
                    'rating': 'int',
                    'desc': 'text'
                    },
                'primary_key': PKEY
            }]
        }
    VALIDATE_BEFORE_WRITE = True


class ReviewTest(unittest.TestCase):

    def setUp(self):
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)

    def test_table_not_set(self):
        """
        Tests for raise of assertion when table is not set.
        """
        db = Reviews()
        try:
            db.read()
        except Exception as err:
            self.assertIn('No table set for operation', str(err))

    def test_primary_key(self):
        """
        Ensures , primary key is honored.
        """
        db = Reviews()
        db.table = 'reviews'
        db.write(rid=10, rating=5)
        try:
            db.write(rid=10, rating=4)
        except sqlite3.IntegrityError as err:
            self.assertIn('UNIQUE constraint failed', str(err))

    def _test_CREATE(self):
        db = Reviews()
        db.table = 'reviews'
        # backward compatibility for 'write' API
        db.write(tbl='reviews', rid=1, header='good thing', rating=5)

        # New API with 'create'
        db.create(tbl='reviews', rid=2, header='good thing', rating=5)

        # backward compatibility for 'write' API, without tbl,
        # explicitly passed
        db.write(tbl='reviews', rid=3, header='good thing', rating=5)

        # New API with 'create', without table name explicitly passed.
        db.create(tbl='reviews', rid=4, header='good thing', rating=5)

        db.commit()   # save the work.

    def _test_READ(self):
        db = Reviews()
        db.table = 'reviews'

        rec1 = db.read(tbl='reviews', rid=1, header='good thing', rating=5)
        rec2 = db.read(rid=1, header='good thing')
        rec3 = db.read(rid=1)

        self.assertEqual(rec1, rec2)
        self.assertEqual(rec2, rec3)

        recs = db.read()  # read all
        self.assertEqual(len(recs), 4)

    def _test_UPDATE(self):
        db = Reviews()
        db.table = 'reviews'

        where = {'rid': 2}
        db.update(condition=where, header='average item', rating=2)
        db.commit()

        rec = db.read(rid=2)[0]
        self.assertIn('average item', rec)

    def _test_DELETE(self):
        db = Reviews()
        db.table = 'reviews'

        db.delete(rid=2)
        db.commit()
        self.assertFalse(db.read(rid=2))

    def _test_export(self):
        db = Reviews()
        db.export(dbfile=BACKUP_DB) 

    def test_CRUD(self):
        self._test_CREATE()
        self._test_READ()
        self._test_UPDATE()
        
        # Export file and ensure it exists.
        self._test_export()
        assert os.path.exists(BACKUP_DB)
        os.remove(BACKUP_DB)

        self._test_DELETE()

    def tearDown(self):
        os.remove(DB_NAME)
        
