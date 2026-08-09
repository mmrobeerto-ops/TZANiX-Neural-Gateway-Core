import os
import licensing

def main():
    print("=================================================================")
    print("TZANiX LICENSE MANAGER - GENERADOR DE LLAVE DE DESARROLLO")
    print("=================================================================")
    
    current_uuid = licensing.get_hardware_uuid()
    print(f"Detectando UUID de Hardware... UUID: {current_uuid}")
    
    client_name = "TZANiX Dev Team"
    expiry_days = 365
    
    print(f"Generando token de licencia para:")
    print(f"  Cliente: {client_name}")
    print(f"  Expiración: {expiry_days} días")
    
    token = licensing.generate_license_token(current_uuid, client_name, expiry_days)
    
    license_file_path = os.path.join(os.path.dirname(__file__), "license.key")
    with open(license_file_path, "w") as f:
        f.write(token)
        
    print(f"\n[ÉXITO] Archivo 'license.key' generado con éxito en:\n  {license_file_path}")
    print("=================================================================")

if __name__ == "__main__":
    main()
