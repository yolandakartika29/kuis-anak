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

# Sidebar Pengaturan
with st.sidebar:
    st.header("⚙️ Pengaturan AI")
    api_key = st.text_input("Masukkan Gemini API Key:", type="password")

# Inisialisasi State Aplikasi
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answered" not in st.session_state:
    st.session_state.answered = False

# Unggah Foto Modul
uploaded_file = st.file_uploader("📸 Upload foto modul/buku pelajaran di sini:", type=["jpg", "jpeg", "png"])

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

                    prompt = """
                    Kamu adalah pembuat game edukasi anak SD kelas 1 yang sangat ceria dan kreatif.
                    Analisis foto modul belajar ini dan buatkan 10 soal pilihan ganda interaktif.

                    Ketentuan Khusus:
                    1. Gunakan bahasa yang sangat ramah, ceria, dan singkat untuk anak usia 6-7 tahun.
                    2. Sertakan emoji visual yang sesuai di dalam teks soal (misal: 🍎, ✏️, 🚗, 🐱) agar soal menarik dilihat.
                    3. Setiap soal wajib memiliki 4 pilihan jawaban (A, B, C, D).

                    Format Output Wajib JSON Valid (Tanpa Markdown/```json):
                    [
                      {
                        "soal": "Teks soal dengan emoji menarik...",
                        "pilihan": ["Pilihan A", "Pilihan B", "Pilihan C", "Pilihan D"],
                        "jawaban_benar": "Pilihan A",
                        "pembahasan": "Pesan semangat singkat!"
                      }
                    ]
                    """

                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=[image, prompt]
                    )

                    clean_text = response.text.strip().replace("```json", "").replace("```", "")
                    soal_list = json.loads(clean_text)
                    
                    # Reset game state
                    st.session_state.soal_ai = soal_list
                    st.session_state.current_q = 0
                    st.session_state.score = 0
                    st.session_state.answered = False
                    st.success("Hore! Soal kuis baru siap dimainkan! 🎉")

                except Exception as e:
                    st.error(f"Gagal membuat soal: {e}")

# ==================== TAMPILAN GAME PER NOMOR ====================
if "soal_ai" in st.session_state and len(st.session_state.soal_ai) > 0:
    soal_data = st.session_state.soal_ai
    idx = st.session_state.current_q
    total = len(soal_data)

    st.write("---")
    
    # Jika masih ada soal yang harus dikerjakan
    if idx < total:
        # Progress Bar
        progress = (idx + 1) / total
        st.progress(progress)
        st.caption(f"🌟 Soal No. {idx + 1} dari {total}")

        item = soal_data[idx]

        # Kartu Soal
        st.markdown(f"""
        <div class="question-card">
            <h3>{item['soal']}</h3>
        </div>
        """, unsafe_allow_html=True)

        # Pilihan Jawaban
        user_choice = st.radio("Pilih jawabanmu:", item["pilihan"], key=f"q_radio_{idx}")

        # Tombol Jawab / Kunci Jawaban
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
            # Umpan balik setelah dijawab
            if user_choice == item["jawaban_benar"]:
                st.success("🎉 Jawabanmu Benar!")
            else:
                st.error(f"💡 Jawaban yang benar: **{item['jawaban_benar']}**")

            # Tombol Lanjut ke Soal Berikutnya
            if st.button("Soal Selanjutnya ➡️"):
                st.session_state.current_q += 1
                st.session_state.answered = False
                st.rerun()

    # ==================== HALAMAN AKHIR / HASIL SKOR ====================
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
            st.success("🥇 LUAR BIASA! Kamu dapat Bintang Emas 🌟🌟🌟🌟🌟!")
        elif nilai_akhir >= 70:
            st.info("🥈 BAGGUS SEKALI! Kamu anak yang pintar dan rajin! 👏")
        else:
            st.warning("🥉 TETAP SEMANGAT! Yuk latihan lagi supaya makin jago! 💪")

        if st.button("🔄 Main Lagi dari Awal"):
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.rerun()
