import os
import sys
import uuid
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.supabase import supabase
from app.core.security import get_password_hash

client = TestClient(app)

print("INICIANDO CERTIFICACIÓN DE SEGURIDAD (FASE 1.7)")
print("-" * 50)

resultados = []

def registrar_prueba(caso, result, response_status, error_msg=""):
    estado = "✅ PASS" if result == "PASS" else "❌ FAIL"
    resultados.append({
        "caso": caso,
        "resultado": result,
        "status_code": response_status,
        "detalle": error_msg
    })
    print(f"[{result}] {caso} -> HTTP {response_status} {error_msg}")

try:
    # PREPARAR DATOS DE PRUEBA
    test_email = f"seguridad_{uuid.uuid4().hex[:6]}@test.com"
    test_pass = "S3cur3P4ssw0rd!"
    
    # 1. Crear usuario test SIN password
    user_no_pass = {
        "nombre": "Test Sin Pass",
        "email": test_email,
        "rol": "ADMIN",
        "activo": True
    }
    supabase.table("usuarios").insert(user_no_pass).execute()
    
    # CASO 1: Usuario válido, pero SIN contraseña asignada (password_hash es nulo)
    resp = client.post("/api/v1/auth/login", json={"email": test_email, "password": test_pass})
    if resp.status_code == 401 and "sin credenciales" in resp.json().get("detail", "").lower():
        registrar_prueba("Bloqueo de usuario sin password_hash configurado", "PASS", resp.status_code, resp.json().get("detail"))
    else:
        registrar_prueba("Bloqueo de usuario sin password_hash configurado", "FAIL", resp.status_code, "El sistema no rechazó correctamente.")

    # 2. Asignar contraseña hasheada al usuario
    hashed = get_password_hash(test_pass)
    supabase.table("usuarios").update({"password_hash": hashed}).eq("email", test_email).execute()

    # CASO 2: Contraseña Incorrecta
    resp = client.post("/api/v1/auth/login", json={"email": test_email, "password": "WrongPassword123"})
    if resp.status_code == 401 and "incorrectas" in resp.json().get("detail", "").lower():
        registrar_prueba("Bloqueo de email válido con password incorrecta", "PASS", resp.status_code, resp.json().get("detail"))
    else:
        registrar_prueba("Bloqueo de email válido con password incorrecta", "FAIL", resp.status_code, "Permitió el acceso o devolvió otro error.")

    # CASO 3: Email Inexistente
    resp = client.post("/api/v1/auth/login", json={"email": "no_existe@test.com", "password": "any"})
    if resp.status_code == 401:
        registrar_prueba("Bloqueo de email inexistente", "PASS", resp.status_code, resp.json().get("detail"))
    else:
        registrar_prueba("Bloqueo de email inexistente", "FAIL", resp.status_code, "Permitió el acceso.")

    # CASO 4: Acceso Correcto
    resp = client.post("/api/v1/auth/login", json={"email": test_email, "password": test_pass})
    if resp.status_code == 200 and "access_token" in resp.json():
        registrar_prueba("Acceso exitoso con email válido y password correcta", "PASS", resp.status_code, "Token emitido correctamente.")
    else:
        registrar_prueba("Acceso exitoso con email válido y password correcta", "FAIL", resp.status_code, "No se generó token.")

    # LIMPIEZA
    supabase.table("usuarios").delete().eq("email", test_email).execute()

except Exception as e:
    registrar_prueba("Excepción Crítica", "FAIL", 500, str(e))

# Generar Reporte MD
reporte_md = "# AUTH SECURITY CERTIFICATION (Fase 1.7)\n\n"
for res in resultados:
    reporte_md += f"### Prueba: {res['caso']}\n"
    reporte_md += f"- **Resultado**: {'✅ PASS' if res['resultado'] == 'PASS' else '❌ FAIL'}\n"
    reporte_md += f"- **Status HTTP Esperado/Obtenido**: {res['status_code']}\n"
    reporte_md += f"- **Detalle**: {res['detalle']}\n\n"

md_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AUTH_SECURITY_CERTIFICATION.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write(reporte_md)

print(f"\nReporte de seguridad generado en: {md_path}")
