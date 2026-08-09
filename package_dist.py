import os
import shutil
import zipfile

def make_archive(source_dir, output_filename):
    # Exclusiones de seguridad y desarrollo
    ignore_patterns = [
        '.git',
        '.agents',
        'venv',
        '__pycache__',
        'fourier_ifa.db',
        'license.key',
        'nuitka-build',
        '.next',
        'node_modules',
        'package_dist.py',
        'tzanix_edge_node.zip',
        '.dockerignore',
        'portal/.next',
        'portal/node_modules',
        'portal/out',
    ]

    print("=================================================================")
    print("TZANiX PACKAGER - GENERANDO DISTRIBUCIÓN LIMPIA")
    print("=================================================================")
    
    # Crear un directorio temporal de distribución
    dist_dir = "tzanix_edge_node"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)

    # Copiar archivos respetando exclusiones
    for root, dirs, files in os.walk(source_dir):
        # Filtrar directorios excluidos
        dirs[:] = [d for d in dirs if not any(ignore in os.path.join(root, d) for ignore in ignore_patterns)]
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, source_dir)
            
            # Validar que el archivo no esté en la lista de exclusiones
            if any(ignore in rel_path.replace("\\", "/") for ignore in ignore_patterns):
                continue
                
            dest_file_path = os.path.join(dist_dir, rel_path)
            dest_dir_path = os.path.dirname(dest_file_path)
            
            if not os.path.exists(dest_dir_path):
                os.makedirs(dest_dir_path)
                
            shutil.copy2(file_path, dest_file_path)
            
    # Crear el archivo ZIP
    zip_filename = f"{output_filename}.zip"
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
        
    print(f"Comprimiendo archivos en {zip_filename}...")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_dir)
                zipf.write(file_path, arcname)
                
    # Limpiar carpeta temporal
    shutil.rmtree(dist_dir)
    
    print(f"\n[ÉXITO] Archivo de distribución generado con éxito:\n  {os.path.abspath(zip_filename)}")
    print("=================================================================")

if __name__ == "__main__":
    make_archive(".", "tzanix_edge_node")
