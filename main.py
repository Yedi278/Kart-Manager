####################################
# Mechanic - Kart Repair Management
# Version 1.0.0
# Author: Yehan Edirisinghe
# Mail: yehan278@gmail.com
# Date: 2025-01
####################################

from Mechanic import Mechanic
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
db = Mechanic()

mechanic = Mechanic()

@app.route("/")
def home():
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT kart_id, kart_num, modello, stato FROM kart")
    karts = c.fetchall()
    conn.close()
    return render_template("index.html", karts=karts)

@app.route("/add_kart", methods=["POST"])
def add_kart():
    kart_num = request.form["kart_num"]
    modello = request.form["modello"]
    stato = request.form["stato"]

    db.add_kart(int(kart_num), modello, stato)
    return redirect("/")

@app.route("/repairs")
def repairs():
    conn = db.get_connection()
    c = conn.cursor()

    # Recupero riparazioni
    c.execute("""
        SELECT r.id_riparazione, k.kart_num, p.nome_pezzo,
            t.nome || ' ' || t.cognome,
            r.data_riparazione, r.descrizione
        FROM riparazioni r
        JOIN kart k ON r.kart_id = k.kart_id
        JOIN pezzi p ON r.pezzo_id = p.pezzo_id
        JOIN tecnici t ON r.tecnico_id = t.tecnico_id
    """)
    repairs = c.fetchall()

    # Recupero tutti i kart per la tendina
    c.execute("SELECT kart_id, kart_num, modello FROM kart")
    karts = c.fetchall()

    # Recupero tutti i pezzi per la tendina
    c.execute("SELECT pezzo_id, nome_pezzo FROM pezzi")
    pieces = c.fetchall()

    # Recupero tecnici per la tendina
    c.execute("SELECT tecnico_id, nome, cognome FROM tecnici")
    technicians = c.fetchall()

    conn.close()
    return render_template("repairs.html", repairs=repairs, karts=karts, pieces=pieces, technicians=technicians)

@app.route("/add_repair", methods=["POST"])
def add_repair():
    try:
        kart_id = int(request.form["kart_id"])
        pezzo_id = int(request.form["pezzo_id"])
        tecnico_id = int(request.form["tecnico_id"])
        data_riparazione = request.form["data_riparazione"]
        descrizione = request.form["descrizione"]

        conn = db.get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO riparazioni (kart_id, pezzo_id, tecnico_id, data_riparazione, descrizione) VALUES (?, ?, ?, ?, ?)",
            (kart_id, pezzo_id, tecnico_id, data_riparazione, descrizione)
        )
        conn.commit()
        conn.close()
        print(f"Riparazione aggiunta con successo per kart_id {kart_id}")

    except Exception as e:
        print(f"Errore nell'aggiungere riparazione: {e}")

    return redirect("/repairs")

@app.route("/remove_kart/<int:kart_id>")
def remove_kart(kart_id):
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM kart WHERE kart_id = ?", (kart_id,))
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/remove_technician/<int:tecnico_id>")
def remove_technician(tecnico_id):
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM tecnici WHERE tecnico_id = ?", (tecnico_id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/remove_piece/<int:pezzo_id>")
def remove_piece(pezzo_id):
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM pezzi WHERE pezzo_id = ?", (pezzo_id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/change_kart_status/<int:kart_id>/<new_status>")
def change_kart_status(kart_id:int, new_status:str):
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("UPDATE kart SET stato = ? WHERE kart_id = ?", (new_status, kart_id))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/remove_repair/<int:repair_id>")
def remove_repair(repair_id:int):
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM riparazioni WHERE id_riparazione = ?", (repair_id,))
    conn.commit()
    conn.close()

@app.route("/change_repair_description/<int:repair_id>/<new_description>")
def change_repair_description(repair_id:int, new_description:str):
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("UPDATE riparazioni SET descrizione = ? WHERE id_riparazione = ?", (new_description, repair_id))
    conn.commit()
    conn.close()

app.run(debug=False)