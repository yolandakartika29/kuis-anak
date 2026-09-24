import streamlit as st
from google import genai
from PIL import Image
import json
import tempfile
import os
import time

st.set_page_config(page_title="Ayo Zee selesaikan soalnya, kamu kan pintar!", page_icon="🎈", layout="centered")

# Custom Styling untuk tampilan game interaktif anak
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

st.title("🎈 Ayo Zee selesaikan soalnya, kamu kan pintar! 🎈")

# Ambil API Key otomatis dari Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")

# Sidebar Pengaturan
with st.sidebar:
    st.header("⚙️ Pengaturan AI")
    if not api_key:
        api_key = st.text_input("Masukkan Gemini API Key:", type="password")
    else:
        st.success("API Key Terhubung Otomatis! 🔑")

# Inisialisasi State Aplikasi
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answered" not in st.session_state:
    st.session_state.answered = False

# Pilih Tipe Sumber Materi
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

# Fitur Catatan / Instruksi Tambahan Pilihan Pengguna
user_instruction = st.text_input(
    "✏️ Instruksi Tambahan / Topik Khusus (Opsional):", 
    placeholder="Contoh: Fokus Pancasila Sila ke-1 sampai ke-5 atau Bab Tumbuhan IPAS"
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
                    client = genai.Client(api_key=api_key)

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
                    3. Setiap soal HARUS menyertakan "prompt_gambar_en" berupa deskripsi visual singkat dalam Bahasa Inggris yang jelas untuk dijadikan masukan pembuatan gambar AI (Misal: "A colorful cartoon illustration of two yellow cards, the first card has a large plus sign and the second has an equals sign, vector art for kids").
                    4. Gunakan bahasa anak yang ramah, jelas, ceria, dan mudah dipahami usia SD.
                    5. Setiap soal wajib memiliki 4 pilihan jawaban (A, B, C, D).

                    Output HARUS berupa JSON murni berbentuk Array Object tanpa format markdown:
                    [
                      {{
                        "soal": "Perhatikan gambar berikut! Simbol manakah yang digunakan untuk penjumlahan?",
                        "prompt_gambar_en": "Two yellow cards, one with a large plus symbol and one with an equals symbol, cute cartoon style for children",
                        "pilihan": ["Pilihan A (+)", "Pilihan B (-)", "Pilihan C (=)", "Pilihan D (x)"],
                        "jawaban_benar": "Pilihan A (+)",
                        "pembahasan": "Simbol tambah (+) digunakan untuk menjumlahkan kelompok benda!"
                      }}
                    ]
                    """

                    # Penanganan Konten berdasarkan Tipe File
                    if file_type in ["image", "barcode"]:
                        image_input = Image.open(uploaded_file)
                        contents_payload = [image_input, prompt]
                    else:
                        suffix = os.path.splitext(uploaded_file.name)[1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name

                        st.write("🔄 Mengunggah berkas ke server AI...")
                        uploaded_media = client.files.upload(file=tmp_path)
                        
                        while uploaded_media.state.name == "PROCESSING":
                            time.sleep(2)
                            uploaded_media = client.files.get(name=uploaded_media.name)

                        contents_payload = [uploaded_media, prompt]

                    # Multi-model fallback untuk mengantisipasi error 503
                    models_to_try = ["gemini-1.5-flash", "gemini-2.5-flash", "gemini-3.6-flash"]
                    response = None
                    last_exception = None

                    for model_name in models_to_try:
                        try:
                            response = client.models.generate_content(
                                model=model_name,
                                contents=contents_payload
                            )
                            if response and response.text:
                                break
                        except Exception as err:
                            last_exception = err
                            time.sleep(1)
                            continue

                    if response is None or not response.text:
                        raise last_exception if last_exception else Exception("Gagal mendapat respon dari model AI.")

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
                    st.error(f"Gagal membuat soal: {e}. Silakan coba klik tombol sekali lagi!")

# ==================== TAMPILAN GAME PER NOMOR ====================
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

        # Pembuatan dan Penampilan Gambar Visual Otomatis via AI
        if "prompt_gambar_en" in item and item["prompt_gambar_en"]:
            # Menggunakan Gambar Unsplash Edukasi atau Ilustrasi Berdasar Kata Kunci Soal
            keywords = item["prompt_gambar_en"].replace(" ", ",")
            image_url = f"https://source.unsplash.com/600x400/?{keywords}"
            
            # Tampilkan Gambar Ilustrasi Visual Nyata
            st.image(image_url, caption="🖼️ Perhatikan Gambar di Atas!", use_container_width=True)

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

    # ==================== HASIL SKOR ====================
    else:
        st.balloons()
        st.snow()
        
        nilai_akhir = int((st.session_state.score / total) * 100)
        
        st.markdown(f"""
        <div style="text-align: center; background-color: #ffffff; padding: 30px; border-radius: 20px; box-shadow: 0px 4px 15px rgba(0,0,0,0.1);">
            <h1>🏆 PETUALANGAN SELESAI! KAMU PINTAR SEKALI ZEE! 🏆</h1>
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
