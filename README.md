# SOCIEDAD ECONOMICA DE AMIGOS DEL PAIS DE LA HABANA: ARCHIVO

## Descripción
Este proyecto tiene el objetivo de ayudar en la digitilazación de los documentos del Archivo de la Sociedad Económica de Amigos del País de la Habana.
Mediante la plataforma web se podrá acceder a los documentos digitalizados y realizar búsquedas en los mismos.
Así mismo, se ofrece una herramienta para la transcripción automática de los documentos, con el fin de facilitar el proceso de digitalización.

## Estructura del proyecto
El proyecto está dividido en dos partes:
1. **Frontend**: Aplicación web que permite visualizar los documentos digitalizados y realizar búsquedas en los mismos.
2. **Backend**: Servidor que se encarga de servir los documentos digitalizados y realizar la transcripción automática de los mismos.

## Tecnologías utilizadas
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Django
- **Base de datos**: SQLite
- **Herramientas de transcripción**: tensorflow, keras
- **Herramientas de segmentación de líneas**: OpenCV
- **Herramientas de generación de XML-TEI**: ElementTree

## Instalación
Para instalar el proyecto, se deben seguir los siguientes pasos:
1. Clonar el repositorio:
```bash
git clone 
```
2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```
3. Crear la base de datos:
```bash
python manage.py migrate
```
4. Correr el servidor:
```bash
python manage.py runserver
```
5. Acceder a la aplicación web en la dirección `http://localhost:8000`
6. Si es la primera vez q se ejecuta la bd, se deben crear los usuarios y roles:
```bash
python manage.py createsuperuser
```
7. Para crear los roles, se debe acceder a la dirección `http://localhost:8000/admin` y loguearse con el usuario creado en el paso anterior.
8. Crear 3 grupos: 'ADMIN', 'EDITOR', 'REVISOR'. Asignar los permisos correspondientes a cada grupo.
9. En admin también se debe crear una instancia de 'Profile' para el usuario administrador creado en el paso 6.


## Contraseñas de roles
Ver en archivo `secrets.json`

