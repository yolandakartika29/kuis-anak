import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import tempfile
import os
import time
import urllib.parse

st.set_page_config(page_title="Petualangan Kuis Kurikulum Merdeka", page_icon="🎈", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f0f8ff; }
    .stButton>button {
        background-color: #ff6b6b;
        color: white;
        font-size: 18px;
        border-radius: 12px;
        padding: 10px 24px;
        border: none;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover { background-color: #ff5252; color: white; }
    .question-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #4ecdc4;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎈 Petualangan Kuis Kurikulum Merdeka 🎈")

api_key = st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.header("⚙️ Pengaturan AI")
    if not api_key:
        api_key = st.text_input("Masukkan Gemini API Key:", type="password")
    else:
        st.success("API Key Terhubung Otomatis! 🔑")

if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answered" not in st.session_state:
    st.session_state.answered = False

input_option = st.radio(
    "📚 Pilih sumber materi belajar:",
    ["📸 Foto Gambar Modul", "📷 Scan Barcode / QR Code", "📄 File PDF Modul", "🎥 Video / Audio Pembelajaran"],
    horizontal=True
)

uploaded_file = None
file_type = None

if input_option == "📸 Foto Gambar Modul":
    uploaded_file = st.file_uploader("Unggah foto modul/buku pelajaran:", type=["jpg", "jpeg", "png"])
    file_type = "image"
elif input_option == "📷 Scan Barcode / QR Code":
    uploaded_file = st.file_uploader("Unggah foto Barcode / QR Code dari buku:", type=["jpg", "jpeg", "png"])
    file_type = "barcode"
elif input_option == "📄 File PDF Modul":
    uploaded_file = st.file_uploader("Unggah dokumen PDF modul:", type=["pdf"])
    file_type = "pdf"
elif input_option == "🎥 Video / Audio Pembelajaran":
    uploaded_file = st.file_uploader("Unggah file video atau audio pembelajaran:", type=["mp4", "mov", "avi", "m4v", "mp3", "wav"])
    file_type = "media"

user_instruction = st.text_input(
    "✏️ Instruksi Tambahan / Topik Khusus (Opsional):", 
    placeholder="Contoh: Fokus Penjumlahan atau Bab Tumbuhan IPAS"
)

if uploaded_file is not None:
    if file_type in ["image", "barcode"]:
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar / Barcode Materi", use_container_width=True)
    elif file_type == "pdf":
        st.info(f"📄 Berkas PDF terunggah: **{uploaded_file.name}**")
    elif file_type == "media":
        if uploaded_file.name.lower().endswith(('.mp4', '.mov', '.avi', '.m4v')):
            st.video(uploaded_file)
        else:
            st.audio(uploaded_file)

    if st.button("✨ Buat Petualangan Kuis Baru!"):
        if not api_key:
            st.error("Masukkan Gemini API Key di menu samping terlebih dahulu!")
        else:
            with st.spinner("AI sedang menganalisis materi & menyelaraskan dengan Kurikulum Merdeka... ⏳"):
                try:
                    # Konfigurasi API Key
                    genai.configure(api_key=api_key.strip())

                    catatan_tambahan = ""
                    if user_instruction.strip():
                        catatan_tambahan = f"\nINSTRUKSI KHUSUS PENGGUNA: {user_instruction.strip()}"

                    prompt_barcode = ""
                    if file_type == "barcode":
                        prompt_barcode = """
                        PERHATIAN: Gambar yang diunggah adalah BARCODE / QR CODE materi pelajaran.
                        1. Lakukan ekstraksi dan pembacaan teks/link/informasi yang terkandung dalam Barcode/QR Code tersebut.
                        2. Gunakan informasi materi di dalam barcode tersebut sebagai bahan utama pembuatan kuis.
                        """

                    prompt = f"""
                    Kamu adalah pakar pengembang soal edukasi anak SD berbasis KURIKULUM MERDEKA Indonesia yang sangat ceria, inspiratif, dan interaktif.
                    Analisis materi/sumber pembelajaran yang diunggah ini dan buatkan 10 soal pilihan ganda interaktif.
                    {prompt_barcode}
                    {catatan_tambahan}

                    Ketentuan Utama & Kurikulum Merdeka:
                    1. Adaptasi Capaian Pembelajaran (CP) Kurikulum Merdeka untuk SD (Pancasila, Bahasa Indonesia, Matematika, IPAS, atau Seni).
                    2. Buatlah soal berorientasi pada visual & kehidupan sehari-hari anak (kontekstual).
                    3. ATURAN PENULISAN PROMPT GAMBAR (`prompt_gambar_en`):
                       - Harus berupa deskripsi objek konkret, spesifik, dan SANGAT SESUAI dengan konteks soal.
                       - Jangan menggunakan simbol seperti "+", "=" langsung. Gunakan kata lengkap seperti "plus symbol sign", "equals symbol sign", "three red apples", "green tree leaf".
                       - Contoh Baik: "A big colorful equals sign symbol '=' on a clean background" atau "A cartoon illustration of three red apples next to two green apples".
                    4. Gunakan bahasa anak yang ramah, jelas, ceria, dan mudah dipahami usia SD.
                    5. Setiap soal wajib memiliki 4 pilihan jawaban (A, B, C, D).

                    Output HARUS berupa JSON murni berbentuk Array Object tanpa format markdown:
                    [
                      {{
                        "soal": "Perhatikan gambar berikut! Simbol apakah yang kita pakai untuk menunjukkan hasil akhir dari sebuah penjumlahan?",
                        "prompt_gambar_en": "a bright yellow equals symbol sign, 3d cute style, centered",
                        "pilihan": ["Pilihan A (+)", "Pilihan B (-)", "Pilihan C (=)", "Pilihan D (x)"],
                        "jawaban_benar": "Pilihan C (=)",
                        "pembahasan": "Simbol sama dengan (=) digunakan untuk menunjukkan hasil akhir dari penjumlahan!"
                      }}
                    ]
                    """

                    if file_type in ["image", "barcode"]:
                        image_input = Image.open(uploaded_file)
                        contents_payload = [image_input, prompt]
                    else:
                        suffix = os.path.splitext(uploaded_file.name)[1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name

                        st.write("🔄 Mengunggah berkas ke server AI...")
                        uploaded_media = genai.upload_file(path=tmp_path)
                        
                        while uploaded_media.state.name == "PROCESSING":
                            time.sleep(2)
                            uploaded_media = genai.get_file(name=uploaded_media.name)

                        contents_payload = [uploaded_media, prompt]

                    candidate_models = [
                        "gemini-1.5-flash",
                        "gemini-1.5-pro",
                        "gemini-2.0-flash-exp"
                    ]

                    response = None
                    last_error = None

                    for mod in candidate_models:
                        try:
                            model_instance = genai.GenerativeModel(mod)
                            response = model_instance.generate_content(contents_payload)
                            if response and response.text:
                                break
                        except Exception as e_mod:
                            last_error = e_mod
                            continue

                    if response is None or not response.text:
                        raise last_error if last_error else Exception("Koneksi ke server AI gagal.")

                    if 'tmp_path' in locals() and os.path.exists(tmp_path):
                        os.remove(tmp_path)

                    clean_text = response.text.strip()
                    if "[" in clean_text and "]" in clean_text:
                        clean_text = clean_text[clean_text.find("["):clean_text.rfind("]")+1]

                    soal_list = json.loads(clean_text)
                    
                    st.session_state.soal_ai = soal_list
                    st.session_state.current_q = 0
                    st.session_state.score = 0
                    st.session_state.answered = False
                    st.success("Hore! Soal kuis Kurikulum Merdeka siap dimainkan! 🎉")

                except Exception as e:
                    st.error(f"Gagal membuat soal: {e}")

if "soal_ai" in st.session_state and len(st.session_state.soal_ai) > 0:
    soal_data = st.session_state.soal_ai
    idx = st.session_state.current_q
    total = len(soal_data)

    st.write("---")
    
    if idx < total:
        progress = (idx + 1) / total
        st.progress(progress)
        st.caption(f"🌟 Soal No. {idx + 1} dari {total}")

        item = soal_data[idx]

        if "prompt_gambar_en" in item and item["prompt_gambar_en"]:
            clean_prompt = item['prompt_gambar_en'].replace("+", "plus").replace("=", "equals")
            prompt_encoded = urllib.parse.quote(f"educational illustration of {clean_prompt}, 3d cartoon style, clear isolated subject, vivid colors")
            image_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=600&height=400&nologo=true"
            
            st.image(image_url, caption="🖼️ Perhatikan Gambar Ilustrasi di Atas!", use_container_width=True)

        st.markdown(f"""
        <div class="question-card">
            <h3>{item['soal']}</h3>
        </div>
        """, unsafe_allow_html=True)

        user_choice = st.radio("Pilih jawabanmu:", item["pilihan"], key=f"q_radio_{idx}")

        if not st.session_state.answered:
            if st.button("Jawab Sekarang! 🎯"):
                st.session_state.answered = True
                if user_choice == item["jawaban_benar"]:
                    st.session_state.score += 1
                    st.success("🎉 HEBAT! Jawabanmu BENAR SEKALI! 🌟")
                    st.balloons()
                else:
                    st.error(f"💡 Kurang tepat! Jawaban yang benar adalah: **{item['jawaban_benar']}**")
                st.rerun()
        else:
            if user_choice == item["jawaban_benar"]:
                st.success("🎉 Jawabanmu Benar!")
            else:
                st.error(f"💡 Jawaban yang benar: **{item['jawaban_benar']}**")
            
            if "pembahasan" in item and item["pembahasan"]:
                st.info(f"💬 **Pembahasan Ringkas:** {item['pembahasan']}")

            if st.button("Soal Selanjutnya ➡️"):
                st.session_state.current_q += 1
                st.session_state.answered = False
                st.rerun()

    else:
        st.balloons()
        st.snow()
        
        nilai_akhir = int((st.session_state.score / total) * 100)
        
        st.markdown(f"""
        <div style="text-align: center; background-color: #ffffff; padding: 30px; border-radius: 20px; box-shadow: 0px 4px 15px rgba(0,0,0,0.1);">
            <h1>🏆 PETUALANGAN SELESAI! 🏆</h1>
            <h2>Total Skor Kamu: <span style="color: #ff6b6b;">{nilai_akhir} / 100</span></h2>
            <p style="font-size: 20px;">Kamu berhasil menjawab <b>{st.session_state.score}</b> dari <b>{total}</b> soal dengan benar!</p>
        </div>
        """, unsafe_allow_html=True)

        if nilai_akhir == 100:
            st.success("🥇 LUAR BIASA! Kamu dapat Bintang Emas Kurikulum Merdeka 🌟🌟🌟🌟🌟!")
        elif nilai_akhir >= 70:
            st.info("🥈 BAGUS SEKALI! Kamu anak yang pintar dan rajin! 👏")
        else:
            st.warning("🥉 TETAP SEMANGAT! Yuk latihan lagi supaya makin jago! 💪")

        if st.button("🔄 Main Lagi dari Awal"):
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.rerun()
