import streamlit as st

st.title("🌟 Kuis Pintar Kelas 1 SD 🌟")
st.write("Yuk, jawab pertanyaan di bawah ini!")

st.subheader("1. Berapa hasil dari 7 + 5?")
j1 = st.radio("Pilih:", [10, 11, 12, 13], key="q1")

st.subheader("2. Suku kata awal kata 'Buku'?")
j2 = st.radio("Pilih:", ["Bu", "Ba", "Ku", "Bi"], key="q2")

if st.button("Selesai & Cek Nilai 🎉"):
    skor = (1 if j1 == 12 else 0) + (1 if j2 == "Bu" else 0)
    if skor == 2:
        st.success("Horeee! Jawabanmu BENAR SEMUA! 🎈")
        st.balloons()
    else:
        st.warning("Bagus! Coba periksa lagi ya!")