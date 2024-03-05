# libsiae

Biblioteca en Python para acceder de forma fácil al [Sistema Integral de Administración Escolar](https://www.dgae-siae.unam.mx/www_gate.php) de la Universidad Nacional Autónoma de México.

Este es un proyecto en desarrollo, y aún hay varias características de la plataforma que no están disponibles en esta biblioteca. Por ahora, los siguientes apartados están disponibles:

* Etapas de trayectoria
* Historiales académicos
* Inscripciones
## Instalación

Esta biblioteca contiene un solo archivo (`src/libreunam/siae.py`), puedes copiarlo directamente en tu proyecto.

También puedes descargar los [paquetes por lanzamiento](https://gitlab.com/libre-unam/libsiae/-/releases).

Para ejecutar, se requiere de las bibliotecas `requests` y `beautifulsoup4`.
## Uso

```python
from libreunam.siae import SIAE
obj = SIAE()

# Obtén el captcha para resolverlo
with open('captcha.png', 'wb') as f:
    f.write(obj.captcha.read())

# Inicia sesión
obj.login(usuario, contraseña, respuesta_captcha)

# ¡Usa la biblioteca!
hist = obj.trayectoria[0].inscripcion[1] # Mi última inscripción
```

Si querías implementar un sistema de inicio de sesión basado en cuentas del SIAE, tal vez te interese [este módulo de autentificación para Django](https://gitlab.com/libre-unam/django-auth-libreunam-siae).
## Ayuda
Me gustaría poder seguir dedicando tiempo para realizar más herramientas libres. Si lo consideras pertinente, puedes [invitarme un té 🍵](https://paypal.me/twilight1794). También puedes ayudarme a mantener estas utilidades, puedes contactarme si te interesa. ¡Muchas gracias!


## Licencia

*  [GPLv3+](https://www.gnu.org/licenses/gpl-3.0.html)
* _[¿Por qué las escuelas deben promover el uso de software libre?](https://www.gnu.org/education/edu-schools.es.html)_
