import sqlite3
import numpy as np
import io

def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


class Storage:
    def __init__(self):
        """
        https://stackoverflow.com/questions/18621513/python-insert-numpy-array-into-sqlite3-database
        """
        # Converts np.array to TEXT when inserting
        sqlite3.register_adapter(np.ndarray, adapt_array)

        # Converts TEXT to np.array when selecting
        sqlite3.register_converter("array", convert_array)

        self.con = sqlite3.connect("song_info.db", detect_types=sqlite3.PARSE_DECLTYPES)
        self.cur = self.con.cursor()
        self.cur.execute("create table if not exists song_info (song_hash text, wave_form array, duration int)")

if __name__ == "__main__":
    s = Storage()
    s.cur.execute("select * from song_info")
    print(s.cur.fetchall())