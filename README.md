# 📡 Mô phỏng Phương trình sóng 2D & Tối ưu hóa vị trí Wi-Fi
## 🛠 Yêu cầu hệ thống
- **Python:** Phiên bản 3.8 trở lên.
- **IDE khuyên dùng:** Visual Studio Code (VS Code).
- **Git:** Để clone source code.

Mở Terminal trong VS Code và chạy lệnh:
```bash
git clone <đường-link-github-của-repo-này>
cd <tên-thư-mục-chứa-repo>

# Tạo môi trường ảo (có thể skip qua cài thư viện luôn)
# Dành cho Windows
python -m venv venv

# Dành cho macOS/Linux
python3 -m venv venv

# Dành cho Windows (Command Prompt)
venv\Scripts\activate.bat

# Dành cho Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Dành cho macOS/Linux
source venv/bin/activate

# Cài thư viện
pip install -r requirements.txt

#Chạy chương trình
python main.py