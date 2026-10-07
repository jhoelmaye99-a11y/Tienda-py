from flask import Flask, redirect, render_template, request, url_for
import pymysql
import pymysql.cursors


app = Flask(__name__)
def connect_to_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='tiendaejemplo',
        cursorclass=pymysql.cursors.DictCursor,
        
    )
    

@app.route('/')
def inicio():
    return render_template('index.html')



# -----Login de administrador-----}

@app.route(
'/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        #inicio de sesión del administrador
        username = request.form['username']
        password = request.form['password']
        # Validar las credenciales del administrador
        if username == 'jhoelmaye9.9@gmail.com' and password == 'admin123':
            return redirect(url_for('dashboard_admin'))
        else:
            return "Credenciales inválidas"
    return render_template('login_admin.html')


@app.route('/dashboard_admin')  
def dashboard_admin():
    return render_template('dashboard_admin.html')



#-----Gestión de productos-----

@app.route('/gestion_productos', methods=['GET', 'POST'])
def gestion_productos():
    if request.method == "POST": 
        nombre = request.form["nombre"] 
        precio = request.form["precio"] 
        stock = request.form["stock"] 
        try: 
            conn = connect_to_db() 
            cur = conn.cursor()  
            cur.execute("INSERT INTO producto (nombre, precio, stock) VALUES (%s, %s, %s)", 
                            (nombre, precio, stock)) 
            conn.commit() 
            cur.close()
            conn.close() 
            return redirect(url_for('gestion_productos')) 
        except Exception: 
            return redirect(url_for('gestion_productos'))

    return render_template('gestion_productos.html')



#-----Gestión de pedidos-----

@app.route('/gestion_pedidos', methods=['GET', 'POST'])
def gestion_pedidos():
    if request.method == "POST": 
        id_cliente = request.form["id_cliente"] 
        id_producto = request.form["id_producto"] 
        cantidad = request.form["cantidad"] 
        fecha_pedido = request.form["fecha_pedido"]
        try: 
            conn = connect_to_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO pedido (id_cliente, id_producto, cantidad, fecha_pedido) VALUES (%s, %s, %s, %s)", 
                            (id_cliente, id_producto, cantidad, fecha_pedido)) 
            conn.commit() 
            cur.close() 
            conn.close() 
            return redirect(url_for('gestion_pedidos')) 
        except Exception: 
            return redirect(url_for('gestion_pedidos'))

    return render_template('gestion_pedidos.html')



#-----Gestión de clientes-----

@app.route('/gestion_clientes', methods=['GET', 'POST'])
def gestion_clientes():
    if request.method == "POST": 
        nombre = request.form["nombre"] 
        correo = request.form["correo"]
        apellido = request.form["apellido"]
        telefono = request.form["telefono"] 
        try: 
            conn = connect_to_db() 
            cur = conn.cursor()  
            cur.execute("INSERT INTO usuarios (nombre, apellido, correo, telefono) VALUES (%s, %s, %s, %s)", 
                            (nombre, apellido, correo, telefono)) 
            conn.commit() 
            cur.close()
            conn.close() 
            return redirect(url_for('gestion_clientes')) 
        except Exception as e:
            return f"Error al insertar: {e}"

    return render_template('gestion_clientes.html')

if __name__ == '__main__':
    app.run(debug=True)