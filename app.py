from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import urllib.parse

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")

# MONGO_URI CORREGIDA - REEMPLAZA CON LA TUYA
MONGO_URI = os.environ.get(
    "MONGO_URI", 
    "mongodb+srv://vazquezjimenezarelycbtis272_db_user:admin1234@cluster0.xxxxx.mongodb.net/ecoconnect_db?retryWrites=true&w=majority"
)

# Codificar contraseña si tiene caracteres especiales
username = "vazquezjimenezarelycbtis272_db_user"
password = "admin1234"
encoded_password = urllib.parse.quote_plus(password)

# MONGO_URI con contraseña codificada
MONGO_URI = f"mongodb+srv://vazquezjimenezarelycbtis272_db_user:admin1234@cluster0.xxxxx.mongodb.net/ecoconnect_db?retryWrites=true&w=majority"

db = None
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Probar la conexión
    client.admin.command('ping')
    db = client.ecoconnect_db
    print("✅ Conexión exitosa a MongoDB Atlas")
except Exception as e:
    print(f"❌ Error de conexión a MongoDB Atlas: {e}")
    # Intentar con MongoDB local como fallback
    try:
        client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        db = client.ecoconnect_db
        print("✅ Conectado a MongoDB local")
    except Exception as e2:
        print(f"❌ No se pudo conectar a MongoDB local: {e2}")
        db = None

# Rutas actualizadas para ECOCONNECT
@app.route("/")
def index():
    if db is None:
        flash("Error: La base de datos no está conectada.", "danger")
        return render_template("index.html", datos=[])
    try:
        datos = list(db.puntos_reciclaje.find())
        return render_template("index.html", datos=datos)
    except Exception as e:
        flash(f"Error al obtener datos: {e}", "danger")
        return render_template("index.html", datos=[])

@app.route("/new", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        if db is None:
            flash("Error: Base de datos no conectada.", "danger")
            return redirect(url_for("index"))
        
        # Campos para ECOCONNECT
        nombre = request.form.get("nombre", "").strip()
        materiales = request.form.get("materiales", "").strip()
        direccion = request.form.get("direccion", "").strip()
        horarios = request.form.get("horarios", "").strip()
        telefono = request.form.get("telefono", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        if not all([nombre, materiales, direccion, horarios, descripcion]):
            flash("Completa todos los campos obligatorios.", "danger")
            return redirect(url_for("create"))

        try:
            db.puntos_reciclaje.insert_one({
                "nombre": nombre,
                "materiales": materiales,
                "direccion": direccion,
                "horarios": horarios,
                "telefono": telefono,
                "descripcion": descripcion
            })
            flash("Punto de reciclaje creado correctamente.", "success")
        except Exception as e:
            flash(f"Error al crear registro: {e}", "danger")

        return redirect(url_for("index"))
    
    return render_template("create.html")

@app.route("/view/<id>")
def view(id):
    if db is None:
        flash("Base de datos no conectada.", "danger")
        return redirect(url_for("index"))
    try:
        dato = db.puntos_reciclaje.find_one({"_id": ObjectId(id)})
        if not dato:
            flash("Punto de reciclaje no encontrado.", "warning")
            return redirect(url_for("index"))
        return render_template("view.html", dato=dato)
    except Exception as e:
        flash(f"Error al obtener datos: {e}", "danger")
        return redirect(url_for("index"))

@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    if db is None:
        flash("Base de datos no conectada.", "danger")
        return redirect(url_for("index"))
    
    try:
        dato = db.puntos_reciclaje.find_one({"_id": ObjectId(id)})
        if not dato:
            flash("Punto de reciclaje no encontrado.", "warning")
            return redirect(url_for("index"))

        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            materiales = request.form.get("materiales", "").strip()
            direccion = request.form.get("direccion", "").strip()
            horarios = request.form.get("horarios", "").strip()
            telefono = request.form.get("telefono", "").strip()
            descripcion = request.form.get("descripcion", "").strip()

            if not all([nombre, materiales, direccion, horarios, descripcion]):
                flash("Completa todos los campos obligatorios.", "danger")
                return redirect(url_for("edit", id=id))

            db.puntos_reciclaje.update_one(
                {"_id": ObjectId(id)},
                {"$set": {
                    "nombre": nombre,
                    "materiales": materiales,
                    "direccion": direccion,
                    "horarios": horarios,
                    "telefono": telefono,
                    "descripcion": descripcion
                }}
            )
            flash("Punto de reciclaje actualizado correctamente.", "info")
            return redirect(url_for("index"))

        return render_template("edit.html", dato=dato)
    except Exception as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for("index"))

@app.route("/delete/<id>", methods=["POST"])
def delete(id):
    if db is None:
        flash("Base de datos no conectada.", "danger")
        return redirect(url_for("index"))
    try:
        db.puntos_reciclaje.delete_one({"_id": ObjectId(id)})
        flash("Punto de reciclaje eliminado correctamente.", "secondary")
    except Exception as e:
        flash(f"Error al eliminar: {e}", "danger")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
