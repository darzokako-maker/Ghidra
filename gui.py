import customtkinter as ctk
from tkinter import filedialog
import os
import threading
import subprocess

# Arayüz Teması Ayarları
ctk.set_appearance_mode("Dark")       # Koyu Tema (Dark)
ctk.set_default_color_theme("blue")   # Mavi Vurgu Rengi

class AICrackerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Otonom Tersine Mühendislik ve Analiz İstasyonu")
        self.geometry("800x600")
        self.resizable(False, False)

        # ---- UI BİLEŞENLERİ ----
        # Ana Başlık
        self.title_label = ctk.CTkLabel(
            self, 
            text="⚙️ AI OTONOM IDA-STYLE CRACKER ASSISTANT", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(pady=20)

        # Dosya Seçim Paneli (Frame)
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=10, fill="x", padx=30)

        self.file_entry = ctk.CTkEntry(
            self.file_frame, 
            placeholder_text="Analiz edilecek uygulamayı (.exe, .dll, .py, .txt) seçin...", 
            width=500
        )
        self.file_entry.pack(side="left", padx=15, pady=15)

        self.browse_btn = ctk.CTkButton(
            self.file_frame, 
            text="📁 Dosya Seç", 
            width=120, 
            command=self.browse_file
        )
        self.browse_btn.pack(side="right", padx=15, pady=15)

        # AI Komut Giriş Paneli
        self.msg_label = ctk.CTkLabel(
            self, 
            text="💬 AI Otonom Hedefi ve Özel Talimat (Deney/Gözlem):",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.msg_label.pack(anchor="w", padx=35, pady=(10, 5))
        
        self.instruction_input = ctk.CTkTextbox(self, height=100, width=730, font=ctk.CTkFont(size=12))
        self.instruction_input.pack(pady=5)
        # Varsayılan güçlü talimat
        self.instruction_input.insert(
            "0.0", 
            "Bu uygulamanın şifre kontrol/lisans doğrulama fonksiyonunu bul, mantığını çöz ve programı başarıyla geçebilecek DOĞRU ŞİFREYİ tespit et."
        )

        # Tetikleme Butonu
        self.start_btn = ctk.CTkButton(
            self, 
            text="⚡ Otonom Analiz ve Deney Döngüsünü Başlat", 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1abc9c", 
            hover_color="#16a085", 
            height=45, 
            command=self.start_analysis_thread
        )
        self.start_btn.pack(pady=20)

        # Canlı Log Çıktı Paneli
        self.log_label = ctk.CTkLabel(
            self, 
            text="📊 Canlı Takip, Decompile ve Gözlem Logları:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.log_label.pack(anchor="w", padx=35)

        self.log_output = ctk.CTkTextbox(
            self, 
            height=200, 
            width=730, 
            fg_color="#111111", 
            text_color="#00ff00",
            font=ctk.CTkFont(family="Courier", size=12)
        )
        self.log_output.pack(pady=5)
        self.log(" Sitem Hazır. Lütfen analiz edilecek bir dosya seçip başlatın.")

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Tüm Dosyalar", "*.*"), 
                ("Uygulamalar", "*.exe;*.dll;*.so"), 
                ("Kaynak Kodlar", "*.py;*.cpp;*.cs;*.c")
            ]
        )
        if file_path:
            self.file_entry.delete(0, ctk.END)
            self.file_entry.insert(0, file_path)
            self.log(f"📁 Dosya Başarıyla Seçildi: {file_path}")

    def log(self, text):
        self.log_output.insert(ctk.END, text + "\n")
        self.log_output.see(ctk.END)

    def start_analysis_thread(self):
        # Arayüzün (GUI) işlem yaparken donmaması için arka plan thread'i açıyoruz
        threading.Thread(target=self.run_autonomous_loop, daemon=True).start()

    def run_autonomous_loop(self):
        target = self.file_entry.get().strip()
        instruction = self.instruction_input.get("1.0", ctk.END).strip()

        if not target or not os.path.exists(target):
            self.log("❌ Hata: Geçersiz dosya yolu! Lütfen önce geçerli bir uygulama seçin.")
            return

        self.log("\n[BAŞLATILDI] --- Otonom Süreç ve IDA Analiz Modu Aktif ---")
        self.start_btn.configure(state="disabled", text="🔄 Otonom Döngü Çalışıyor...", fg_color="#7f8c8d")

        try:
            # main.py motorunu alt işlem olarak çağırıp çıktıları canlı olarak GUI'ye basıyoruz
            cmd = f"python main.py \"{target}\" \"{instruction}\""
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            # Konsol çıktılarını satır satır CustomTkinter ekranına yönlendir
            for line in process.stdout:
                self.log(line.strip())
                
            process.wait()
            self.log("\n[TAMAMLANDI] ✅ Yapay zeka tüm deney ve gözlemlerini tamamladı.")
            self.log("📝 Detaylı analiz raporu proje klasöründeki 'ai_chat_report.md' dosyasına yazıldı.")
        except Exception as e:
            self.log(f"❌ Çalıştırma Hatası: {str(e)}")
        
        self.start_btn.configure(state="normal", text="⚡ Otonom Analiz ve Deney Döngüsünü Başlat", fg_color="#1abc9c")

if __name__ == "__main__":
    app = AICrackerGUI()
    app.mainloop()
          
