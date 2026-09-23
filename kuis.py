import streamlit as st
from google import genai
from PIL import Image
import json

st.set_page_config(page_title="Kuis Petualangan Anak", page_icon="🎈", layout="centered")

# Styling CSS khusus agar tampilan lebih ceria dan mirip game edukasi
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

st.title("🎈 Petualangan Kuis Pintar 🎈")

# Ambil API Key otomatis dari Secrets Streamlit jika ada
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

# Unggah Foto Modul
uploaded_file = st.file_uploader("📸 Upload foto modul/buku pelajaran di sini:", type=["jpg", "jpeg", "png"])

# Fitur Catatan / Instruksi Tambahan Pilihan Pengguna
user_instruction = st.text_input(
    "✏️ Instruksi Tambahan (Opsional):", 
    placeholder="Contoh: Fokus latihan soal sila pertama sampai kelima"
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Foto Modul Belajar", use_container_width=True)

    if st.button("✨ Buat Petualangan Kuis Baru!"):
        if not api_key:
            st.error("Masukkan Gemini API Key di menu samping terlebih dahulu!")
        else:
            with st.spinner("AI sedang menyiapkan petualangan soal yang seru... ⏳"):
                try:
                    client = genai.Client(api_key=api_key)

                    # Menambahkan instruksi tambahan pengguna jika diisi
                    catatan_tambahan = ""
                    if user_instruction.strip():
                        catatan_tambahan = f"\nINSTRUKSI KHUSUS PENGGUNA: {user_instruction.strip()}"

                    prompt = f"""
                    Kamu adalah pembuat game edukasi anak SD kelas 1 yang sangat ceria dan kreatif.
                    Analisis foto modul belajar ini dan buatkan 10 soal pilihan ganda interaktif.
                    {catatan_tambahan}

                    Ketentuan Khusus:
                    1. Gunakan bahasa yang sangat ramah, ceria, dan singkat untuk anak usia 6-7 tahun.
                    2. Sertakan emoji visual yang sesuai di dalam teks soal (misal: 🍎, ✏️, 🚗, 🐱, 🇮🇩) agar soal menarik dilihat.
                    3. Setiap soal wajib memiliki 4 pilihan jawaban (A, B, C, D).
                    4. Jika ada instruksi khusus pengguna di atas, utamakan topik atau fokus latihan yang diminta tersebut.

                    Format Output Wajib JSON Valid (Tanpa Markdown/```json):
                    [
                      {{
                        "soal": "Teks soal dengan emoji menarik...",
                        "pilihan": ["Pilihan A", "Pilihan B", "Pilihan C", "Pilihan D"],
                        "jawaban_benar": "Pilihan A",
                        "pembahasan": "Pesan semangat singkat!"
                      }}
                    ]
                    """

                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=[image, prompt]
                    )

                    clean_text = response.text.strip().replace("
