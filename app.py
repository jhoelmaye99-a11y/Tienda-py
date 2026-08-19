from flask import Flask, render_template, request
app = Flask(__name__)
@app.route('/')
def inicio():
    return render_template('index.html')


@app.route(
'/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        # Aquí puedes manejar la lógica de inicio de sesión del administrador
        username = request.form['username']
        password = request.form['password']
        # Validar las credenciales del administrador
        if username == 'jhoelmaye9.9@gmail.com' and password == 'admin123':
            return render_template('dashboard_admin.html')
        else:
            return "Credenciales inválidas"
    return render_template('login_admin.html')


@app.route('/dashboard_admin')  
def dashboard_admin():
    return render_template('dashboard_admin.html')


if __name__ == '__main__':
    app.run(debug=True)