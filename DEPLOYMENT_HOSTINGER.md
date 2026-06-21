# Guía de Despliegue en Hostinger

## Requisitos Previos
- Cuenta de Hostinger con acceso SSH
- Dominio configurado en Hostinger
- PostgreSQL configurado en Hostinger

## Despliegue del Backend

### 1. Subir el código al servidor
```bash
# Desde tu máquina local
scp -r /opt/acuaticapp-backend usuario@tu-dominio-hostinger.com:/home/usuario/
```

### 2. Conectar por SSH al servidor
```bash
ssh usuario@tu-dominio-hostinger.com
cd acuaticapp-backend
```

### 3. Crear entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales de PostgreSQL
```

### 6. Ejecutar migraciones
```bash
python scripts/migrate_add_grupo_id.py
python scripts/migrate_add_admin_telefono.py
python scripts/seed_data.py
```

### 7. Configurar Gunicorn para producción
```bash
pip install gunicorn
```

### 8. Crear archivo de servicio systemd
```bash
sudo nano /etc/systemd/system/acuaticapp.service
```

Contenido del archivo:
```ini
[Unit]
Description=Acuaticapp Backend
After=network.target

[Service]
User=usuario
Group=usuario
WorkingDirectory=/home/usuario/acuaticapp-backend
Environment="PATH=/home/usuario/acuaticapp-backend/venv/bin"
ExecStart=/home/usuario/acuaticapp-backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

### 9. Iniciar el servicio
```bash
sudo systemctl start acuaticapp
sudo systemctl enable acuaticapp
```

### 10. Configurar Nginx como reverse proxy
```bash
sudo nano /etc/nginx/sites-available/acuaticapp
```

Contenido:
```nginx
server {
    listen 80;
    server_name tu-dominio-hostinger.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 11. Habilitar el sitio
```bash
sudo ln -s /etc/nginx/sites-available/acuaticapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Despliegue del Frontend

### 1. Construir el frontend
```bash
cd /opt/acuaticapp-frontend
npm run build
```

### 2. Configurar URL del API
Editar `.env.production`:
```
VITE_API_URL=https://tu-dominio-hostinger.com/api
```

### 3. Subir archivos al servidor
```bash
scp -r dist/* usuario@tu-dominio-hostinger.com:/home/usuario/public_html/
```

### 4. Configurar HTTPS con Let's Encrypt
```bash
sudo certbot --nginx -d tu-dominio-hostinger.com
```

## Acceso desde Celulares

Una vez desplegado, los usuarios pueden acceder:
- **Frontend**: https://tu-dominio-hostinger.com
- **Backend API**: https://tu-dominio-hostinger.com/api

El frontend funcionará desde cualquier dispositivo con acceso a internet.

## Solución de Problemas

### Verificar que el backend está funcionando
```bash
curl https://tu-dominio-hostinger.com/api/health
```

### Verificar logs del backend
```bash
sudo journalctl -u acuaticapp -f
```

### Verificar logs de Nginx
```bash
sudo tail -f /var/log/nginx/error.log
```

## Configuración CORS en Producción

En `app/main.py`, cambiar `allow_origins` para producción:
```python
allow_origins=["https://tu-dominio-hostinger.com"]
```
