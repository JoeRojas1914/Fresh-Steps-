# Fresh Steps — Sistema de Gestión

<!-- Logo -->
<p align="center">
  <img src="static/images/FreshStepsLogo.png" alt="Fresh Steps" height="80" style="margin-right:20px;">
  &nbsp;&nbsp;&nbsp;
  <img src="static/images/FersShopLogo.png" alt="Confección" height="80">
</p>

---

Sistema web interno para la gestión de ventas, clientes, servicios y usuarios de **Fresh Steps**, **Confección** y **Maquila**. Permite registrar recibos, dar seguimiento a entregas, administrar gastos y consultar estadísticas por negocio.

---

## Módulos

| Módulo | Descripción |
|---|---|
| **Ventas** | Crear, consultar y eliminar recibos. Flujo: Pendiente → Lista → Entregada |
| **Clientes** | Registro y perfil de clientes con historial de ventas |
| **Servicios** | Catálogo de servicios por negocio con precios base |
| **Usuarios** | Gestión de cajeros y administradores con PIN de acceso |
| **Gastos** | Registro de gastos operativos por negocio |
| **Estadísticas** | Gráficas de ingresos, ventas y servicios más solicitados |
| **Historial** | Auditoría de acciones sobre cada venta (CREADO, LISTA, ENTREGADO, ELIMINADO) |

---

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12 + Flask |
| Base de datos | MySQL 8+ |
| Frontend | Jinja2 + CSS modular + JavaScript vanilla |
| Gráficas | Chart.js |
| Autenticación | Sesiones Flask + PIN numérico |
| Seguridad | Flask-WTF (CSRF) + Flask-Talisman + bcrypt |

---

## Requisitos

- Python 3.12
- MySQL 8+
- Las dependencias listadas en `requirements.txt`

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd fresh-steps

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp scripts/.env.example .env
# Editar .env con los valores reales

# 5. Crear las tablas en MySQL
mysql -u usuario -p freshstepsproduccion < migrations/001_schema_completo.sql

# 6. Correr la aplicación
python app.py
```

---

## Variables de entorno

Crear un archivo `.env` en la raíz:

```env
DB_HOST=localhost
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=freshstepsproduccion
SECRET_KEY=clave-secreta-flask
WTF_CSRF_SECRET_KEY=clave-secreta-csrf
```

---

## Estructura del proyecto

```
fresh-steps/
├── app.py                  # Punto de entrada y registro de blueprints
├── db.py                   # Pool de conexiones MySQL
├── config.py               # Constantes de configuración
├── extensions.py           # Extensiones Flask (rate limiter)
│
├── routes/                 # Blueprints de Flask (solo HTTP, sin lógica)
│   ├── auth_routes.py
│   ├── ventas_routes.py
│   ├── clientes_routes.py
│   ├── servicios_routes.py
│   ├── usuarios_routes.py
│   ├── estadisticas_routes.py
│   └── gastos_routes.py
│
├── services/               # Lógica de negocio
│   ├── ventas_service.py
│   ├── clientes_service.py
│   ├── usuarios_service.py
│   ├── servicios_service.py
│   ├── estadisticas_service.py
│   ├── gastos_service.py
│   └── auth_service.py
│
├── models/                 # Acceso a datos (queries SQL)
│   ├── ventas.py           # Re-exports de ventas_*
│   ├── ventas_crear.py
│   ├── ventas_detalles.py
│   ├── ventas_historial.py
│   ├── estadisticas.py     # Re-exports de estadisticas_*
│   ├── estadisticas_ventas.py
│   ├── estadisticas_clientes.py
│   ├── estadisticas_gastos.py
│   ├── clientes.py
│   ├── servicios.py
│   ├── usuarios.py
│   ├── gastos.py
│   ├── negocio.py
│   └── pagos.py
│
├── middleware/
│   └── auth_middleware.py  # Protección de rutas y timeout de sesión
│
├── migrations/
│   └── 001_schema_completo.sql  # Esquema completo: tablas, datos e índices
│
├── templates/              # Jinja2
│   ├── base.html
│   ├── components/
│   ├── macros/
│   └── pages/
│
├── static/
│   ├── css/
│   │   ├── main.css        # Import de todos los módulos
│   │   ├── base/           # Variables, reset, navbar, footer
│   │   ├── components/     # Botones, badges, modales, formularios
│   │   └── pages/          # CSS específico por página
│   ├── js/
│   │   ├── base/           # CSRF, navbar, inicialización de Lucide
│   │   └── pages/          # JS específico por página
│   └── images/
│
└── requirements.txt
```

---

## Base de datos

<!-- Diagrama ER -->
<p align="center">
  <img src="static/images/Diagrama BD.png" alt="Diagrama de base de datos" width="800">
</p>

### Tablas principales

| Tabla | Descripción |
|---|---|
| `usuario` | Cajeros y administradores con PIN hasheado |
| `cliente` | Clientes registrados |
| `negocio` | Negocios: Fresh Steps, Confección, Maquila |
| `servicio` | Catálogo de servicios por negocio |
| `venta` | Recibos de venta |
| `articulo` | Artículos dentro de cada venta |
| `articulo_calzado` | Datos específicos de artículos de calzado |
| `articulo_confeccion` | Datos específicos de artículos de confección |
| `articulo_maquila` | Datos específicos de artículos de maquila |
| `articulo_servicio` | Servicios aplicados a cada artículo |
| `pago_venta` | Pagos y prepagos asociados a ventas |
| `gastos` | Gastos operativos por negocio |
| `historial_venta` | Auditoría de cambios en ventas |

---

## Acceso

El sistema tiene dos niveles de acceso:

- **Cajero** — accede vía PIN numérico desde la pantalla principal
- **Administrador** — accede vía `/login?admin=1` con usuario y contraseña

Las sesiones expiran automáticamente por inactividad (15 min admin, 20 min cajero). El middleware redirige al login en caso de sesión vencida.

---

## Notas de desarrollo

- Arquitectura en tres capas: `routes/` → `services/` → `models/`
- Las rutas importan exclusivamente desde `services/`, nunca de `models/` directamente
- El CSS sigue arquitectura modular: `base/` → `components/` → `pages/`
- Los macros de Jinja2 están en `templates/macros/`
- El token CSRF se inyecta automáticamente vía meta tag en `base.html`
