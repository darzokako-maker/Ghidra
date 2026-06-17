import os
import sys
import subprocess
from groq import Groq

def run_command(command):
    """Sistem komutlarını güvenli bir şekilde çalıştırır ve çıktısını döner."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=40)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return f"[Komut Hatası]: {str(e)}"

def ida_style_static_analysis(file_path):
    """IDA Pro veya Ghidra mantığıyla kritik kontrol noktalarını ve metinleri analiz eder."""
    analysis_log = []
    
    # 1. Kritik Kelimeleri ve Olası Şifreleri Taramak (Strings)
    analysis_log.append("🔍 [IDA MODE] Kritik bellek stringleri ve fonksiyon isimleri taranıyor...")
    strings_cmd = f"strings '{file_path}' | grep -E -i 'password|pass|key|auth|check|secret|flag|admin|login' | head -n 100"
    strings_res = run_command(strings_cmd)
    if strings_res.strip():
        analysis_log.append(f"Bulunan Kritik Kelimeler:\n{strings_res}\n")
    else:
        analysis_log.append("Metin tabanlı kritik kelime (strings) bulunamadı veya dosya düz metin.\n")

    # 2. Assembly Seviyesinde Karşılaştırma (CMP, TEST, JNE) Noktalarını Yakalama
    analysis_log.append("🛡️ [DISASSEMBLY MODE] Kritik Dallanma ve Karşılaştırma (cmp, test, je, jne|jz|jnz) Komutları Ayıklanıyor...")
    objdump_cmd = f"objdump -d -M intel '{file_path}' | grep -A 3 -E 'cmp|test|je|jne|jz|jnz' | head -n 150"
    objdump_res = run_command(objdump_cmd)
    if "objdump: command not found" not in objdump_res:
        analysis_log.append(f"Kritik Assembly Akış Noktaları:\n{objdump_res}\n")
    else:
        analysis_log.append("[Uyarı]: Bilgisayarda 'objdump' bulunamadı, assembly analizi atlandı.\n")

    # 3. .NET / C# için Üst Düzey Kod Analizi (ilspycmd)
    analysis_log.append("⚡ [DECOMPILE MODE] Üst düzey kontrol akış şeması üretiliyor...")
    decompile_res = run_command(f"ilspycmd '{file_path}' | grep -A 20 -E -i 'bool|string|check|verify|password' | head -n 200")
    if "ilspycmd: command not found" not in decompile_res and decompile_res.strip():
        analysis_log.append(f"Decompile Edilen Kritik Fonksiyon Blokları:\n{decompile_res}\n")
    else:
        analysis_log.append("Otomatik decompile çıktısı alınamadı veya dosya yerel (native) C/C++.\n")

    return "\n".join(analysis_log)

def main():
    # Verilen Groq API Anahtarı doğrudan koda entegre edildi
    STATIC_GROQ_API_KEY = "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"

    if len(sys.argv) < 3:
        print("Hata: Eksik parametre! Kullanım: python main.py <dosya_yolu> '<talimat>'")
        sys.exit(1)

    target_file = sys.argv[1]
    user_instruction = sys.argv[2]

    print(f"🚀 {target_file} için IDA Tarzı Gelişmiş Otonom Analiz Başlatıldı...")
    
    if not os.path.exists(target_file):
        print(f"❌ Hata: Belirtilen hedef dosya bulunamadı: {target_file}")
        sys.exit(1)

    # Dosya türüne göre ham veriyi veya decompile çıktısını hazırlama
    file_ext = os.path.splitext(target_file)[1].lower()
    if file_ext in ['.exe', '.dll', '.so', '.bin']:
        print("[Otonom Motor] Binary dosya analiz ediliyor...")
        extracted_data = ida_style_static_analysis(target_file)
    else:
        print("[Otonom Motor] Script/Düz metin dosyası okunuyor...")
        try:
            with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
                extracted_data = f.read(25000)
        except Exception as e:
            extracted_data = f"[Dosya okuma hatası]: {str(e)}"

    # Groq API İstemci Kurulumu (Gömülü anahtar kullanılıyor)
    client = Groq(api_key=STATIC_GROQ_API_KEY)
    
    system_prompt = (
        "Sen IDA Pro, Ghidra ve x64dbg araçlarıyla tam entegre çalışan, dünyanın en gelişmiş Yapay Zeka Tersine Mühendislik Uzmanısın. "
        "Görevin, sana sağlanan strings, assembly (cmp, test, jump) ve decompile kod yapılarını inceleyerek uygulamanın 'Kontrol Akış Şemasını' çıkarmaktır. "
        "Şifrenin, lisans anahtarının (key) veya aktivasyon kodunun kontrol edildiği tam algoritmayı deşifre et. "
        "Kullanıcının ne derse o uygulama üzerinde deney ve gözlem yapmasını sağla, matematiksel/mantıksal olarak DOĞRU GİRDİYİ/ŞİFREYİ kesin olarak bul."
    )

    agent_prompt = f"""
===================================================================
💾 IDA / GHIDRA TARZI OTOMATİK DECOMPILE VE AKIŞ VERİLERİ
===================================================================
{extracted_data}
===================================================================

🎯 KULLANICININ HEDEFİ / KOMUTU:
"{user_instruction}"

Senden İstenen Güçlü Analiz:
1. Uygulamanın şifre kilit mekanizmasını (XOR, MD5, Custom Matematiksel Döngü vb.) çöz ve mantığını açıkla.
2. Karşılaştırma yapılan kritik atlama (Jump) veya kontrol fonksiyonunu işaret et.
3. Deney ve gözlemlerine dayanarak, bu doğrulamayı başarıyla geçecek DOĞRU ŞİFREYİ tam olarak üret ve teslim et.
"""

    print(f"🧠 Groq (llama-3.3-70b-versatile) derin analiz moduna geçiyor...")
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": agent_prompt}
            ],
            temperature=0.1
        )
        
        ai_analysis = completion.choices[0].message.content
        print("\n📊 === OTONOM ANALİZ VE ŞİFRE TESPİT RAPORU ===\n")
        print(ai_analysis)
        print("\n================================================\n")

        # Raporlama
        with open("ai_chat_report.md", "w", encoding="utf-8") as r:
            r.write(f"# 🛡️ IDA Tarzı Otonom Analiz Raporu\n\n")
            r.write(f"- **Hedef Dosya:** {target_file}\n")
            r.write(f"- **Talimat:** {user_instruction}\n\n")
            r.write(f"## 🤖 Yapay Zeka Bulguları ve Çözüm\n{ai_analysis}")
            
        print("📝 Detaylı analiz raporu 'ai_chat_report.md' dosyasına kaydedildi.")
            
    except Exception as e:
        print(f"❌ Otonom analiz hatası: {e}")

if __name__ == "__main__":
    main()
