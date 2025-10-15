# Fingerprinting_osint

Este script en Python recopila información pasiva y activa sobre un dominio (WHOIS, crt.sh, Wayback, DNS, resolución) y opcionalmente hace fuzzing de directorios y búsquedas de código en GitHub. El resultado se guarda en un archivo JSON.


## Características

- WHOIS lookup
- Búsqueda de certificados en crt.sh
- Snapshots básicos desde Wayback Machine
- Resumen de DNS (A, AAAA, NS, MX, TXT, CNAME)
- Resolución de host (IPs, aliases)
- Fuzzing de directorios (opcional, con wordlist)
- Búsqueda en GitHub Code Search (opcional, con token)
- Salida JSON (opcional `--pretty` para formato legible)


## Requisitos

- Python 3.8+
- pip

Paquetes Python requeridos:

- python-whois
- dnspython
- requests


## Instalación 

1. Clonar o descargar el repositorio a tu máquina local.

```bash
git clone https://github.com/adri1709/Fingerprinting_OSINT.git
cd Fingerprinting_OSINT
```

3. Instala dependencias.

```bash
pip install python-whois dnspython requests
```


## Uso

El script se ejecuta desde la línea de comandos.

```bash
python script.py <dominio> [opciones]
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
