from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, template_folder='Templates')

# página inicial
@app.route('/')
def index():
    return render_template('index.html')

# segunda página inicial
@app.route('/inicial') 
def inicial():
    return render_template('inicial.html')

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('inicial'))
    return render_template('login.html')

# logout (melhorar com o javascript)
@app.route('/logout')
def logout():
    return render_template('inicial.html')

# cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        return redirect(url_for('servicos'))
    return render_template('cadastro.html')

# serviços
@app.route('/servicos')
def servicos():    
    return render_template('servicos.html')

# página de banho
@app.route('/banho')
def banho():
    return render_template('banho.html')

# página de vacinas
@app.route('/vacinas')
def vacinas():
    return render_template('vacinas.html')

# página de ficha
@app.route('/ficha')
def ficha():
    return render_template('ficha.html')        

if __name__ == '__main__':
    app.run(debug=True)
