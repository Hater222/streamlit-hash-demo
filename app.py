"""
app.py

Streamlit app: interfaz didáctica para hashing, salting, peppering y HMAC.
Entrada: texto o ficheros. Salida: hash (hex), opciones de descarga y comparación.

Notas:
- Secrets: PEPPER y HMAC_KEY deben configurarse en st.secrets en Streamlit Cloud.
- Límite de tamaño de archivo por defecto: 10 MB (configurable).
"""

from __future__ import annotations
import streamlit as st
from hash_utils import hash_text, hash_file_chunked, generate_salt, apply_salt, apply_pepper, hmac_text, compare_hashes, DEFAULT_ALGOS
import io
import csv
import base64

# ----- Configuración -----
st.set_page_config(page_title="Streamlit Hash Demo", layout="centered")
MAX_FILE_MB = 10
MAX_FILE_BYTES = MAX_FILE_MB * 1024 * 1024

# ----- UI -----
st.title("🔐 Streamlit Hash Demo")
st.markdown("App educativa: hashing (SHA/BLAKE2), salt, pepper y HMAC. **No** almacenes secrets en el repo.")

tabs = st.tabs(["Hash Texto", "Hash Archivo", "Comparar", "Salting/Pepper", "HMAC", "Descargar / CSV", "Ayuda"])

with tabs[0]:
    st.header("Hash de texto")
    algo = st.selectbox("Algoritmo", DEFAULT_ALGOS, index=0)
    txt = st.text_area("Texto a hashear", value="hola mundo")
    if st.button("Calcular hash (texto)"):
        result = hash_text(txt, algorithm=algo)
        st.code(result)
        st.success(f"Algoritmo: {algo} — longitud: {len(result)} hex chars")

with tabs[1]:
    st.header("Hash de archivo")
    f = st.file_uploader("Sube un fichero (máx 10 MB)", type=None)
    algo_file = st.selectbox("Algoritmo (archivo)", DEFAULT_ALGOS, index=0, key="algo_file")
    if f is not None:
        if f.size > MAX_FILE_BYTES:
            st.error(f"Fichero demasiado grande: {f.size} bytes > {MAX_FILE_BYTES} bytes")
        else:
            progress = st.progress(0)
            status = st.empty()
            # leer en chunks usando buffer
            buffer = io.BytesIO(f.read())
            buffer.seek(0)
            def progress_cb(total_bytes):
                # actualizamos barra en base a bytes leídos; como no conocemos total fiable, usamos heurística
                try:
                    pct = min(1.0, total_bytes / f.size)
                except Exception:
                    pct = 0.0
                progress.progress(int(pct*100))
                status.text(f"{total_bytes} bytes leídos")
            digest = hash_file_chunked(buffer, algorithm=algo_file, chunk_size=8192, progress_callback=progress_cb)
            st.code(digest)
            st.success(f"Algoritmo: {algo_file} — tamaño: {f.size} bytes")

with tabs[2]:
    st.header("Comparar hashes")
    h1 = st.text_input("Hash 1")
    h2 = st.text_input("Hash 2")
    if st.button("Comparar"):
        ok = compare_hashes(h1.strip(), h2.strip())
        if ok:
            st.success("Los hashes coinciden (compare_digest)")
        else:
            st.error("Los hashes NO coinciden")

with tabs[3]:
    st.header("Salting y Pepper")
    col1, col2 = st.columns(2)
    with col1:
        txt_s = st.text_input("Texto base para salt/pepper", value="secret-password")
        if st.button("Generar salt (base64)"):
            salt = generate_salt()
            st.code(salt)
            st.info("Guarda el salt junto al hash. Salt es público y no sustituye a buenas prácticas.")
    with col2:
        salt_input = st.text_input("Salt (base64) — pegar aquí para aplicar")
        algo_sp = st.selectbox("Algoritmo (salt/pepper)", DEFAULT_ALGOS, index=0, key="algo_sp")
        pepper = st.secrets.get("PEPPER") if hasattr(st, "secrets") else None
        if pepper:
            st.write("Pepper configurado en st.secrets (usado si lo aplicas).")
        else:
            st.warning("PEPPER no configurado en st.secrets — configurar en Streamlit Cloud panel de Secrets.")
        if st.button("Hash con salt"):
            if not salt_input:
                st.error("Provee un salt (o genera uno).")
            else:
                combined = apply_salt(txt_s, salt_input)
                digest_sp = hash_text(combined, algorithm=algo_sp)
                st.code(digest_sp)
                st.write("Nota: el salt se debe almacenar junto al digest para verificación.")
        if st.button("Hash con pepper (usando PEPPER en st.secrets)"):
            if not pepper:
                st.error("PEPPER no configurado.")
            else:
                combined_p = apply_pepper(txt_s, pepper)
                digest_p = hash_text(combined_p, algorithm=algo_sp)
                st.code(digest_p)
                st.write("Pepper es secreto y no debe almacenarse en texto claro; usar st.secrets.")

with tabs[4]:
    st.header("HMAC")
    txt_h = st.text_input("Texto para HMAC", value="mensaje")
    algo_h = st.selectbox("Algoritmo HMAC", DEFAULT_ALGOS, index=0, key="algo_h")
    hmac_key = st.secrets.get("HMAC_KEY") if hasattr(st, "secrets") else None
    if hmac_key:
        st.write("HMAC_KEY configurada en st.secrets.")
    else:
        st.warning("HMAC_KEY no configurada en st.secrets — añadir en Streamlit Cloud.")
    if st.button("Calcular HMAC"):
        if not hmac_key:
            st.error("HMAC_KEY no configurada.")
        else:
            mac = hmac_text(txt_h, key=hmac_key, algorithm=algo_h)
            st.code(mac)
            st.write("HMAC provee **autenticidad** y detección de modificación si la clave es secreta.")

with tabs[5]:
    st.header("Descargar / CSV")
    results = []
    st.write("Puedes añadir entradas manualmente para descargar un CSV con resultados.")
    c1 = st.text_input("Etiqueta (ej: archivo.txt)")
    c2 = st.text_input("Hash (hex)")
    if st.button("Añadir a resultados"):
        if c1 and c2:
            results.append((c1, c2))
            st.success("Añadido (temporal, solo dura en esta interacción).")
        else:
            st.error("Proveer etiqueta y hash.")
    if results:
        st.write("Resultados actuales:")
        st.table(results)
        # preparar CSV
        csv_bytes = io.StringIO()
        writer = csv.writer(csv_bytes)
        writer.writerow(["label", "hash"])
        for r in results:
            writer.writerow(r)
        b64 = base64.b64encode(csv_bytes.getvalue().encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="hash-results.csv">Descargar CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
        st.info("No hay resultados en esta sesión interactiva. Añade entradas y descarga.")

with tabs[6]:
    st.header("Ayuda y buenas prácticas")
    st.markdown(
        """
- **Hash ≠ cifrado**. No podrás recuperar el texto original desde un hash.
- **Salt**: público, único por entrada, evita rainbow tables.
- **Pepper**: secreto adicional; almacenarlo en st.secrets o KMS; no subir al repo.
- **HMAC**: autentica origen/integidad si clave secreta es compartida.
- **SHA-1**: vulnerable a colisiones — no usar para seguridad crítica.
- Para contraseñas, usar PBKDF2/Argon2 con sal y múltiples iteraciones (señalado como mejora).
"""
    )
