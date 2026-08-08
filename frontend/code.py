import os
import argparse

# --- Configuration ---
EXCLUDED_DIRS = {
    '.git',
    'node_modules',
    '__pycache__',
    'dist',
    'build',
    '.vscode',
    '.idea',
    '.idx',
    '.next',
    'docs',
    'ui',
    '.env',
    '.env.local'
    'test-reports','venv','__pycache__',
    'Pdf-Scraping',
    'fbr_acts_rules_ordinances',
    'fbr_customs_orders','Instrxctions','useless',
    'fbr_valuation_documents','Sample_Proj','processing_logs','logs',
    'fbr_sros_customs'
}

EXCLUDED_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg','.txt',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.zip', '.rar', '.gz', '.tar',
    '.exe', '.dll', '.so', '.o', '.jar','.Pdf',',pdf'
    '.mp4', '.mov', '.avi',
    '.mp3', '.wav',
    '.lock'
}

# --- Nayi Tabdeeli: Khaas files jo ignore karni hain ---
EXCLUDED_FILES = {
    'package-lock.json',
    '.env',
    '.env.local'
}

def process_project(root_dir, output_file_path):
    """
    Project ko process karta hai: pehle structure banata hai, phir content.
    Yeh debugging messages bhi print karega.
    """
    print("--- SCRIPT STARTING ---")
    print(f"Project Directory: {os.path.abspath(root_dir)}")
    print(f"Excluded Directories: {EXCLUDED_DIRS}")
    print(f"Excluded Files: {EXCLUDED_FILES}") # Debugging ke liye

    # Pehle purani output file ko delete kar dein (agar maujood hai)
    if os.path.exists(output_file_path):
        os.remove(output_file_path)
        print(f"Deleted old output file: {output_file_path}")

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write("PROJECT STRUCTURE:\n====================\n\n")
        
        # os.walk se sab folders aur files ko process karein
        for root, dirs, files in os.walk(root_dir, topdown=True):
            print(f"\nCurrently in directory: {root}")
            
            # Directories ko filter karein
            original_dirs = list(dirs)
            dirs[:] = [d for d in dirs if d.lower() not in EXCLUDED_DIRS]
            
            skipped_dirs = set(original_dirs) - set(dirs)
            if skipped_dirs:
                for skipped in skipped_dirs:
                    print(f"!!! SKIPPING Directory: {skipped} !!!")
            
            # --- Nayi Tabdeeli: Files ko pehle filter karein ---
            valid_files = []
            for f in sorted(files):
                is_excluded_ext = any(f.lower().endswith(ext) for ext in EXCLUDED_EXTENSIONS)
                is_excluded_file = f.lower() in EXCLUDED_FILES

                if not is_excluded_ext and not is_excluded_file:
                    valid_files.append(f)
                else:
                    print(f"!!! SKIPPING File: {f} !!!")

            # Structure likhein
            level = root.replace(root_dir, '').count(os.sep)
            if level > 0:
                 output_file.write(f"{' ' * 4 * (level-1)}└── {os.path.basename(root)}/\n")
            
            sub_indent = ' ' * 4 * level
            for f in valid_files:
                 output_file.write(f"{sub_indent}    ├── {f}\n")

        output_file.write("\n\nFILE CONTENTS:\n==============\n\n")

        # Dobara walk karein take content likh sakein
        for root, dirs, files in os.walk(root_dir, topdown=True):
            dirs[:] = [d for d in dirs if d.lower() not in EXCLUDED_DIRS]
            
            # Phir content likhein
            for filename in sorted(files):
                is_excluded_ext = any(filename.lower().endswith(ext) for ext in EXCLUDED_EXTENSIONS)
                is_excluded_file = filename.lower() in EXCLUDED_FILES

                if is_excluded_ext or is_excluded_file:
                    continue

                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, root_dir)

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    output_file.write(f"\n--- START OF FILE: {relative_path} ---\n\n")
                    output_file.write(content)
                    output_file.write(f"\n\n--- END OF FILE: {relative_path} ---\n\n" + "="*80 + "\n\n")

                except Exception as e:
                    output_file.write(f"\n--- Could not read file: {relative_path} (Error: {e}) ---\n\n" + "="*80 + "\n\n")

def main():
    parser = argparse.ArgumentParser(description="Combine project files into a single text file with debugging.")
    parser.add_argument("project_dir", type=str, help="Project ka path.")
    parser.add_argument("output_file", type=str, nargs='?', default="combined_project_code.txt", help="Output file ka naam.")
    args = parser.parse_args()

    if not os.path.isdir(args.project_dir):
        print(f"Error: Directory not found at '{args.project_dir}'")
        return
    
    process_project(args.project_dir, args.output_file)
    print(f"\n--- SCRIPT FINISHED ---")
    print(f"Output saved to '{args.output_file}'")

if __name__ == "__main__":
    main()