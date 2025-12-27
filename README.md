# DexFileManager 📂

**Automatic File Organizer**
Stop wasting time organizing your downloads manually. DexFileManager categorizes your files instantly.

## 🔥 Why?
- **Paling sering viral** (Highly requested feature)
- Everyone has a messy Downloads folder.
- **Clone → Run → Done.**

## 🚀 Features
- **Auto-Organize**: Sorts by Extension (default) or Date.
- **God Mode Dashboard**: 🖥️ Live terminal UI with real-time stats (via `rich`).
- **Time Traveller (Undo)**: ⏳ Oops? Reverses the last batch of moves instantly.
- **Mind Reader (Smart Rules)**: 🧠 Regex/Keyword matching to override defaults (e.g. "invoice" -> Finance).
- **Deep Dive (Recursive)**: 🤿 Scans inside subfolders to find every last file.
- **Black Hole**: 🕳️ Auto-deletes empty folders to keep it clean.
- **Duplicate Assassin**: 🔪 Smartly compares file hashes. Identical? **Deleted**. Different? Renamed.
- **The Butler**: 🔔 Sends desktop notifications when files are organized.
- **Dry-Run**: Preview what will happen safely.
- **Watch Mode**: Run in the background and organize incoming files automatically.
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
### 6. Undo (Time Traveller)
Made a mistake? Revert the last batch of moves:
```bash
python main.py --undo
```

### 7. Recursive Deep Scan
Organize files inside subfolders too:
```bash
python main.py --source "C:/Downloads" --recursive
```

## ⚙️ Configuration
### Smart Rules (Mind Reader)
Add regex or keywords in `config.yaml` to sort specific files:
```yaml
rules:
  - name: "Finance"
    keyword: "invoice"
  - name: "Screenshots"
    pattern: "^Screenshot.*"
```
Edit `config.yaml` to add more extensions or change folder names.

```yaml
mappings:
  Images: [jpg, png, gif]
  Docs: [pdf, docx]
```
