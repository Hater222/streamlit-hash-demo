# streamlit-hash-demo

Aplicación didáctica de hashing en Streamlit (100% web — GitHub + Streamlit Community Cloud).

## Resumen rápido
Esta app permite calcular y comparar hashes de textos y ficheros (sha256 por defecto), demostrar salting (salt), pepper (valor en `st.secrets`), y HMAC (clave en `st.secrets`). Incluye hashing incremental con barra de progreso, descarga de resultados y utilidades pedagógicas.

## Archivos en el repo
- `app.py` — App Streamlit principal.
- `hash_utils.py` — Funciones puras de hashing, HMAC y helpers.
- `requirements.txt` — Dependencias.
- `tests/test_hash_utils.md` — Ejemplos de tests manuales.
- `assets/example.txt` — Archivo de prueba.
- `LICENSE` — MIT License.
- `.gitignore` — recomendado.
- `README.md` — (este archivo)

---

## Despliegue en Streamlit Cloud (GUI only)
1. Crear repo en GitHub:
   - Accede a https://github.com → **New repository**.
   - Nombre sugerido: `streamlit-hash-demo`.
   - Inicializar con: **None** (crear vacío) o añade `.gitignore` y `LICENSE` manualmente.
2. Añadir archivos via GitHub web:
   - En el repo, click **Add file → Create new file**, pega los contenidos de cada archivo que encontrarás en este repo.
   - Para `assets/example.txt` puedes usar **Upload files**.
   - Commit al branch `main`.
3. Conectar con Streamlit Community Cloud:
   - Ve a https://share.streamlit.io/new → click **Deploy an app**.
   - Autoriza GitHub, selecciona el repositorio y la rama `main`.
   - Indica `app.py` como entrypoint.
4. Configurar `st.secrets` (en el panel de la app en Streamlit Cloud):
   - En la UI de tu app desplegada, ve a **Manage app → Secrets** y añade (ejemplo):
```toml
PEPPER = "mi_pepper_de_ejemplo_ponlo_seguro"
HMAC_KEY = "mi_hmac_key_segura"
```
   - **No** subas estos valores al repo.
5. Despliega y prueba.

---

## Notas de seguridad / limitaciones rápidas
- Hash ≠ cifrado. Un hash es una huella; no recupera el texto original.
- Salt: añade entropía pública para evitar rainbow tables; debe almacenarse junto al hash.
- Pepper & HMAC: secretos que no deben almacenarse en el código ni el repo. En esta app se configuran en `st.secrets`.
- SHA-1 es inseguro para colisiones; usar SHA-256 o SHA-512 para integridad.
- Para almacenamiento de contraseñas preferir PBKDF2 / Argon2 (mencionado, no implementado).

--- 

## Mensaje de commit sugerido
`feat: primera versión app de hashing con salt/pepper y HMAC`

## Descripción corta para el repo
"App educativa en Streamlit que demuestra hashing (SHA, BLAKE2), salting, peppering y HMAC — deploy directo con GitHub + Streamlit Cloud."

## Script de prueba manual (pasos)
1. Abrir la app desplegada.
2. Pestaña "Texto": pegar "hola mundo", seleccionar SHA-256 → Calcular.
3. Pestaña "Archivo": subir `assets/example.txt` → Calcular hash (ver progreso).
4. Generar salt y aplicar `with_salt` → comparar hashes con la sección "Comparar".
5. Configurar `st.secrets` con `PEPPER` y `HMAC_KEY` y probar funciones de pepper y HMAC.
6. Descargar CSV con resultados y revisar contenido.

