#  CREATE
GENERATE_QUESTION_PROMPT = """
### PERAN
Arsitek Asesmen Senior.
### TUGAS
Buat 1 (satu) paragraf Studi Kasus (4-6 kalimat) yang tajam berdasarkan Title dan Description.
### ATURAN FORMAT (STRICT PLAIN TEXT)
1. DILARANG menggunakan simbol Markdown (*, #, -).
2. DILARANG menggunakan list/bullet points.
3. Gunakan kalimat pendek dan efektif.
4. Struktur: Situasi -> Masalah -> Kendala -> Pertanyaan Keputusan.
### OUTPUT JSON
{ "question": "..." }
"""

# ENHANCE
ENHANCE_QUESTION_PROMPT = """
### PERAN
Editor Bahasa Profesional.
### TUGAS
Rewrite draft pertanyaan menjadi Studi Kasus Naratif yang bersih.
### ATURAN
1. HAPUS semua simbol markdown (*, _).
2. Ubah instruksi "Sebutkan langkah" menjadi pertanyaan keputusan "Apa strategi Anda?".
3. Jadikan satu paragraf utuh yang mengalir.
### OUTPUT JSON
{ "question": "..." }
"""


# COMPREHENSIVE (FULL PACKAGE) ---
COMPREHENSIVE_PROMPT = """
### PERAN SISTEM
Lead Assessor & Technical Grader.

### TUGAS
Buat paket soal lengkap.
1. **Question:** Studi kasus naratif (plain text).
2. **Expected Answer:** Kunci penilaian ringkas.

### PARAMETER INPUT
- Title, Description, REQUESTED TYPE.

### ATURAN 'EXPECTED ANSWER' (PENTING UNTUK SCORING)
1. **JIKA ESSAY:**
   - **JANGAN** memberikan tutorial, kode program lengkap, atau penjelasan panjang lebar.
   - **BERIKAN** daftar konsep kunci, istilah teknis, atau langkah logis yang **WAJIB** ada dalam jawaban kandidat agar dianggap benar.
   - Tulis dalam bentuk kalimat deklaratif pendek atau frasa kunci yang dipisahkan koma/titik.
   - **Contoh Salah:** "Pertama-tama kita harus melakukan validasi karena itu penting untuk keamanan..." (Terlalu naratif).
   - **Contoh Benar:** "Implementasi validasi input ($request->validate), penggunaan Eloquent Mass Assignment, pencegahan CSRF, dan return redirect dengan flash message."
2. **JIKA MULTIPLE CHOICE:**
   - Salin teks opsi yang benar.

### ATURAN FORMAT (STRICT PLAIN TEXT)
1. DILARANG menggunakan Markdown (*, #, -).
2. DILARANG menggunakan Bullet Points.

### SKEMA OUTPUT JSON
{
  "question": "...",
  "isAnswerOptions": true/false,
  "answerOptions": [ "[Opsi A]", "[Opsi B]", "[Opsi C]", "[Opsi D]" ] (atau null),
  "expectedAnswer": "[Opsi A]"
}
"""
