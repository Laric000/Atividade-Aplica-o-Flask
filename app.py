from flask import Flask, render_template, request

app = Flask(__name__)

#rota da pag inicial
@app.route('/')
def index():
    return render_template('index.html') #carrega a pag incial (index.html)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    return render_template('login.html')

#rota da pag de cadastro
@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html') #carrega o formulario de cadastro

#rota para receber os dados do formulario (com POST)
@app.route('/dados', methods=['POST'])
def resultado():
    #dados enviados pelo formulario
    nome_pet = request.form.get('nome_pet')
    nascimento = request.form.get('nascimento')
    tutor = request.form.get('tutor')
    contato = request.form.get('contato')
    endereco = request.form.get('endereco')
    bairro = request.form.get('bairro')

    #envia os dados para pag com os dados (dados.html)
    return render_template('dados.html',
    nome_pet=nome_pet,
    nascimento=nascimento,
    tutor=tutor,
    email=email,
    contato=contato,
    endereco=endereco,
    bairro=bairro)

if __name__ == '__main__':
    app.run(debug=True)