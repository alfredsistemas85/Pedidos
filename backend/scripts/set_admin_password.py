import os
import sys
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.supabase import supabase
from app.core.security import get_password_hash

def main():
    parser = argparse.ArgumentParser(description="Configurar contraseña inicial para un usuario.")
    parser.add_argument("--email", required=True, help="Email del usuario existente.")
    parser.add_argument("--password", required=True, help="Nueva contraseña a asignar.")
    
    args = parser.parse_args()
    
    # 1. Verificar prohibiciones
    prohibidas = ["admin123", "password", "123456", "contraseña"]
    if args.password.lower() in prohibidas:
        print("ERROR: Contraseña demasiado común. Prohibido usar admin123, password, 123456, etc.")
        sys.exit(1)
        
    # 2. Buscar usuario
    res = supabase.table("usuarios").select("id").eq("email", args.email).execute()
    if not res.data:
        print(f"ERROR: Usuario con email {args.email} no encontrado.")
        sys.exit(1)
        
    user_id = res.data[0]["id"]
    
    # 3. Hashear y actualizar
    hashed = get_password_hash(args.password)
    supabase.table("usuarios").update({"password_hash": hashed}).eq("id", user_id).execute()
    print(f"ÉXITO: Contraseña configurada y hasheada correctamente para {args.email}.")

if __name__ == "__main__":
    main()
