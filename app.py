from flask import Flask, render_template, request
from rotas import buscar_rotas

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    resultados = None
    if request.method == "POST":
        resultados = buscar_rotas(
            request.form["origem"],
            request.form["destino"],
            request.form.get("prioridade"),
        )
    return render_template("index.html", resultados=resultados)

if __name__ == "__main__":
    app.run(debug=True)