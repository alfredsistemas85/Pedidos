import os
import sys
import uuid
import json

# Añadir el directorio actual al PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.supabase import supabase
from app.domain.models import EstadoPedido

client = TestClient(app)

print("INICIANDO FASE 1.6 - CERTIFICACION DEL BACKEND MVP")
print("-" * 50)

# Variables globales para el reporte
resultados = []

def registrar_prueba(caso, status, request_data=None, response_status=None, response_data=None, error=None):
    res = {
        "caso": caso,
        "status": status,
        "request_data": request_data,
        "response_status": response_status,
        "error": error
    }
    
    # Sanitizar respuesta
    if response_data:
        if isinstance(response_data, dict):
            sanitized = response_data.copy()
            if "access_token" in sanitized:
                sanitized["access_token"] = "*** SANITIZED ***"
            res["response_data"] = sanitized
        else:
            res["response_data"] = response_data
            
    resultados.append(res)
    print(f"[{status}] {caso}")

try:
    # 0. SETUP: Obtener un email de admin para el login
    # Ya que la validación de password está desactivada temporalmente, necesitamos cualquier email de ADMIN
    res_users = supabase.table("usuarios").select("email").eq("rol", "ADMIN").limit(1).execute()
    if not res_users.data:
        registrar_prueba("Bloqueo de Autenticación", "FAIL", error="No existe un usuario con rol ADMIN en la tabla 'usuarios' para realizar las pruebas. La prueba está bloqueada.")
        raise Exception("Requisito incumplido: No hay usuarios ADMIN locales válidos.")
    
    admin_email = res_users.data[0]["email"]

    # 4. SEGURIDAD: Validar acceso sin token
    response = client.post("/api/v1/products/", json={"nombre": "TEST_Auth_Fail", "precio": 10.0, "categoria": "Pizzas"})
    if response.status_code == 401:
        registrar_prueba("Seguridad: Acceso a ruta protegida sin token", "PASS", response_status=response.status_code, response_data=response.json())
    else:
        registrar_prueba("Seguridad: Acceso a ruta protegida sin token", "FAIL", response_status=response.status_code, error="Debería retornar 401")

    # Autenticación Real (Login)
    response = client.post("/api/v1/auth/login", json={"email": admin_email, "password": "any_password"})
    if response.status_code == 200:
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        registrar_prueba("Seguridad: Login exitoso", "PASS", request_data={"email": admin_email}, response_status=response.status_code, response_data=response.json())
    else:
        registrar_prueba("Seguridad: Login exitoso", "FAIL", response_status=response.status_code, error="Login falló")
        raise Exception("Login falló, abortando pruebas.")

    # 1. PRODUCTOS
    # POST /products
    product_payload = {
        "nombre": f"TEST_PIZZA_{uuid.uuid4().hex[:4]}",
        "descripcion": "Pizza de prueba automatizada",
        "precio": 1200.50,
        "categoria": "Pizzas",
        "stock_controlado": True,
        "stock": 10
    }
    response = client.post("/api/v1/products/", json=product_payload, headers=headers)
    if response.status_code == 200:
        created_product = response.json()
        product_id = created_product["id"]
        registrar_prueba("Productos: Crear producto (POST)", "PASS", product_payload, response.status_code, created_product)
    else:
        registrar_prueba("Productos: Crear producto (POST)", "FAIL", product_payload, response.status_code, response.json())
        raise Exception("No se pudo crear el producto")

    # PATCH /products/{id}
    patch_payload = {
        "nombre": f"{created_product['nombre']}_MODIFICADA",
        "precio": 1500.00,
        "stock": 5
    }
    response = client.patch(f"/api/v1/products/{product_id}", json=patch_payload, headers=headers)
    if response.status_code == 200 and response.json()["precio"] == 1500.00:
        registrar_prueba("Productos: Editar producto (PATCH)", "PASS", patch_payload, response.status_code, response.json())
    else:
        registrar_prueba("Productos: Editar producto (PATCH)", "FAIL", patch_payload, response.status_code, response.json())

    # GET /products/{id}
    response = client.get(f"/api/v1/products/{product_id}")
    if response.status_code == 200 and response.json()["id"] == product_id:
        registrar_prueba("Productos: Obtener producto detalle (GET)", "PASS", None, response.status_code, response.json())
    else:
        registrar_prueba("Productos: Obtener producto detalle (GET)", "FAIL", None, response.status_code, response.json())

    # 2. PEDIDOS
    # POST /orders
    order_payload = {
        "pedido": {
            "origen": "PANEL",
            "observaciones": "TEST_OBSERVACION"
        },
        "items": [
            {
                "producto_id": product_id,
                "cantidad": 2,
                "precio_unitario": 1500.00,
                "subtotal": 3000.00
            }
        ]
    }
    response = client.post("/api/v1/orders/", json=order_payload, headers=headers)
    if response.status_code == 200:
        created_order = response.json()
        order_id = created_order["id"]
        registrar_prueba("Pedidos: Crear pedido (POST)", "PASS", order_payload, response.status_code, created_order)
    else:
        registrar_prueba("Pedidos: Crear pedido (POST)", "FAIL", order_payload, response.status_code, response.json())
        raise Exception("No se pudo crear el pedido")

    # PATCH /orders/{id}/status (Transición Válida)
    status_payload = {"estado": "CONFIRMADO"}
    response = client.patch(f"/api/v1/orders/{order_id}/status", json=status_payload, headers=headers)
    if response.status_code == 200 and response.json()["estado"] == "CONFIRMADO":
        registrar_prueba("Pedidos: Transición estado válida PENDIENTE->CONFIRMADO (PATCH)", "PASS", status_payload, response.status_code, response.json())
    else:
        registrar_prueba("Pedidos: Transición estado válida (PATCH)", "FAIL", status_payload, response.status_code, response.json())

    # PATCH /orders/{id}/status (Transición Inválida)
    # De CONFIRMADO a ENTREGADO directamente es inválido
    status_payload_invalid = {"estado": "ENTREGADO"}
    response = client.patch(f"/api/v1/orders/{order_id}/status", json=status_payload_invalid, headers=headers)
    if response.status_code == 409: # HTTP 409 Conflict o StateMachineException
        registrar_prueba("Pedidos: Rechazo de transición inválida CONFIRMADO->ENTREGADO", "PASS", status_payload_invalid, response.status_code, response.json())
    else:
        registrar_prueba("Pedidos: Rechazo de transición inválida", "FAIL", status_payload_invalid, response.status_code, response.json())

    # Limpieza: Cancelar pedido para no afectar ventas_hoy (o dejarlo para ver si sube)
    client.patch(f"/api/v1/orders/{order_id}/status", json={"estado": "CANCELADO"}, headers=headers)

    # GET /orders (Paginación)
    response = client.get("/api/v1/orders/?page=1&limit=5", headers=headers)
    if response.status_code == 200 and "data" in response.json() and "total" in response.json():
        registrar_prueba("Pedidos: Listar paginado (GET)", "PASS", None, response.status_code, {"total": response.json()["total"], "data_length": len(response.json()["data"])})
    else:
        registrar_prueba("Pedidos: Listar paginado (GET)", "FAIL", None, response.status_code, response.json())

    # 3. DASHBOARD
    response = client.get("/api/v1/admin/dashboard", headers=headers)
    if response.status_code == 200 and "ventas_hoy" in response.json():
        registrar_prueba("Dashboard: Obtener métricas reales (GET)", "PASS", None, response.status_code, response.json())
    else:
        registrar_prueba("Dashboard: Obtener métricas reales (GET)", "FAIL", None, response.status_code, response.json())

    # LIMPIEZA PRODUCTOS (Soft Delete)
    # DELETE /products/{id}
    response = client.delete(f"/api/v1/products/{product_id}", headers=headers)
    if response.status_code == 200 and response.json()["producto"]["activo"] == False:
        registrar_prueba("Productos: Soft delete (DELETE)", "PASS", None, response.status_code, response.json())
    else:
        registrar_prueba("Productos: Soft delete (DELETE)", "FAIL", None, response.status_code, response.json())

    # Verificar que GET /products ya no lo devuelve
    response = client.get("/api/v1/products/")
    product_found = any(p["id"] == product_id for p in response.json())
    if not product_found:
        registrar_prueba("Productos: Verificación de soft delete en catálogo", "PASS", None, 200, None)
    else:
        registrar_prueba("Productos: Verificación de soft delete en catálogo", "FAIL", None, 200, "Producto eliminado lógicamente sigue apareciendo en el catálogo")

except Exception as e:
    print(f"ERROR DURANTE EJECUCIÓN: {e}")
    registrar_prueba("Excepción Crítica", "FAIL", error=str(e))

# Escribir reporte en Markdown
reporte_md = "# BACKEND CERTIFICATION REPORT (Fase 1.6)\n\n"
reporte_md += "Este reporte fue generado automáticamente por el script de certificación.\n\n"

total_tests = len(resultados)
passed_tests = sum(1 for r in resultados if r["status"] == "PASS")
failed_tests = total_tests - passed_tests

reporte_md += f"## Resumen\n"
reporte_md += f"- **Total Pruebas**: {total_tests}\n"
reporte_md += f"- **Aprobadas**: {passed_tests}\n"
reporte_md += f"- **Fallidas**: {failed_tests}\n\n"

reporte_md += "## Detalle de Pruebas\n\n"

for i, res in enumerate(resultados):
    estado_md = "✅ PASS" if res["status"] == "PASS" else "❌ FAIL"
    reporte_md += f"### Prueba {i+1}: {res['caso']}\n"
    reporte_md += f"**Estado**: {estado_md}\n"
    if res['response_status']:
        reporte_md += f"**Status HTTP**: {res['response_status']}\n"
    if res['error']:
        reporte_md += f"**Error/Motivo**: {res['error']}\n"
    
    if res['response_data']:
        reporte_md += "**Respuesta Sanitizada**:\n"
        reporte_md += "```json\n"
        reporte_md += json.dumps(res['response_data'], indent=2, ensure_ascii=False) + "\n"
        reporte_md += "```\n"
    reporte_md += "\n---\n\n"

# Escribir el reporte MD en la misma carpeta donde esté el script
md_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BACKEND_CERTIFICATION_REPORT.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write(reporte_md)

print("-" * 50)
print(f"CERTIFICACIÓN FINALIZADA. Reporte generado en: {md_path}")

