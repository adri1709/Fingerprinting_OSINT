# Fingerprinting_OSINT

Este repositorio contiene dos scripts de Python para reconocimiento y captura de información:

1. **Script de Reconocimiento OSINT** (`script.py`) - Recopila información pasiva y activa sobre un dominio
2. **Servidor de Captura User-Agent** (`script2.py`) - Captura User-Agents de visitantes y los envía a un webhook

## Scripts Incluidos

### Script 1: Reconocimiento OSINT (`script.py`)

Recopila información pasiva y activa sobre un dominio (WHOIS, crt.sh, Wayback, DNS, resolución) y opcionalmente hace fuzzing de directorios y búsquedas de código en GitHub. El resultado se guarda en un archivo JSON.

#### Características

- WHOIS lookup
- Búsqueda de certificados en crt.sh
- Snapshots básicos desde Wayback Machine
- Resumen de DNS (A, AAAA, NS, MX, TXT, CNAME)
- Resolución de host (IPs, aliases)
- Fuzzing de directorios (opcional, con wordlist)
- Búsqueda en GitHub Code Search (opcional, con token)
- Salida JSON (opcional `--pretty` para formato legible)

### Script 2: Captura User-Agent (`script2.py`)

Servidor HTTP que captura User-Agents de los visitantes, los guarda en un archivo local y los envía a un webhook para análisis externo.

#### Características

- Servidor HTTP en puerto 8080
- Captura automática de User-Agent de cada petición
- Almacenamiento local en archivo `user_agents.txt`
- Envío automático a webhook externo (webhook.site)
- Logging detallado de todas las operaciones
- Respuesta HTML confirmando la captura

## Requisitos

- Python 3.8+
- pip

### Paquetes Python requeridos

Para ambos scripts:
```bash
pip install requests
```

Para el script de reconocimiento OSINT (`script.py`):
```bash
pip install python-whois dnspython requests
```

## Instalación 

1. Clonar o descargar el repositorio a tu máquina local.

```bash
git clone https://github.com/adri1709/Fingerprinting_OSINT.git
cd Fingerprinting_OSINT
```

2. Instalar dependencias.

```bash
pip install python-whois dnspython requests
```

## Uso

### Script 1: Reconocimiento OSINT (`script.py`)

El script se ejecuta desde la línea de comandos.

```bash
python script.py <dominio> [opciones]
```

#### Opciones

- `domain` — dominio objetivo (posicional). Ej: `example.com`
- `--fuzz <ruta>` — ruta a una wordlist para fuzz de directorios
- `--github-token <token>` — token opcional para la GitHub Code Search
- `--output, -o <archivo>` — archivo JSON de salida (por defecto `recon_results.json`)
- `--pretty` — formatea el JSON con indentación
- `--threads <n>` — número de threads para fuzz (por defecto `20`)

#### Ejemplos de comando

1. Ejecución básica — WHOIS + crt.sh + Wayback + DNS + resolución (sin GitHub ni fuzz):

```bash
python script.py example.com
```

2. Usar salida "pretty" y archivo personalizado:

```bash
python script.py example.com -o resultados.json --pretty
```

3. Incluir búsqueda en GitHub (añade tu token):

```bash
python script.py example.com --github-token ghp_xxx... -o recon_github.json --pretty
```

4. Hacer fuzz de directorios con una wordlist (ej: `wordlist.txt`):

```bash
python script.py example.com --fuzz /ruta/a/wordlist.txt --threads 50 -o recon_fuzz.json --pretty
```

> Nota: el script intentará normalizar el URL para el fuzz (si pasas `example.com` usará `https://example.com`).

### Script 2: Captura User-Agent (`script2.py`)

#### Configuración

1. **Configurar Webhook URL**: Antes de ejecutar, modifica la variable `WEBHOOK_URL` en el script con tu webhook personalizado:

```python
WEBHOOK_URL = 'https://webhook.site/tu-id-unico-aqui'
```

2. **Ejecutar el servidor**:

```bash
python script2.py
```

#### Uso del servidor

1. El servidor se ejecuta en `localhost:8080`
2. Cualquier petición GET capturará el User-Agent del navegador/cliente
3. Los User-Agents se guardan en `user_agents.txt`
4. Se envía automáticamente al webhook configurado
5. El visitante verá un mensaje de confirmación

#### Ejemplo de uso

```bash
# Iniciar el servidor
python script2.py

# En otro terminal o navegador, hacer una petición
curl http://localhost:8080
# o simplemente visitar http://localhost:8080 en el navegador
```

#### Verificar capturas

```bash
# Ver User-Agents capturados
type user_agents.txt
# o en sistemas Unix: cat user_agents.txt
```

## Formato de la wordlist (para `--fuzz` en script.py)

- Un entry por línea.
- No debe incluir slashes frontales (`/`) — por ejemplo:

```
admin
login
robots.txt
.gitignore
.env
```

## Formatos de salida

### `recon_results.json` — estructura básica de salida (script.py)

El JSON resultante contiene las siguientes claves principales:

```json
{
  "domain": "example.com",
  "timestamp_utc": "2025-10-15T12:34:56Z",
  "whois": { ... },
  "crtsh": [ ... ],
  "wayback": [ ... ],
  "github_search": { ... },
  "dns_records": { "A": [...], "MX": [...], ... },
  "resolve_host": { "hostname": "...", "ips": [...] },
  "fuzz_hits": [ {"url":"...","status":200,"length":1234}, ... ],
  "runtime_seconds": 12.34
}
```

### `user_agents.txt` — archivo de User-Agents capturados (script2.py)

Ejemplo de contenido:

```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1
curl/7.68.0
```

## Configuración avanzada

### Script 2: Personalización del servidor

Puedes modificar las siguientes variables en `script2.py`:

- `WEBHOOK_URL`: URL del webhook donde enviar los User-Agents
- Puerto del servidor (línea `server_address = ('', 8080)`): cambiar `8080` por el puerto deseado
- Archivo de salida: cambiar `'user_agents.txt'` por el nombre de archivo deseado

### Webhook.site

Para obtener una URL de webhook gratuita:

1. Visita [webhook.site](https://webhook.site)
2. Copia la URL única generada
3. Reemplaza `WEBHOOK_URL` en el script

## Casos de uso

### Script 1 (Reconocimiento OSINT)
- Auditorías de seguridad
- Reconocimiento pasivo de objetivos
- Investigación de dominios
- Mapeo de infraestructura web

### Script 2 (Captura User-Agent)
- Análisis de tráfico web
- Identificación de bots vs usuarios reales
- Estudios de dispositivos y navegadores
- Honeypots y trampas de seguridad

