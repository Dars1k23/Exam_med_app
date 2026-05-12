# Medical Exam System (Exam_med_app)

## Project Overview

This is a desktop application for conducting medical examinations, built with Python and **PyQt6**. It reads exam questions and sections from Excel files, conducts timed tests, performs proctoring (taking webcam shots and screenshots), and saves results back to Excel and as PDF reports.

### Main Technologies
- **UI Framework:** PyQt6
- **Data Handling:** `pandas`, `openpyxl` (reading/writing Excel files)
- **Reporting:** `fpdf2` (PDF generation)
- **Proctoring:** `opencv-python` (webcam), `pyautogui` (screenshots)

### Architecture
- **Entry Point:** `main.py`
- **UI Navigation:** Uses a `QStackedWidget` (`MainWindow` in `src/ui/main_window.py`) to sequentially navigate through 5 main screens:
  1. `CategoryScreen`: Select exam category.
  2. `LoginScreen`: Enter category-specific password.
  3. `NameScreen`: Validate student name (Regex).
  4. `TestScreen`: The main testing interface with a timer, questions, navigation panel, and background proctoring threads (`ProctorThread`, `WebcamThread`). Temporary state is saved to `tmp.txt` to prevent data loss.
  5. `ResultScreen`: Calculates the score, saves to Excel, generates a PDF, and allows logging out.
- **Core Logic:** Data loading and scoring logic reside in `src/core.py`. Utility functions and thread definitions are in `src/utils.py`.
- **Database Paths:** A newly added module `src/db_paths.py` parses database paths from a text file (`dataBasePath.txt`).

## Building and Running

### Prerequisites
Make sure you have Python installed and use the provided virtual environment.

```bash
# Activate the virtual environment
source .venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt
```

### Running the Application
```bash
python main.py
```

### Building Executables
There is a `build/` directory indicating that tools like PyInstaller might be used to bundle the application into an executable (`ExamApp.exe`), but no explicit build scripts are currently defined in the root.

## Development Conventions

- **UI Components:** Place new screens and UI components inside the `src/ui/` directory (`screens.py`, `widgets.py`).
- **Styling:** The application uses a unified dark theme defined in `src/ui/styles.py` (`DARK_QSS`). Adhere to these styles when creating new widgets.
- **Data Storage:** The application currently relies heavily on Excel files (`.xlsx`) in the `data/` directory for both reading questions/categories and writing results.
- **State Management:** Critical test state is saved iteratively to a temporary file (`tmp.txt`) to allow recovery in case of unexpected closure. Ensure any new test mechanics also update this temporary state.
- **Path Handling:** Use `pathlib.Path` for file system paths, as seen in the core and ui modules.