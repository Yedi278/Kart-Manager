####################################
# Mechanic - Kart Repair Management
# Version 1.0.2
# Author: Yehan Edirisinghe
# Mail: yehan278@gmail.com
# Date: 2025-01
####################################

from Mechanic import Mechanic
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
db = Mechanic()


@app.route("/")
def home():
    conn = db.get_connection()
    c = conn.cursor()

    # Parametri filtro da query string
    kart_id = request.args.get("kart_id")
    pezzo_id = request.args.get("pezzo_id")
    data_riparazione = request.args.get("data_riparazione")

    # Query base riparazioni
    query = """
        SELECT r.id_riparazione,
               k.kart_num,
               p.nome_pezzo,
               t.nome || ' ' || t.cognome,
               r.data_riparazione,
               r.quantità,
               r.descrizione
        FROM riparazioni r
        JOIN kart k ON r.kart_id = k.kart_id
        JOIN pezzi p ON r.pezzo_id = p.pezzo_id
        JOIN tecnici t ON r.tecnico_id = t.tecnico_id
    """
    filters = []
    params = []

    if kart_id:
        filters.append("r.kart_id = ?")
        params.append(kart_id)
    if pezzo_id:
        filters.append("r.pezzo_id = ?")
        params.append(pezzo_id)
    if data_riparazione:
        filters.append("r.data_riparazione = ?")
        params.append(data_riparazione)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY r.data_riparazione DESC"

    c.execute(query, params)
    repairs = c.fetchall()

    # Recupero tutti i kart, pezzi e tecnici per i select
    c.execute("SELECT kart_id, kart_num, modello FROM kart")
    karts = c.fetchall()

    c.execute("SELECT pezzo_id, nome_pezzo, codice FROM pezzi")
    parts = c.fetchall()

    c.execute("SELECT tecnico_id, nome, cognome FROM tecnici")
    technicians = c.fetchall()

    conn.close()

    return render_template(
        "index.html",
        repairs=repairs,
        karts=karts,
        parts=parts,
        technicians=technicians,
        selected_kart=kart_id,
        selected_pezzo=pezzo_id,
        selected_data=data_riparazione
    )

@app.route("/add_repair", methods=["POST"])
def add_repair():
    kart_id = int(request.form["kart_id"])
    tecnico_id = int(request.form["tecnico_id"])
    pezzo_id = int(request.form["pezzo_id"])
    data_riparazione = request.form["data_riparazione"]
    quantità = int(request.form["quantità"])
    descrizione = request.form["descrizione"]

    conn = db.get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO riparazioni (kart_id, tecnico_id, pezzo_id, data_riparazione, quantità, descrizione) VALUES (?, ?, ?, ?, ?, ?)",
        (kart_id, tecnico_id, pezzo_id, data_riparazione, quantità, descrizione)
    )
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/remove_repair/<int:repair_id>")
def remove_repair(repair_id: int):
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM riparazioni WHERE id_riparazione = ?", (repair_id,))
    conn.commit()
    conn.close()
    return redirect("/")  # torna alla home

@app.route("/karts")
def karts():
    conn = db.get_connection()
    c = conn.cursor()

    c.execute("""
    SELECT kart_id, kart_num, modello, stato
    FROM kart
    ORDER BY kart_num ASC
    """)

    karts = c.fetchall()

    conn.close()
    return render_template("karts.html", karts=karts)

@app.route("/add_kart", methods=["POST"])
def add_kart():
    kart_num = int(request.form["kart_num"])
    modello = request.form["modello"]
    stato = request.form["stato"]

    conn = db.get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO kart (kart_num, modello, stato) VALUES (?, ?, ?)",
        (kart_num, modello, stato)
    )
    conn.commit()
    conn.close()
    return redirect("/karts")

@app.route("/remove_kart/<int:kart_id>")
def remove_kart(kart_id):
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM kart WHERE kart_id = ?", (kart_id,))
    conn.commit()
    conn.close()
    return redirect("/karts")

@app.route("/technicians")
def technicians():
    conn = db.get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT tecnico_id, nome, cognome, specializzazione
        FROM tecnici
        ORDER BY tecnico_id ASC
    """)

    technicians = c.fetchall()
    conn.close()
    return render_template("technicians.html", technicians=technicians)

@app.route("/add_technician", methods=["POST"])
def add_technician():
    nome = request.form["nome"]
    cognome = request.form["cognome"]
    specializzazione = request.form.get("specializzazione", "")

    conn = db.get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO tecnici (nome, cognome, specializzazione) VALUES (?, ?, ?)",
        (nome, cognome, specializzazione)
    )
    conn.commit()
    conn.close()
    return redirect("/technicians")

@app.route("/remove_technician/<int:tecnico_id>")
def remove_technician(tecnico_id):
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM tecnici WHERE tecnico_id = ?", (tecnico_id,))
    conn.commit()
    conn.close()
    return redirect("/technicians")

@app.route("/parts")
def parts():
    conn = db.get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT pezzo_id, nome_pezzo, codice, costo_unitario
        FROM pezzi
        ORDER BY pezzo_id ASC
    """)

    parts = c.fetchall()
    conn.close()
    return render_template("parts.html", parts=parts)

@app.route("/add_part", methods=["POST"])
def add_part():
    nome_pezzo = request.form["nome_pezzo"]
    codice = request.form["codice"]
    costo_unitario = float(request.form["costo_unitario"])

    conn = db.get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO pezzi (nome_pezzo, codice, costo_unitario) VALUES (?, ?, ?)",
        (nome_pezzo, codice, costo_unitario)
    )
    conn.commit()
    conn.close()
    return redirect("/parts")

@app.route("/remove_part/<int:pezzo_id>")
def remove_part(pezzo_id: int):
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM pezzi WHERE pezzo_id = ?", (pezzo_id,))
    conn.commit()
    conn.close()
    return redirect("/parts")

@app.route("/change_kart_status/<int:kart_id>/<new_status>")
def change_kart_status(kart_id: int, new_status: str):
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("UPDATE kart SET stato = ? WHERE kart_id = ?", (new_status, kart_id))
    conn.commit()
    conn.close()
    return redirect("/karts")

@app.route("/change_repair_description/<int:repair_id>/<new_description>")
def change_repair_description(repair_id: int, new_description: str):
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("UPDATE riparazioni SET descrizione = ? WHERE id_riparazione = ?", (new_description, repair_id))
    conn.commit()
    conn.close()
    return redirect("/")


app.run(debug=False)