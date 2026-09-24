import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
from pypdf import PdfReader

# Konfigurasi Tampilan Halaman Streamlit
st.set_page_config(page_title="Petualangan Kuis Kurikulum Merdeka", page_icon="🎈", layout="centered")

# Styling CSS Sederhana
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

# Mengambil API Key dari Streamlit Secrets atau Sidebar Input
api_key = st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.header("⚙️ Pengaturan AI")
    if not api_key:
        api_key = st.text_input("Masukkan Gemini API Key:", type="password")
    else:
        st.success("API Key Terhubung Otomatis! 🔑")

# Inisialisasi Session State
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answered" not in st.session_state:
    st.session_state.answered = False

# Pilihan Sumber Belajar
input_option = st.radio(
    "📚 Pilih sumber materi belajar:",
    ["📸 Foto Gambar Modul", "📷 Scan Barcode / QR Code", "📄 File PDF Modul"],
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

user_instruction = st.text_input(
    "✏️ Instruksi Tambahan / Topik Khusus (Opsional):", 
    placeholder="Contoh: Fokus Penjumlahan atau Bab Tumbuhan IPAS"
)

# Proses Pembuatan Soal
if uploaded_file is not None:
    if file_type in ["image", "barcode"]:
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar / Barcode Materi", use_container_width=True)
    elif file_type == "pdf":
        st.info(f"📄 Berkas PDF terunggah: **{uploaded_file.name}**")

    if st.button("✨ Buat Petualangan Kuis Baru!"):
        if not api_key:
            st.error("Masukkan Gemini API Key di menu samping terlebih dahulu!")
        else:
            with st.spinner("AI sedang menganalisis materi & menyelaraskan dengan Kurikulum Merdeka... ⏳"):
                try:
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

                    prompt_base = f"""
                    Kamu adalah pakar pengembang soal edukasi anak SD berbasis KURIKULUM MERDEKA Indonesia yang ceria dan ramah.
                    Analisis materi/sumber pembelajaran ini dan buatkan 10 soal pilihan ganda interaktif.
                    {prompt_barcode}
                    {catatan_tambahan}

                    Ketentuan Utama:
                    1. Adaptasi Kurikulum Merdeka untuk anak SD.
                    2. Gunakan bahasa anak yang ramah, jelas, ceria, dan mudah dipahami.
                    3. Setiap soal wajib memiliki 4 pilihan jawaban (A, B, C, D).

                    Output HARUS berupa JSON murni berbentuk Array Object tanpa format markdown:
                    [
                      {{
                        "soal": "Pertanyaan kuis...",
                        "pilihan": ["Pilihan A", "Pilihan B", "Pilihan C", "Pilihan D"],
                        "jawaban_benar": "Pilihan A",
                        "pembahasan": "Penjelasan singkat jawaban..."
                      }}
                    ]
                    """

                    contents_payload = []

                    if file_type in ["image", "barcode"]:
                        img = Image.open(uploaded_file)
                        contents_payload = [img, prompt_base]

                    elif file_type == "pdf":
                        pdf_reader = PdfReader(uploaded_file)
                        pdf_text = ""
                        for page in pdf_reader.pages:
                            text = page.extract_text()
                            if text:
                                pdf_text += text + "\n"
                        
                        full_prompt = f"BERIKUT ADALAH TEKS MATERI DARI DOKUMEN PDF MODUL:\n\n{pdf_text[:15000]}\n\n{prompt_base}"
                        contents_payload = [full_prompt]

                    # PERBAIKAN PEMANGGILAN MODEL GEMINI
                    response = None
                    last_err = ""
                    
                    models_to_try = [
                        'gemini-1.5-flash',
                        'gemini-1.5-pro',
                        'gemini-2.0-flash-exp'
                    ]
                    
                    for model_name in models_to_try:
                        try:
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content(contents_payload)
                            if response and response.text:
                                break
                        except Exception as e:
                            last_err = str(e)

                    if not response or not response.text:
                        raise Exception(f"Gagal memproses dengan model Gemini. Detail: {last_err}")

                    raw_text = response.text.strip()
                    clean_text = raw_text
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

# Tampilan Antarmuka Kuis
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
            st.warning("🥉 TETAP SEMANGAT! Yuk latihan lagi supaya makin jago!")

        if st.button("🔄 Main Lagi dari Awal"):
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.rerun()
