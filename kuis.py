import streamlit as st
from google import genai
from PIL import Image
import json

st.set_page_config(page_title="Kuis Pintar Anak SD", page_icon="🌟", layout="centered")

st.title("🌟 Kuis Pintar Kelas 1 SD 🌟")
st.write("Belajar jadi lebih seru dan menyenangkan!")

# Sidebar Pengaturan
with st.sidebar:
    st.header("⚙️ Pengaturan AI")
    api_key = st.text_input("Masukkan Gemini API Key:", type="password", help="Dapatkan API Key gratis di aistudio.google.com")
    st.info("API Key diperlukan untuk membaca foto modul secara otomatis.")

tab1, tab2 = st.tabs(["📸 Kuis dari Foto Modul", "✏️ Kuis Manual"])

# ==================== TAB 1: KUIS DARI FOTO SOAL ====================
with tab1:
    st.subheader("Unggah Foto Soal / Modul Belajar")
    uploaded_file = st.file_uploader("Pilih foto modul/buku (JPG / PNG):", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Foto Modul yang Diunggah", use_container_width=True)

        if st.button("✨ Buat 10 Soal Kuis dari Foto Ini"):
            if not api_key:
                st.error("Silakan masukkan Gemini API Key di sidebar sebelah kiri terlebih dahulu!")
            else:
                with st.spinner("AI sedang membaca modul dan meracik 10 soal kuis... ⏳"):
                    try:
                        client = genai.Client(api_key=api_key)

                        # PROMPT REVISI: Disesuaikan untuk anak Kelas 1 SD & meminta 10 soal
                        prompt = """
                        Kamu adalah asisten guru SD kelas 1 yang sangat ramah dan menyenangkan.
                        Analisis gambar/foto modul belajar yang diberikan dan buatkan tepat 10 soal kuis pilihan ganda.

                        Ketentuan Soal:
                        1. Bahasa harus singkat, jelas, ceria, dan sangat mudah dipahami anak usia 6-7 tahun (Kelas 1 SD).
                        2. Setiap soal memiliki 4 pilihan jawaban (A, B, C, D).
                        3. Pilihan jawaban harus realistis dan berkaitan langsung dengan isi gambar.

                        Kembalikan respon HANYA dalam format JSON valid tanpa format markdown tambahan seperti ```json.
                        Format JSON harus berupa list dari objek dengan struktur persis seperti ini:
                        [
                          {
                            "soal": "Pertanyaan soal...",
                            "pilihan": ["Pilihan A", "Pilihan B", "Pilihan C", "Pilihan D"],
                            "jawaban_benar": "Pilihan A"
                          }
                        ]
                        """

                        response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=[image, prompt]
                        )

                        clean_text = response.text.strip().replace("```json", "").replace("```", "")
                        soal_list = json.loads(clean_text)
                        st.session_state["soal_ai"] = soal_list
                        st.success("Berhasil membuat 10 soal kuis baru dari foto! 🎉")

                    except Exception as e:
                        st.error(f"Gagal memproses gambar: {e}")

    # Display Kuis AI
    if "soal_ai" in st.session_state:
        st.write("---")
        st.subheader("📝 Jawab 10 Soal di Bawah Ini:")
        
        jawaban_user = {}
        for idx, item in enumerate(st.session_state["soal_ai"]):
            st.markdown(f"**Soal {idx+1}: {item['soal']}**")
            jawaban_user[idx] = st.radio(
                "Pilih jawaban:", 
                item["pilihan"], 
                key=f"ai_q_{idx}"
            )

        if st.button("Selesai & Cek Nilai AI 🎉"):
            skor = 0
            total_soal = len(st.session_state["soal_ai"])
            
            for idx, item in enumerate(st.session_state["soal_ai"]):
                if jawaban_user[idx] == item["jawaban_benar"]:
                    skor += 1

            nilai_akhir = int((skor / total_soal) * 100)
            st.header(f"Nilai Kamu: {nilai_akhir} / 100")

            if nilai_akhir == 100:
                st.success("Horeee! Luar biasa, 10 soal BENAR SEMUA! 🎈🎈")
                st.balloons()
            elif nilai_akhir >= 70:
                st.info("Hebat sekali! Bagus nilainya, terus tingkatkan ya!")
            else:
                st.warning("Bagus sudah mencoba! Yuk pelajari lagi modulnya dan coba ulang!")


# ==================== TAB 2: KUIS MANUAL ====================
with tab2:
    st.subheader("Kuis Latihan Standar")
    
    st.write("1. Berapa hasil dari 7 + 5?")
    j1 = st.radio("Pilih jawaban:", [10, 11, 12, 13], key="m_q1")

    st.write("2. Suku kata awal dari kata 'Buku' adalah...")
    j2 = st.radio("Pilih jawaban:", ["Bu", "Ba", "Ku", "Bi"], key="m_q2")

    if st.button("Cek Nilai Kuis Manual"):
        skor_m = (1 if j1 == 12 else 0) + (1 if j2 == "Bu" else 0)
        if skor_m == 2:
            st.success("Hebat! Jawaban kuis manual benar semua! 🎈")
            st.balloons()
        else:
            st.warning("Ayo coba periksa lagi jawabannya!")
