# DexFileManager 📂

**Automatic File Organizer**
Stop wasting time organizing your downloads manually. DexFileManager categorizes your files instantly.

## 🔥 Why?
- **Paling sering viral** (Highly requested feature)
- Everyone has a messy Downloads folder.
- **Clone → Run → Done.**

## 🚀 Features
- **Auto-Organize**: Sorts by Extension (default) or Date.
- **Dry-Run**: Preview what will happen before moving files.
- **Watch Mode**: Run in the background and organize incoming files automatically.
- **Safe**: Handles duplicate filenames automatically (e.g., `file.txt` -> `file_1.txt`).
- **Customizable**: simple `config.yaml` to change mappings.

## 🛠️ Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/dexpie/DexFileManager.git
   cd DexFileManager
   ```

2. **Install requirements**
   ```bash
   pip install -r requirements.txt
   ```

## 🏃 Usage

### 1. Basic Run (Organize local folder)
```bash
python main.py
```

### 2. Organize Specific Folder
```bash
python main.py --source "C:/Users/You/Downloads"
```

### 3. Dry Run (Simulation)
See what *would* happen without moving files:
```bash
python main.py --source "C:/Users/You/Downloads" --dry-run
```

### 4. Watch Mode (Keep running)
Keep the script running and organize files as they arrive:
```bash
python main.py --source "C:/Users/You/Downloads" --watch
```

### 5. Organize by Date
Sorts into folders like `2025-12`, `2025-01`:
```bash
python main.py --strategy date
```

## ⚙️ Configuration
Edit `config.yaml` to add more extensions or change folder names.

```yaml
mappings:
  Images: [jpg, png, gif]
  Docs: [pdf, docx]
```
