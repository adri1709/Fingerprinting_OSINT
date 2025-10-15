# recon.py — Recon pasivo y activo (salida JSON)

**Recon.py** es un script en Python que recopila información pasiva y activa sobre un dominio (WHOIS, crt.sh, Wayback, DNS, resolución) y opcionalmente hace fuzzing de directorios y búsquedas de código en GitHub. El resultado se guarda en un archivo JSON.

---

## Características

- WHOIS lookup
- Búsqueda de certificados en crt.sh
- Snapshots básicos desde Wayback Machine
- Resumen de DNS (A, AAAA, NS, MX, TXT, CNAME)
- Resolución de host (IPs, aliases)
- Fuzzing de directorios (opcional, con wordlist)
- Búsqueda en GitHub Code Search (opcional, con token)
- Salida JSON (opcional `--pretty` para formato legible)

---

## Requisitos

- Python 3.8+
- pip

Paquetes Python requeridos (puedes instalarlos manualmente o con `requirements.txt`):

- python-whois
- dnspython
- requests

---

## Instalación (rápida)

1. Clonar o descargar el repositorio a tu máquina local.

```bash
# clona tu repo (ejemplo)
git clone https://github.com/tuusuario/tu-repo.git
cd tu-repo
```

2. Crea un entorno virtual (recomendado) y actívalo.

```bash
python3 -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Windows (CMD)
.\.venv\Scripts\activate.bat
```

3. Instala dependencias.

```bash
pip install --upgrade pip
pip install python-whois dnspython requests
```

(Opcional) crea un `requirements.txt` y usa:

```bash
pip freeze > requirements.txt
# o, para instalar desde requirements.txt
pip install -r requirements.txt
```

---

## Uso

El script se ejecuta desde la línea de comandos.

```bash
python3 recon.py <dominio> [opciones]
```

### Opciones

- `domain` — dominio objetivo (posicional). Ej: `example.com`
- `--fuzz <ruta>` — ruta a una wordlist para fuzz de directorios
- `--github-token <token>` — token opcional para la GitHub Code Search
- `--output, -o <archivo>` — archivo JSON de salida (por defecto `recon_results.json`)
- `--pretty` — formatea el JSON con indentación
- `--threads <n>` — número de threads para fuzz (por defecto `20`)

### Ejemplos de comando

1. Ejecución básica — WHOIS + crt.sh + Wayback + DNS + resolución (sin GitHub ni fuzz):

```bash
python3 recon.py example.com
```

2. Usar salida "pretty" y archivo personalizado:

```bash
python3 recon.py example.com -o resultados.json --pretty
```

3. Incluir búsqueda en GitHub (añade tu token):

```bash
python3 recon.py example.com --github-token ghp_xxx... -o recon_github.json --pretty
```

4. Hacer fuzz de directorios con una wordlist (ej: `wordlist.txt`):

```bash
python3 recon.py example.com --fuzz /ruta/a/wordlist.txt --threads 50 -o recon_fuzz.json --pretty
```

> Nota: el script intentará normalizar el URL para el fuzz (si pasas `example.com` usará `https://example.com`).

---

## Formato de la wordlist (para `--fuzz`)

- Un entry por línea.
- No debe incluir slashes frontales (`/`) — por ejemplo:

```
admin
login
robots.txt
.gitignore
.env
```

---

## `recon_results.json` — estructura básica de salida

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

---

## Buenas prácticas y limitaciones

- **Rate limits y cortes**: crt.sh, GitHub y Wayback imponen límites. Si planeas automatizar escaneos masivos respeta rate limits y añade retardo entre peticiones.
- **Permisos legales**: haz recon en objetivos que poseas o tengas permiso para auditar. El fuzzing activo puede considerarse intrusivo.
- **Tokens**: guarda tu `--github-token` en variables de entorno o en un gestor seguro; evita subir tokens a repos públicos.
- **User-Agent**: el fuzzer usa `Recon-Fuzzer/1.0`. Cambia si es necesario.
- **Concurrencia**: subir `--threads` acelera fuzz pero puede generar tráfico masivo y false positives.

---

## Depuración y resolución de errores

- `whois` puede fallar si la librería no soporta TLDs muy nuevos o la respuesta del servidor es inusual.
- `crt.sh` a veces devuelve contenido no-JSON — el script detecta esto y reporta el error en la sección `crtsh`.
- Si `dns_records` devuelve errores, revisa la configuración DNS de tu entorno y los timeouts.
- Para problemas con `requests`, prueba a aumentar `timeout` o comprobar conectividad.

---

## Seguridad y ética

Este script realiza consultas pasivas y algunas acciones activas (fuzzing y solicitudes HTTP). Asegúrate de:

1. Tener autorización explícita para testear el dominio.
2. No usarlo para comprometer sistemas.
3. Cumplir la legislación local y los términos de servicio de los proveedores externos.

---

## Contribuciones

Si quieres mejorar el script, sugerencias comunes:

- Añadir soporte para `--rate` o `--delay` en fuzz
- Añadir más tipos DNS o peticiones recursivas
- Soporte para guardar resultados parciales y reanudar
- Soporte para limitar domains por scope

Haz un fork, crea una rama y abre un Pull Request.

---

## Ejemplo rápido (paso a paso)

```bash
# Crear entorno
python3 -m venv .venv
source .venv/bin/activate
pip install python-whois dnspython requests

# Ejecutar recon básico
python3 recon.py example.com --pretty -o example_recon.json

# Ejecutar con fuzz
python3 recon.py example.com --fuzz wordlist.txt --threads 30 -o example_recon_fuzz.json --pretty
```

---

## Licencia

Incluye aquí la licencia que prefieras (p. ej. MIT). Añade un `LICENSE` en tu repo.

---

## Preguntas frecuentes (FAQ)

**P: ¿Puedo ejecutar esto desde Windows?**
R: Sí — usa `python` en lugar de `python3` si tu entorno lo requiere y activa el virtualenv con el script de Windows.

**P: ¿Por qué `crt.sh` a veces no devuelve JSON?**
R: crt.sh puede devolver HTML en ciertas condiciones; el script detecta y reporta ese caso.

---

## Contacto

Para dudas o soporte abre un issue en el repositorio o contacta al mantenedor.

---

*Fin del README.*

