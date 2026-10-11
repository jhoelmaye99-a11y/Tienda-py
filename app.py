
from flask import Flask, redirect, render_template, request, url_for, flash
import pymysql
import pymysql.cursors


app = Flask(__name__)
app.secret_key = 'elite_pro_sports_clave'
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
        accion = request.form.get("accion")
        conn = None
        cur = None
        try:
            conn = connect_to_db()
            cur = conn.cursor()

            # ------REGISTRAR PRODUCTO------
            if accion == "registrar":
                nombre = request.form["nombre"]
                precio = request.form["precio"]
                stock = request.form["stock"]
                cur.execute("""
                    INSERT INTO producto (nombre, precio, stock)
                    VALUES (%s, %s, %s)
                """, (nombre, precio, stock))
                conn.commit()

            # ------ACTUALIZAR PRODUCTO------
            elif accion == "actualizar":
                id_producto = request.form["id_producto"]
                nombre = request.form["nombre"]
                precio = request.form["precio"]
                stock = request.form["stock"]
                cur.execute("""
                    UPDATE producto
                    SET nombre = %s,
                        precio = %s,
                        stock = %s
                    WHERE id_producto = %s
                """, (nombre, precio, stock, id_producto))
                conn.commit()

            # ------ ELIMINAR PRODUCTO ------
            elif accion == "eliminar":
                id_producto = request.form["id_producto"]
                try:
                    cur.execute("""
                        DELETE FROM producto
                        WHERE id_producto = %s
                    """, (id_producto,))
                    conn.commit()
                    flash("Producto eliminado correctamente.", 'confirmado')
                except pymysql.err.IntegrityError as e:
                    conn.rollback()

                    if e.args[0] == 1451:
                        flash(
                            "No se puede eliminar este producto porque ya está registrado en uno o varios pedidos.",
                            'error'
                        )
                    else:
                        raise

        except Exception:
            if conn is not None:
                conn.rollback()
            raise
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

        return redirect(url_for('gestion_productos'))

    # ------CONSULTAR PRODUCTOS------
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM producto")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('gestion_productos.html', data=data)



# ----- Gestión de pedidos -----
@app.route('/gestion_pedidos', methods=['GET', 'POST'])
def gestion_pedidos():
    if request.method == "POST":
        accion = request.form.get("accion", "registrar")
        conn = None
        cur = None
        try:
            conn = connect_to_db()
            cur = conn.cursor()
            if accion == "registrar":
                id_cliente = request.form["id_cliente"]
                id_producto = request.form["id_producto"]
                cantidad = request.form["cantidad"]
                fecha_pedido = request.form["fecha_pedido"]
                cur.execute("""
                    INSERT INTO pedido
                        (id_cliente, id_producto, cantidad, fecha_pedido)
                    VALUES (%s, %s, %s, %s)
                """, (id_cliente, id_producto, cantidad, fecha_pedido))
                conn.commit()
                flash("Pedido registrado correctamente.", "success")
            elif accion == "actualizar":
                id_pedido = request.form["id_pedido"]
                id_cliente = request.form["id_cliente"]
                id_producto = request.form["id_producto"]
                cantidad = request.form["cantidad"]
                fecha_pedido = request.form["fecha_pedido"]
                cur.execute("""
                    UPDATE pedido
                    SET id_cliente = %s,
                        id_producto = %s,
                        cantidad = %s,
                        fecha_pedido = %s
                    WHERE id_pedido = %s
                """, (
                    id_cliente, id_producto, cantidad,
                    fecha_pedido, id_pedido
                ))
                conn.commit()
                flash("Pedido actualizado correctamente.", "success")
            elif accion == "eliminar":
                id_pedido = request.form["id_pedido"]
                cur.execute("""
                    DELETE FROM pedido
                    WHERE id_pedido = %s
                """, (id_pedido,))
                if cur.rowcount > 0:
                    conn.commit()
                    flash("Pedido eliminado correctamente.", "success")
                else:
                    conn.rollback()
                    flash("No se encontró el pedido que intentas eliminar.", "error")
            else:
                flash("La acción solicitada no es válida.", "error")
        except pymysql.err.IntegrityError as e:
            if conn is not None:
                conn.rollback()
            if e.args[0] == 1452:
                flash(
                    "No se pudo guardar el pedido: el cliente o el producto "
                    "indicado no existe. Verifica los ID.",
                    "error"
                )
            elif e.args[0] == 1451:
                flash(
                    "No se puede eliminar este pedido porque está relacionado "
                    "con otros registros.",
                    "error"
                )
            else:
                print("Error de integridad:", e)
                flash("No se pudo completar la operación por una restricción de la base de datos.", "error")
        except Exception as e:
            if conn is not None:
                conn.rollback()
            print("Error al gestionar el pedido:", e)
            flash("Ocurrió un error al procesar el pedido.", "error")
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
        return redirect(url_for('gestion_pedidos'))

    # ------ CONSULTAR PEDIDOS ------
    conn = connect_to_db()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                p.id_pedido,
                p.id_cliente,
                p.id_producto,
                u.nombre AS nombre_cliente,
                u.apellido AS apellido_cliente,
                pr.nombre AS nombre_producto,
                p.cantidad,
                p.fecha_pedido
            FROM pedido AS p
            LEFT JOIN usuarios AS u
                ON p.id_cliente = u.id_cliente
            LEFT JOIN producto AS pr
                ON p.id_producto = pr.id_producto
            ORDER BY p.id_pedido DESC
        """)

        data = cur.fetchall()
        print("PEDIDOS ENVIADOS A LA PLANTILLA:", data)

    finally:
        cur.close()
        conn.close()

    return render_template('gestion_pedidos.html', data=data)


# ----- Gestión de clientes -----
@app.route('/gestion_clientes', methods=['GET', 'POST'])
def gestion_clientes():
    if request.method == "POST":
        accion = request.form.get("accion", "registrar")
        conn = None
        cur = None
        try:
            conn = connect_to_db()
            cur = conn.cursor()
            # ------ REGISTRAR CLIENTE ------
            if accion == "registrar":
                nombre = request.form["nombre"].strip()
                apellido = request.form["apellido"].strip()
                correo = request.form["correo"].strip()
                telefono = request.form.get("telefono", "").strip()
                cur.execute("""
                    INSERT INTO usuarios
                        (nombre, apellido, correo, telefono)
                    VALUES (%s, %s, %s, %s)
                """, (nombre, apellido, correo, telefono))
                conn.commit()
                flash("Cliente registrado correctamente.", "success")
            # ------ ACTUALIZAR CLIENTE ------
            elif accion == "actualizar":
                id_cliente = request.form["id_cliente"]
                nombre = request.form["nombre"].strip()
                apellido = request.form["apellido"].strip()
                correo = request.form["correo"].strip()
                telefono = request.form.get("telefono", "").strip()
                cur.execute("""
                    UPDATE usuarios
                    SET nombre = %s,
                        apellido = %s,
                        correo = %s,
                        telefono = %s
                    WHERE id_cliente = %s
                """, (
                    nombre, apellido, correo, telefono, id_cliente
                ))

                conn.commit()
                if cur.rowcount > 0:
                    flash("Cliente actualizado correctamente.", "success")
                else:
                    flash(
                        "No se realizaron cambios o no se encontró el cliente.",
                        "error"
                    )
            # ------ ELIMINAR CLIENTE ------
            elif accion == "eliminar":
                id_cliente = request.form["id_cliente"]
                cur.execute("""
                    DELETE FROM usuarios
                    WHERE id_cliente = %s
                """, (id_cliente,))
                if cur.rowcount > 0:
                    conn.commit()
                    flash("Cliente eliminado correctamente.", "success")
                else:
                    conn.rollback()
                    flash("No se encontró el cliente que deseas eliminar.", "error")
            else:
                flash("La acción solicitada no es válida.", "error")
        except pymysql.err.IntegrityError as e:
            if conn is not None:
                conn.rollback()
            if e.args[0] == 1451:
                flash(
                    "No se puede eliminar este cliente porque tiene pedidos "
                    "registrados. Conserva el cliente para mantener el historial.",
                    "error"
                )
            elif e.args[0] == 1062:
                flash(
                    "No se pudo guardar el cliente porque uno de sus datos "
                    "ya está registrado.",
                    "error"
                )
            else:
                print("Error de integridad del cliente:", e)
                flash(
                    "No se pudo completar la operación por una restricción "
                    "de la base de datos.",
                    "error"
                )
        except Exception as e:
            if conn is not None:
                conn.rollback()
            print("Error al gestionar el cliente:", e)
            flash("Ocurrió un error al procesar el cliente.", "error")
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
        return redirect(url_for('gestion_clientes'))
    # ------ CONSULTAR CLIENTES ------
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_cliente, nombre, apellido, correo, telefono
            FROM usuarios
            ORDER BY id_cliente DESC
        """)
        data = cur.fetchall()
    finally:
        cur.close()
        conn.close()
    return render_template('gestion_clientes.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)