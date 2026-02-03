import sqlite3

class Mechanic:

    def __init__(self):

        self.__version__ = "1.0.0"

        self.database_name = "repairs.db"
                
        self.conn = sqlite3.connect(self.database_name)
        c = self.conn.cursor()

        # Tabella Kart
        c.execute("""
        CREATE TABLE IF NOT EXISTS kart (
            kart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            kart_num INTEGER UNIQUE,
            modello TEXT,
            stato TEXT,
            note TEXT
        )
        """)

        # Tabella Pezzi
        c.execute("""
        CREATE TABLE IF NOT EXISTS pezzi (
            pezzo_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_pezzo TEXT,
            codice TEXT,
            costo_unitario REAL,
            ricomprare BOOLEAN DEFAULT 0
        )
        """)

        # Tabella Tecnici
        c.execute("""
        CREATE TABLE IF NOT EXISTS tecnici (
            tecnico_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cognome TEXT,
            password TEXT,
            specializzazione TEXT
        )
        """)

        # Tabella Riparazioni
        c.execute("""
        CREATE TABLE IF NOT EXISTS riparazioni (
            id_riparazione INTEGER PRIMARY KEY AUTOINCREMENT,
            kart_id INTEGER,
            pezzo_id INTEGER,
            tecnico_id INTEGER,
            data_riparazione DATE,
            quantità INTEGER,
            descrizione TEXT,
            FOREIGN KEY (kart_id) REFERENCES kart(kart_id),
            FOREIGN KEY (pezzo_id) REFERENCES pezzi(pezzo_id),
            FOREIGN KEY (tecnico_id) REFERENCES tecnici(tecnico_id)
        )
        """)

        self.conn.commit()
        self.conn.close()

        print("Database creato con successo!")

    def get_connection(self):
        return sqlite3.connect(self.database_name)
        
    def close_connection(self, conn):
        conn.close()