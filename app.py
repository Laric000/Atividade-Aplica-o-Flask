import sqlite3
from functools import wraps

from flask import Flask, flash, g, redirect, render_template, request, session, url_for

app = Flask(__name__, template_folder="Templates")
app.secret_key = "dev-secret-key-change-this"
DATABASE = "banco.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_pet TEXT NOT NULL,
            nascimento TEXT NOT NULL,
            tutor TEXT NOT NULL,
            email TEXT NOT NULL,
            contato TEXT NOT NULL,
            endereco TEXT NOT NULL,
            bairro TEXT NOT NULL,
            servico TEXT NOT NULL,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
        """
    )
    connection.commit()
    connection.close()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("usuario_id") is None:
            flash("Faca login para acessar esta pagina.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.before_request
def load_logged_user():
    usuario_id = session.get("usuario_id")
    if usuario_id is None:
        g.usuario = None
        return

    connection = get_db_connection()
    g.usuario = connection.execute(
        "SELECT id, usuario FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    connection.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cadastro-usuario", methods=["GET", "POST"])
def cadastro_usuario():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "").strip()

        if not usuario or not senha:
            flash("Preencha usuario e senha.")
            return render_template("cadastro_usuario.html")

        connection = get_db_connection()
        try:
            connection.execute(
                "INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
                (usuario, senha),
            )
            connection.commit()
        except sqlite3.IntegrityError:
            flash("Usuario ja cadastrado.")
            connection.close()
            return render_template("cadastro_usuario.html")

        connection.close()
        flash("Cadastro realizado com sucesso. Faca login.")
        return redirect(url_for("login"))

    return render_template("cadastro_usuario.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "").strip()

        if not usuario or not senha:
            flash("Preencha usuario e senha.")
            return render_template("login.html")

        connection = get_db_connection()
        user = connection.execute(
            "SELECT id, usuario FROM usuarios WHERE usuario = ? AND senha = ?",
            (usuario, senha),
        ).fetchone()
        connection.close()

        if user is None:
            flash("Usuario ou senha invalidos.")
            return render_template("login.html")

        session.clear()
        session["usuario_id"] = user["id"]
        return redirect(url_for("agendamentos_listar"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/inicial")
@login_required
def inicial():
    return redirect(url_for("agendamentos_listar"))


@app.route("/servicos")
@login_required
def servicos():
    return render_template("servicos.html")


@app.route("/cadastro")
@login_required
def cadastro_legado():
    return redirect(url_for("agendamentos_novo"))


@app.route("/ficha")
@login_required
def ficha_legado():
    return redirect(url_for("agendamentos_listar"))


@app.route("/banho")
@login_required
def banho_legado():
    return redirect(url_for("agendamentos_novo"))


@app.route("/vacinas")
@login_required
def vacinas_legado():
    return redirect(url_for("agendamentos_novo"))


@app.route("/agendamentos")
@login_required
def agendamentos_listar():
    filtro_servico = request.args.get("servico", "").strip()
    connection = get_db_connection()

    if filtro_servico:
        agendamentos = connection.execute(
            """
            SELECT * FROM agendamentos
            WHERE usuario_id = ? AND servico LIKE ?
            ORDER BY id DESC
            """,
            (session["usuario_id"], f"%{filtro_servico}%"),
        ).fetchall()
    else:
        agendamentos = connection.execute(
            "SELECT * FROM agendamentos WHERE usuario_id = ? ORDER BY id DESC",
            (session["usuario_id"],),
        ).fetchall()

    connection.close()
    return render_template(
        "ficha.html",
        agendamentos=agendamentos,
        filtro_servico=filtro_servico,
    )


@app.route("/agendamentos/novo", methods=["GET", "POST"])
@login_required
def agendamentos_novo():
    if request.method == "POST":
        dados = {
            "nome_pet": request.form.get("nome_pet", "").strip(),
            "nascimento": request.form.get("nascimento", "").strip(),
            "tutor": request.form.get("tutor", "").strip(),
            "email": request.form.get("email", "").strip(),
            "contato": request.form.get("contato", "").strip(),
            "endereco": request.form.get("endereco", "").strip(),
            "bairro": request.form.get("bairro", "").strip(),
            "servico": request.form.get("servico", "").strip(),
        }

        if any(not valor for valor in dados.values()):
            flash("Preencha todos os campos do agendamento.")
            return render_template("cadastro.html", agendamento=dados, modo_edicao=False)

        connection = get_db_connection()
        connection.execute(
            """
            INSERT INTO agendamentos
            (nome_pet, nascimento, tutor, email, contato, endereco, bairro, servico, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dados["nome_pet"],
                dados["nascimento"],
                dados["tutor"],
                dados["email"],
                dados["contato"],
                dados["endereco"],
                dados["bairro"],
                dados["servico"],
                session["usuario_id"],
            ),
        )
        connection.commit()
        connection.close()
        flash("Agendamento cadastrado com sucesso.")
        return redirect(url_for("agendamentos_listar"))

    return render_template("cadastro.html", agendamento={}, modo_edicao=False)


@app.route("/agendamentos/<int:id>")
@login_required
def agendamentos_mostrar(id):
    connection = get_db_connection()
    agendamento = connection.execute(
        "SELECT * FROM agendamentos WHERE id = ? AND usuario_id = ?",
        (id, session["usuario_id"]),
    ).fetchone()
    connection.close()

    if agendamento is None:
        flash("Agendamento nao encontrado.")
        return redirect(url_for("agendamentos_listar"))

    return render_template("agendamento_detalhe.html", agendamento=agendamento)


@app.route("/agendamentos/<int:id>/editar", methods=["GET", "POST"])
@login_required
def agendamentos_editar(id):
    connection = get_db_connection()
    agendamento = connection.execute(
        "SELECT * FROM agendamentos WHERE id = ? AND usuario_id = ?",
        (id, session["usuario_id"]),
    ).fetchone()

    if agendamento is None:
        connection.close()
        flash("Agendamento nao encontrado.")
        return redirect(url_for("agendamentos_listar"))

    if request.method == "POST":
        dados = {
            "nome_pet": request.form.get("nome_pet", "").strip(),
            "nascimento": request.form.get("nascimento", "").strip(),
            "tutor": request.form.get("tutor", "").strip(),
            "email": request.form.get("email", "").strip(),
            "contato": request.form.get("contato", "").strip(),
            "endereco": request.form.get("endereco", "").strip(),
            "bairro": request.form.get("bairro", "").strip(),
            "servico": request.form.get("servico", "").strip(),
            "id": id,
        }

        if any(not valor for chave, valor in dados.items() if chave != "id"):
            connection.close()
            flash("Preencha todos os campos do agendamento.")
            return render_template("cadastro.html", agendamento=dados, modo_edicao=True)

        connection.execute(
            """
            UPDATE agendamentos
            SET nome_pet = ?, nascimento = ?, tutor = ?, email = ?,
                contato = ?, endereco = ?, bairro = ?, servico = ?
            WHERE id = ? AND usuario_id = ?
            """,
            (
                dados["nome_pet"],
                dados["nascimento"],
                dados["tutor"],
                dados["email"],
                dados["contato"],
                dados["endereco"],
                dados["bairro"],
                dados["servico"],
                id,
                session["usuario_id"],
            ),
        )
        connection.commit()
        connection.close()
        flash("Agendamento atualizado com sucesso.")
        return redirect(url_for("agendamentos_listar"))

    connection.close()
    return render_template("cadastro.html", agendamento=agendamento, modo_edicao=True)


@app.route("/agendamentos/<int:id>/excluir", methods=["POST"])
@login_required
def agendamentos_excluir(id):
    connection = get_db_connection()
    connection.execute(
        "DELETE FROM agendamentos WHERE id = ? AND usuario_id = ?",
        (id, session["usuario_id"]),
    )
    connection.commit()
    connection.close()
    flash("Agendamento removido com sucesso.")
    return redirect(url_for("agendamentos_listar"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
