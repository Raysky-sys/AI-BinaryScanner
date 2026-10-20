import os
import sys

# Expanded Anchor List (Case-insensitive)
ANCHORS = [
    # --- C2PA & Technical Markers (Universal) ---
    b"c2pa", b"c2pa-ocsp", b"digitalsourcetype", b"trainedalgorithmicmedia", 
    b"compositewithtrainedalgorithmicmedia", b"manifest", b"assertions", 
    b"provenance", b"jumbf", b"cai", b"content credentials",
    
    # --- Google Specific ---
    b"pki.goog", b"google c2pa", b"google core time stamping", b"goog/c2pa",
    
    # --- OpenAI / Microsoft Specific ---
    b"openai", b"openai.com", b"dall-e", b"dall-e 3", b"microsoft.com", 
    b"bing.com", b"microsoft-c2pa", b"designer",
    
    # --- Adobe Specific ---
    b"adobe", b"firefly", b"adobe-c2pa",
    
    # --- Meta Specific ---
    b"meta.com", b"imagine",
    
    # --- Local AI Tools & Frameworks ---
    b"automatic1111", b"sd-webui", b"comfyui", b"workflow", b"fooocus", 
    b"invokeai", b"kohya", b"stable diffusion",
    
    # --- Metadata Fields (The "Tell-Tale" signs) ---
    b"prompt:", b"negative prompt:", b"steps:", b"sampler:", 
    b"cfg scale:", b"seed:", b"modelhash:"
]


def scan_file(file_path):
    """Reads a file in binary, converts to lowercase, and searches for anchors."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read().lower()
            
            found_anchors = []
            for anchor in ANCHORS:
                if anchor in content:
                    found_anchors.append(anchor.decode('utf-8', errors='ignore'))
            
            return found_anchors
    except Exception as e:
        return f"Error reading file: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python binary_scanner.py <file_or_directory>")
        return

    target = sys.argv[1]
    flagged_files = []

    if os.path.isdir(target):
        files = [os.path.join(target, f) for f in os.listdir(target) 
                 if os.path.isfile(os.path.join(target, f))]
        print(f"Scanning directory: {target} ({len(files)} files found)")
    else:
        files = [target]

    for file_path in files:
        results = scan_file(file_path)
        if isinstance(results, list) and len(results) > 0:
            file_name = os.path.basename(file_path)
            flagged_files.append(file_name)
            
            print(f"\n[!] MATCH FOUND: {file_path}")
            print(f"    Detected Markers: {', '.join(results)}")
            
            # Special Logic for the 'cai' marker
            if len(results) == 1 and "cai" in results:
                print("    NOTE: 'cai' belongs to Adobe and is a marker left when an image is modified using Photoshop.")
                
        elif isinstance(results, str):
            print(f"[-] Skipping {file_path}: {results}")

    # Final Summary Output
    print(f"\n--- Scan Complete ---")
    print(f"Files flagged as AI-Generated: {len(flagged_files)}")
    
    for name in flagged_files:
        print(f'"{name}"')

    # Final Pro Tip Output
    print("\n" + "="*60)
    print("PRO TIP: Some markers (like 'adobe' or 'cai') may appear on real photos")
    print("that were simply edited in Photoshop. For high-confidence AI detection,")
    print("look for markers like 'trainedAlgorithmicMedia', 'prompt:', or 'c2pa'")
    print("in combination with vendor names (Google, OpenAI, etc.).")
    print("="*60)

if __name__ == "__main__":
    main()
