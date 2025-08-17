from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_redis_client, close_db_connection
import json
import uuid
import os
from redis.exceptions import RedisError

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super_secret_key_default") # Usa la clave del .env

# Prefijo para las claves de los libros en KeyDB
BOOK_KEY_PREFIX = "libro:"

# --- Funciones de Lógica de Negocio (CRUD) adaptadas para Flask ---

def _add_book_to_db(titulo: str, autor: str, genero: str = None, leido: bool = False):
    """Agrega un nuevo libro a KeyDB."""
    r = get_redis_client()
    if r is None:
        return None # Error de conexión

    book_id = str(uuid.uuid4())
    key = f"{BOOK_KEY_PREFIX}{book_id}"

    book_data = {
        "id": book_id,
        "titulo": titulo,
        "autor": autor,
        "genero": genero,
        "leido": leido
    }

    try:
        r.set(key, json.dumps(book_data))
        return book_data # Devuelve los datos del libro agregado
    except RedisError as e:
        flash(f"Error al agregar libro: {e}", "danger")
        return None

def _get_all_books_from_db():
    """Obtiene todos los libros de KeyDB."""
    r = get_redis_client()
    if r is None:
        return []

    books = []
    try:
        for key in r.scan_iter(f"{BOOK_KEY_PREFIX}*"):
            book_json = r.get(key)
            if book_json:
                try:
                    books.append(json.loads(book_json))
                except json.JSONDecodeError:
                    flash(f"Advertencia: No se pudo decodificar el JSON para la clave {key}.", "warning")
                    continue
        # Opcional: ordenar los libros para la visualización
        books.sort(key=lambda x: x.get('titulo', '').lower())
        return books
    except RedisError as e:
        flash(f"Error al obtener libros: {e}", "danger")
        return []

def _get_book_by_id_from_db(book_id: str):
    """Obtiene un libro específico por su ID."""
    r = get_redis_client()
    if r is None:
        return None

    key = f"{BOOK_KEY_PREFIX}{book_id}"
    try:
        book_json = r.get(key)
        if book_json:
            return json.loads(book_json)
        return None
    except RedisError as e:
        flash(f"Error al obtener libro por ID: {e}", "danger")
        return None
    except json.JSONDecodeError as e:
        flash(f"Error al decodificar JSON para el libro {book_id}: {e}", "danger")
        return None

def _update_book_in_db(book_id: str, updates: dict):
    """Actualiza un libro existente en KeyDB."""
    r = get_redis_client()
    if r is None:
        return False

    key = f"{BOOK_KEY_PREFIX}{book_id}"
    try:
        book_json = r.get(key)
        if not book_json:
            flash(f"No se encontró el libro con ID {book_id}.", "warning")
            return False

        book_data = json.loads(book_json)
        updated = False
        for field, value in updates.items():
            if book_data.get(field) != value: # Solo actualiza si el valor es diferente
                book_data[field] = value
                updated = True

        if updated:
            r.set(key, json.dumps(book_data))
            return True
        return False # No hubo cambios
    except RedisError as e:
        flash(f"Error al actualizar libro: {e}", "danger")
        return False
    except json.JSONDecodeError as e:
        flash(f"Error al decodificar JSON para actualizar libro {book_id}: {e}", "danger")
        return False


def _delete_book_from_db(book_id: str):
    """Elimina un libro de KeyDB."""
    r = get_redis_client()
    if r is None:
        return False

    key = f"{BOOK_KEY_PREFIX}{book_id}"
    try:
        result = r.delete(key)
        return result > 0 # True si se eliminó, False si no existía
    except RedisError as e:
        flash(f"Error al eliminar libro: {e}", "danger")
        return False

# --- Rutas de la Aplicación Flask ---

@app.route('/', methods=['GET', 'POST'])
def index():
    """Ruta principal para listar y buscar libros."""
    search_query = request.args.get('search', '').strip()
    books = _get_all_books_from_db()

    if search_query:
        filtered_books = []
        query_lower = search_query.lower()
        for book in books:
            if (query_lower in book.get('titulo', '').lower() or
                query_lower in book.get('autor', '').lower() or
                (book.get('genero') and query_lower in book['genero'].lower())):
                filtered_books.append(book)
        books = filtered_books
        if not books:
            flash(f"No se encontraron libros que coincidan con '{search_query}'.", "info")

    return render_template('index.html', books=books, search_query=search_query)

@app.route('/add', methods=['GET', 'POST'])
def add_book_route():
    """Ruta para agregar un nuevo libro."""
    if request.method == 'POST':
        titulo = request.form['titulo'].strip()
        autor = request.form['autor'].strip()
        genero = request.form.get('genero', '').strip()
        leido = request.form.get('leido') == 'on' # Checkbox envía 'on' si está marcado

        if not titulo or not autor:
            flash('El título y el autor son obligatorios.', 'danger')
        else:
            book = _add_book_to_db(titulo, autor, genero if genero else None, leido)
            if book:
                flash(f'Libro "{titulo}" agregado exitosamente!', 'success')
                return redirect(url_for('index')) # Redirige a la página principal
    return render_template('add_book.html')

@app.route('/edit/<book_id>', methods=['GET', 'POST'])
def edit_book_route(book_id):
    """Ruta para editar un libro existente."""
    book = _get_book_by_id_from_db(book_id)
    if not book:
        flash('Libro no encontrado.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        updates = {}
        new_titulo = request.form['titulo'].strip()
        new_autor = request.form['autor'].strip()
        new_genero = request.form.get('genero', '').strip()
        new_leido = request.form.get('leido') == 'on'

        # Validar y preparar actualizaciones
        if new_titulo: updates['titulo'] = new_titulo
        if new_autor: updates['autor'] = new_autor
        updates['genero'] = new_genero if new_genero else None # Permitir vaciar género
        updates['leido'] = new_leido

        if not new_titulo or not new_autor:
            flash('El título y el autor son obligatorios.', 'danger')
            # Renderizar la plantilla con los datos actuales para que el usuario pueda corregir
            return render_template('edit_book.html', book=book)

        if _update_book_in_db(book_id, updates):
            flash(f'Libro "{new_titulo}" actualizado exitosamente!', 'success')
            return redirect(url_for('index'))
        else:
            flash('No se realizaron cambios o hubo un error al actualizar.', 'info')
            return redirect(url_for('index')) # O redirigir a la misma página de edición

    return render_template('edit_book.html', book=book)

@app.route('/delete/<book_id>', methods=['POST'])
def delete_book_route(book_id):
    """Ruta para eliminar un libro."""
    book = _get_book_by_id_from_db(book_id)
    if not book:
        flash('Libro no encontrado para eliminar.', 'danger')
    else:
        if _delete_book_from_db(book_id):
            flash(f'Libro "{book.get("titulo", "Desconocido")}" eliminado exitosamente!', 'success')
        else:
            flash(f'Error al eliminar libro "{book.get("titulo", "Desconocido")}".', 'danger')
    return redirect(url_for('index'))

# Manejo de errores de conexión global al iniciar la aplicación
@app.before_request
def check_db_connection():
    if get_redis_client() is None and request.endpoint != 'static':
        # Solo si no es una solicitud de archivo estático
        flash("No se pudo establecer conexión con KeyDB. La aplicación podría no funcionar correctamente.", "danger")


# Cierra la conexión de KeyDB cuando la aplicación Flask se apaga
@app.teardown_appcontext
def teardown_db(exception):
    close_db_connection()

if __name__ == '__main__':
    app.run(debug=True) # debug=True para desarrollo (recarga automática, mensajes de error detallados)