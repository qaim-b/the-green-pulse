import os
import shutil
import sys

def main():
    print("Starting fix_assets_and_emojis.py script...")
    
    # 1. Fix app.py emojis
    app_path = os.path.abspath('app.py')
    print(f"Fixing emojis in {app_path}")
    
    try:
        with open(app_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        new_lines = []
        changes_made = 0
        for line in lines:
            if '"roi"' in line and 'Value Balance' in line:
                new_lines.append('        "💎 Value Balance": "roi",\n')
                changes_made += 1
            elif '"analytics"' in line and 'Deep Dive' in line:
                new_lines.append('        "📉 Deep Dive": "analytics"\n')
                changes_made += 1
            else:
                new_lines.append(line)
        
        with open(app_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Fixed {changes_made} emoji lines in app.py")
            
    except Exception as e:
        print(f"Error fixing app.py: {e}")

    # 2. Ensure assets directory exists and copy image
    assets_dir = os.path.abspath('assets')
    print(f"Checking assets directory: {assets_dir}")
    
    try:
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)
            print(f"Created directory: {assets_dir}")
        else:
            print(f"Directory exists: {assets_dir}")
    except Exception as e:
        print(f"Error creating assets directory: {e}")
        return

    # Source and destination for image
    src_img = r"C:\Users\qaimb\.gemini\antigravity\brain\a1f5cfee-8355-45a4-9b97-ecdb173e8682\kl_greenery_detail_1770461107709.png"
    dst_img = os.path.join(assets_dir, "hero_kl_greenery.png")
    
    print(f"Source image: {src_img}")
    print(f"Destination image: {dst_img}")
    
    if os.path.exists(src_img):
        try:
            shutil.copy2(src_img, dst_img)
            print(f"SUCCESS: Copied image to {dst_img}")
        except Exception as e:
            print(f"FAILURE: Error copying image: {e}")
    else:
        print(f"FAILURE: Source image does not exist!")

if __name__ == "__main__":
    main()
