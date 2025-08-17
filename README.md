# Transformación de Aplicación CLI a Aplicación Web con Flask

Este proyecto transforma la aplicación de gestión de biblioteca personal de una herramienta de línea de comandos a una **aplicación web interactiva** utilizando el microframework **Flask** para el backend y **KeyDB** (compatible con Redis) como base de datos en memoria para el almacenamiento de datos.

## Características Principales

* **Interfaz Web Intuitiva**: Permite gestionar libros a través de formularios y tablas HTML.
* **Funcionalidades CRUD Completas**:
    * **Agregar Nuevo Libro**: Formulario dedicado para añadir títulos, autores, géneros y el estado de lectura.
    * **Listar Libros**: Visualización clara y organizada de todos los libros en una tabla.
    * **Buscar Libros**: Funcionalidad de búsqueda por título, autor o género.
    * **Actualizar Información**: Formulario de edición pre-rellenado para modificar datos de libros existentes.
    * **Eliminar Libro**: Opción sencilla para remover libros de la base de datos.
* **Almacenamiento en Memoria**: Utiliza KeyDB con `redis-py` para operaciones de alta velocidad.
* **Serialización JSON**: Los datos de los libros se almacenan en KeyDB como objetos JSON serializados.
* **Mensajes de Alerta**: Notificaciones visuales para el usuario sobre el éxito o fracaso de las operaciones.
* **Diseño Responsivo Básico**: Implementación de Bootstrap 5 para una presentación moderna.

## Requisitos del Sistema

* **Python 3.x**
* **KeyDB Server** (o Redis Server compatible): Un servidor de KeyDB/Redis debe estar ejecutándose para que la aplicación funcione.
* **Dependencias de Python**: Las librerías necesarias están listadas en `requirements.txt`.

## Instalación y Configuración de KeyDB (Local)

Para ejecutar esta aplicación, necesitas tener un servidor KeyDB (o Redis) en funcionamiento.

1.  **Descarga KeyDB Server**:
    * Visita la página de [releases de KeyDB en GitHub](https://github.com/EQ-Alpha/KeyDB/releases).
    * Descarga el archivo `.zip` para tu sistema operativo (ej., `KeyDB_Windows_x64.zip` para Windows).
2.  **Descomprime**:
    * Extrae el contenido del archivo ZIP en una carpeta de fácil acceso, por ejemplo, `C:\KeyDB`.
3.  **Ejecuta el Servidor**:
    * Abre una terminal (CMD o PowerShell).
    * Navega a la carpeta donde descomprimiste KeyDB (ej., `cd C:\KeyDB`).
    * Inicia el servidor ejecutando:
        ```bash
        keydb.exe keydb.conf
        ```
        Deja esta ventana de terminal abierta mientras la aplicación Flask esté en uso. KeyDB escuchará por defecto en el puerto `6379`.

## Configuración del Proyecto Python

1.  **Clona el Repositorio** (o descarga los archivos del proyecto `tar6`).
2.  **Abre la Carpeta `tar6` en Visual Studio Code.**
3.  **Crea y Activa un Entorno Virtual**:
    ```bash
    python -m venv venv
    # Para Windows PowerShell:
    .\venv\Scripts\Activate
    # Para Windows CMD:
    # venv\Scripts\activate
    ```
4.  **Instala las Dependencias de Python**:
    ```bash
    pip install -r requirements.txt
    ```
    Esto instalará Flask, `redis-py`, `python-dotenv`, y otras dependencias necesarias.

5.  **Configura el Archivo `.env`**:
    * En la raíz de la carpeta `tar6`, crea un archivo llamado `.env` (con el punto inicial).
    * Añade el siguiente contenido, **ajustando si es necesario** los valores de host, puerto y contraseña para tu configuración de KeyDB:
        ```env
        FLASK_APP=app.py
        FLASK_ENV=development
        SECRET_KEY=Una_clave_secreta_fuerte_aqui_para_Flask
        KEYDB_HOST=localhost
        KEYDB_PORT=6379
        # Si KeyDB tiene una contraseña configurada, descomenta y usa:
        # KEYDB_PASSWORD=tu_contraseña_de_keydb
        ```
        **Importante**: La `SECRET_KEY` es fundamental para la seguridad de Flask (sesiones, mensajes `flash`). **¡Usa una cadena de caracteres aleatoria y compleja en un entorno real!**

## Cómo Ejecutar la Aplicación Web

1.  **Asegúrate de que tu servidor KeyDB esté funcionando** en su propia ventana de terminal.
2.  **Abre una nueva terminal** en VS Code y navega a la **raíz de la carpeta `tar6`**.
3.  **Activa tu entorno virtual** (`(venv)`) si aún no lo está.
4.  **Inicia la aplicación Flask**:
    ```bash
    flask run
    ```
5.  Abre tu navegador web y navega a la URL que aparecerá en la terminal (típicamente `http://127.0.0.1:5000/`).

## Estructura de Datos de los Libros en KeyDB

Cada libro se almacena como un par clave-valor en KeyDB:
* **Clave**: `libro:<ID_único_UUID>` (ejemplo: `libro:a1b2c3d4-e5f6-7890-1234-567890abcdef`).
* **Valor**: Un objeto JSON serializado que representa el libro, incluyendo su `id` único.

**Ejemplo de un documento JSON de libro:**

```json
{
    "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "titulo": "Don Quijote de la Mancha",
    "autor": "Miguel de Cervantes",
    "genero": "Novela de caballerías",
    "leido": true
}