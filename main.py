####################################
# Mechanic - Kart Repair Management
# Version 1.1.1
# Author: Yehan Edirisinghe
# Mail: yehan278@gmail.com
# Date: 2025-01
####################################

import io, os, sys
from Mechanic import Mechanic
from flask import Flask, render_template, request, redirect
from flask import send_file
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime


sede="Bicocca"

def resource_path(relative_path):
    """ Ottiene il path corretto sia in sviluppo che in .exe """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

template_dir = resource_path("templates")
static_dir = resource_path("static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
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
            COALESCE(k.kart_num, 'Kart rimosso') AS kart_num,
            p.nome_pezzo,
            t.nome || ' ' || t.cognome,
            r.data_riparazione,
            r.quantità,
            r.descrizione

        FROM riparazioni r
        LEFT JOIN kart k ON r.kart_id = k.kart_id
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
    c.execute("""
        SELECT kart_id, kart_num, modello
        FROM kart
        WHERE stato != 'Dismesso'
        ORDER BY kart_num ASC
    """)
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
    filtro_modello = request.args.get("modello")
    filtro_stato = request.args.get("stato")

    conn = db.get_connection()
    c = conn.cursor()

    query = """
        SELECT kart_id, kart_num, modello, stato, note
        FROM kart
    """

    filters = []
    params = []

    if filtro_modello:
        filters.append("modello = ?")
        params.append(filtro_modello)

    if filtro_stato and filtro_stato != "Tutti":
        filters.append("stato = ?")
        params.append(filtro_stato)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY kart_num ASC"

    c.execute(query, params)
    karts = c.fetchall()

    # 🔹 Lista modelli per filtro
    c.execute("SELECT DISTINCT modello FROM kart ORDER BY modello")
    modelli = [row[0] for row in c.fetchall()]

    # 🔹 Lista stati REALI presenti nel DB
    c.execute("SELECT DISTINCT stato FROM kart ORDER BY stato")
    stati = [row[0] for row in c.fetchall()]

    conn.close()

    return render_template(
        "karts.html",
        karts=karts,
        modelli=modelli,
        stati=stati,
        filtro_modello=filtro_modello,
        filtro_stato=filtro_stato
    )


@app.route("/add_kart", methods=["POST"])
def add_kart():
    kart_num = int(request.form["kart_num"])
    modello = request.form["modello"]
    stato = request.form["stato"]
    # add blank note by default
    note = ""

    conn = db.get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO kart (kart_num, modello, stato, note) VALUES (?, ?, ?, ?)",
        (kart_num, modello, stato, note)
    )
    conn.commit()
    conn.close()
    return redirect("/karts")

@app.route("/update_kart_note/<int:kart_id>", methods=["POST"])
def update_kart_note(kart_id: int):
    note = request.form["note"]

    conn = db.get_connection()
    c = conn.cursor()
    c.execute("UPDATE kart SET note = ? WHERE kart_id = ?", (note, kart_id))
    conn.commit()
    conn.close()
    return redirect("/karts")

@app.route("/remove_kart/<int:kart_id>")
def remove_kart(kart_id):
    conn = db.get_connection()
    c = conn.cursor()
    
    c.execute("UPDATE riparazioni SET kart_id = NULL WHERE kart_id = ?", (kart_id,))    
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
        SELECT pezzo_id, nome_pezzo, codice, costo_unitario, ricomprare
        FROM pezzi
        ORDER BY pezzo_id ASC
    """)

    parts = c.fetchall()
    conn.close()
    return render_template("parts.html", parts=parts)

@app.route("/toggle_reorder/<int:pezzo_id>", methods=["POST"])
def toggle_reorder(pezzo_id: int):
    conn = db.get_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE pezzi
        SET ricomprare = CASE ricomprare WHEN 1 THEN 0 ELSE 1 END
        WHERE pezzo_id = ?
    """, (pezzo_id,))

    conn.commit()
    conn.close()

    return redirect(request.referrer or "/parts")

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

@app.route("/report")
def generate_report():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    conn = db.get_connection()
    c = conn.cursor()

    # ===== TITOLO =====
    title = Paragraph(f"Report Kart - Sede {sede}", styles["Title"])
    date = Paragraph(f"Generato il: {datetime.now().strftime('%d/%m/%Y')}", styles["Normal"])
    elements.extend([title, Spacer(1, 10), date, Spacer(1, 20)])

    # ===== SEZIONE KART =====
    elements.append(Paragraph("Stato Kart", styles["Heading2"]))
    c.execute("SELECT kart_num, modello, stato, note FROM kart ORDER BY kart_num")
    karts = c.fetchall()

    kart_data = [["Kart", "Modello", "Stato", "Note"]]
    for k in karts:
        if k[2] != "Dismesso":
            kart_data.append(list(k))

    kart_table = Table(kart_data, repeatRows=1)
    kart_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))

    elements.append(kart_table)

    elements.append(PageBreak())

    # ===== SEZIONE PEZZI =====
    elements.append(Paragraph("Pezzi da Ricomprare", styles["Heading2"]))
    c.execute("SELECT nome_pezzo, codice, costo_unitario, ricomprare FROM pezzi WHERE ricomprare = 1 ORDER BY nome_pezzo")
    parts = c.fetchall()

    parts_data = [["Pezzo", "Codice", "Costo €", "Da ricomprare"]]
    for p in parts:
        parts_data.append([p[0], p[1], f"{p[2]:.2f}", "SI"])

    parts_table = Table(parts_data, repeatRows=1)
    parts_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (2, 1), (2, -1), "RIGHT"),
        ("ALIGN", (3, 1), (3, -1), "CENTER"),
    ]))

    elements.append(parts_table)

    conn.close()

    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True,
                     download_name="report_kart_bicocca.pdf",
                     mimetype="application/pdf")

app.run(host="0.0.0.0", port=5000, debug=False)