####################################
# Mechanic - Kart Repair Management
# Version 1.0.1
# Author: Yehan Edirisinghe
# Mail: yehan278@gmail.com
# Date: 2025-01
####################################

import sqlite3




class Mechanic:

    def __init__(self):

        self.__version__ = "1.0.0"
                
        self.conn = sqlite3.connect("repair.db")
        c = self.conn.cursor()

        # Tabella Kart
        c.execute("""
        CREATE TABLE IF NOT EXISTS kart (
            kart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            kart_num INTEGER UNIQUE,
            modello TEXT,
            stato TEXT
        )
        """)

        # Tabella Pezzi
        c.execute("""
        CREATE TABLE IF NOT EXISTS pezzi (
            pezzo_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_pezzo TEXT,
            codice TEXT,
            costo_unitario REAL
        )
        """)

        # Tabella Tecnici
        c.execute("""
        CREATE TABLE IF NOT EXISTS tecnici (
            tecnico_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cognome TEXT,
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
        return sqlite3.connect("repair.db")
    
    def add_kart(self, kart_num:int, modello:str, stato:str):

        conn = self.get_connection()
        c = conn.cursor()

        try:
            c.execute(
                "INSERT INTO kart (kart_num, modello, stato) VALUES (?, ?, ?)",
                (kart_num, modello, stato)
            )
            conn.commit()
            print(f"Kart {kart_num} aggiunto con successo.")

        except sqlite3.IntegrityError:
            print(f"Errore: Il kart con numero {kart_num} esiste già.")
        
        conn.close()

    def add_piece(self, nome_pezzo:str, codice:str, costo_unitario:float):
        conn = self.get_connection()
        c = conn.cursor()

        c.execute(
            "INSERT INTO pezzi (nome_pezzo, codice, costo_unitario) VALUES (?, ?, ?)",
            (nome_pezzo, codice, costo_unitario)
        )

        conn.commit()
        print(f"Pezzo {nome_pezzo} aggiunto con successo.")
        conn.close()
    
    def add_technician(self, nome, cognome, specializzazione):
        conn = self.get_connection()
        c = conn.cursor()

        c.execute(
            "INSERT INTO tecnici (nome, cognome, specializzazione) VALUES (?, ?, ?)",
            (nome, cognome, specializzazione)
        )

        conn.commit()
        print(f"Tecnico {nome} {cognome} creato con successo.")
        conn.close()

    def add_repair(self, kart_num:int, nome_pezzo:str, data:str, tecnico:str, descrizione:str):

        conn = self.get_connection()
        c = conn.cursor()

        # Trova kart_id dal numero
        c.execute("SELECT kart_id FROM kart WHERE kart_num = ?", (kart_num,))
        kart_res = c.fetchone()

        if kart_res is None:
            print(f"Errore: Nessun kart con numero {kart_num} trovato.")
            conn.close()
            return
        else:
            kart_id = kart_res[0]
        
        c.execute("SELECT pezzo_id FROM pezzi WHERE nome_pezzo = ?", (nome_pezzo,))
        pezzo_res = c.fetchone()
        if pezzo_res is None:
            print(f"Errore: Nessun pezzo con nome {nome_pezzo} trovato.")
            conn.close()
            return
        else:
            pezzo_id = pezzo_res[0]

        c.execute("SELECT tecnico_id FROM tecnici WHERE nome = ?", (tecnico,))
        tecnico_res = c.fetchone()
        if tecnico_res is None:
            print(f"Errore: Nessun tecnico con nome {tecnico} trovato.")
            conn.close()
            return
        else:
            tecnico_id = tecnico_res[0]

        c.execute(
            "INSERT INTO riparazioni (kart_id, pezzo_id, tecnico_id, data_riparazione, descrizione) VALUES (?, ?, ?, ?, ?)",
            (kart_id, pezzo_id, tecnico_id, data, descrizione)
        )
        conn.commit()
        print(f"Riparazione per kart {kart_num} aggiunta con successo.")
        conn.close()


    def list_technicians(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT tecnico_id, nome, cognome, specializzazione FROM tecnici")
        tecnici = c.fetchall()
        for tecnico in tecnici:
            print(f"Tecnico: {tecnico[1]} {tecnico[2]}, Specializzazione: {tecnico[3]}")
        conn.close()
    
    def list_karts(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT kart_id, kart_num, modello, stato FROM kart")
        karts = c.fetchall()
        for kart in karts:
            print(kart)
        conn.close()

    def list_pieces(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT pezzo_id, nome_pezzo, codice, costo_unitario FROM pezzi")
        pezzi = c.fetchall()
        for pezzo in pezzi:
            print(f"Pezzo: {pezzo[1]}, Codice: {pezzo[2]}, Costo Unitario: {pezzo[3]}")
        conn.close()

    def list_repairs(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""
        SELECT r.id_riparazione, k.kart_num, p.nome_pezzo, t.nome || ' ' || t.cognome AS tecnico_nome, r.data_riparazione, r.descrizione
        FROM riparazioni r
        JOIN kart k ON r.kart_id = k.kart_id
        JOIN pezzi p ON r.pezzo_id = p.pezzo_id
        JOIN tecnici t ON r.tecnico_id = t.tecnico_id
        """)
        riparazioni = c.fetchall()
        for riparazione in riparazioni:
            print(f"Riparazione ID: {riparazione[0]}, Kart Num: {riparazione[1]}, Pezzo: {riparazione[2]}, Tecnico: {riparazione[3]}, Data: {riparazione[4]}, Descrizione: {riparazione[5]}")
        conn.close()

    def filter_by_kart(self, kart_num:int):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""
        SELECT r.id_riparazione, k.kart_num, p.nome_pezzo, t.nome || ' ' || t.cognome AS tecnico_nome, r.data_riparazione, r.descrizione
        FROM riparazioni r
        JOIN kart k ON r.kart_id = k.kart_id
        JOIN pezzi p ON r.pezzo_id = p.pezzo_id
        JOIN tecnici t ON r.tecnico_id = t.tecnico_id
        WHERE k.kart_num = ?
        """, (kart_num,))
        riparazioni = c.fetchall()
        for riparazione in riparazioni:
            print(f"Riparazione ID: {riparazione[0]}, Kart Num: {riparazione[1]}, Pezzo: {riparazione[2]}, Tecnico: {riparazione[3]}, Data: {riparazione[4]}, Descrizione: {riparazione[5]}")
        conn.close()

    def filter_by_technician(self, tecnico_nome:str):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""
        SELECT r.id_riparazione, k.kart_num, p.nome_pezzo, t.nome || ' ' || t.cognome AS tecnico_nome, r.data_riparazione, r.descrizione
        FROM riparazioni r
        JOIN kart k ON r.kart_id = k.kart_id
        JOIN pezzi p ON r.pezzo_id = p.pezzo_id
        JOIN tecnici t ON r.tecnico_id = t.tecnico_id
        WHERE t.nome || ' ' || t.cognome = ?
        """, (tecnico_nome,))
        riparazioni = c.fetchall()
        for riparazione in riparazioni:
            print(f"Riparazione ID: {riparazione[0]}, Kart Num: {riparazione[1]}, Pezzo: {riparazione[2]}, Tecnico: {riparazione[3]}, Data: {riparazione[4]}, Descrizione: {riparazione[5]}")
        conn.close()

    def filter_by_date(self, data_riparazione:str):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""
        SELECT r.id_riparazione, k.kart_num, p.nome_pezzo, t.nome || ' ' || t.cognome AS tecnico_nome, r.data_riparazione, r.descrizione
        FROM riparazioni r
        JOIN kart k ON r.kart_id = k.kart_id
        JOIN pezzi p ON r.pezzo_id = p.pezzo_id
        JOIN tecnici t ON r.tecnico_id = t.tecnico_id
        WHERE r.data_riparazione = ?
        """, (data_riparazione,))
        riparazioni = c.fetchall()
        for riparazione in riparazioni:
            print(f"Riparazione ID: {riparazione[0]}, Kart Num: {riparazione[1]}, Pezzo: {riparazione[2]}, Tecnico: {riparazione[3]}, Data: {riparazione[4]}, Descrizione: {riparazione[5]}")
        conn.close()
    
    def filter_by_piece(self, nome_pezzo:str):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""
        SELECT r.id_riparazione, k.kart_num, p.nome_pezzo, t.nome || ' ' || t.cognome AS tecnico_nome, r.data_riparazione, r.descrizione
        FROM riparazioni r
        JOIN kart k ON r.kart_id = k.kart_id
        JOIN pezzi p ON r.pezzo_id = p.pezzo_id
        JOIN tecnici t ON r.tecnico_id = t.tecnico_id
        WHERE p.nome_pezzo = ?
        """, (nome_pezzo,))
        riparazioni = c.fetchall()
        for riparazione in riparazioni:
            print(f"Riparazione ID: {riparazione[0]}, Kart Num: {riparazione[1]}, Pezzo: {riparazione[2]}, Tecnico: {riparazione[3]}, Data: {riparazione[4]}, Descrizione: {riparazione[5]}")
        conn.close()
    
    def close_connection(self, conn):
        conn.close()

if __name__ == "__main__":

    mechanic = Mechanic()
    mechanic.filter_by_kart(1)