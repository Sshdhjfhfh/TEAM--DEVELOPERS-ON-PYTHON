# Sistema de Gestión de Tópico UNH

## Sprint Goal del Sprint 0
Al finalizar el Sprint 0, el equipo tiene el entorno Python/Django configurado,
el repositorio GitHub con Git Flow activo (ramas main y develop), el Product
Backlog con las User Stories priorizadas en GitHub Projects y los wireframes
de las pantallas principales del Tópico esbozados — listo para iniciar el
desarrollo en el Sprint 1.

## Equipo — TEAM – DEVELOPERS ON PYTHON
| Rol           | Integrante                    | GitHub        |
|---------------|-------------------------------|---------------|
| Scrum Master  | Huaman Prejo, Saul            | @Sshdhjfhfh   |
| Backend Dev   | Aguilar Rivera, Elvis Antoni  | @usuario      |
| Product Owner | [Integrante 3]                | @usuario      |
| Frontend Dev  | [Integrante 4]                | @usuario      |
| QA / DevOps   | [Integrante 5]                | @usuario      |

## Stack Tecnológico
- Python 3.12+ | Django 5.x | DRF 3.15+
- Django Templates + Bootstrap 5 + JavaScript | SQLite (dev) | PostgreSQL (prod)

## Cómo ejecutar el proyecto localmente
```bash
git clone https://github.com/Sshdhjfhfh/TEAM--DEVELOPERS-ON-PYTHON.git
cd TEAM--DEVELOPERS-ON-PYTHON
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Navegar a http://127.0.0.1:8000/