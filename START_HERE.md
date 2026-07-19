# MULAI DI SINI -- baca file ini DULU, jangan langsung ke PROJECT_STATUS.md

Project: Aplikasi Android offline "Setting Relay Proteksi GH United Power".
Python + Kivy 2.3.1 + Buildozer 1.6.0, dibuild via Termux (proot-Ubuntu),
tanpa PC/Android Studio sama sekali.

STATUS SEKARANG: Tahap 9B (fitur UI) hampir selesai -- navigasi, search,
edit relay, tambah GH, hapus GH semua SUDAH ada & terkonfirmasi jalan
(minimal "import tanpa error" -- lihat catatan display di bawah).
Yang BELUM: dark mode + palet warna terpusat + polish akhir.

## ATURAN WAJIB SEBELUM BERTINDAK
1. JANGAN audit ulang seluruh riwayat, skema, atau keputusan desain di
   PROJECT_STATUS.md. Anggap SEMUA yang ditandai [SELESAI+KONFIRMASI] di
   sana itu benar dan teruji -- TIDAK PERLU diverifikasi ulang.
2. Kerjakan HANYA "NEXT ACTION" di bawah. Kalau berhasil & user bilang
   lanjut, BARU buka PROJECT_STATUS.md bagian "LANGKAH SELANJUTNYA" utk
   tahu apa berikutnya -- jangan baca dari atas ke bawah.
3. Butuh detail teknis spesifik (isi tabel, kenapa suatu keputusan
   diambil)? Cari pakai grep/Ctrl+F nama fungsi/tabelnya di
   PROJECT_STATUS.md, JANGAN dibaca utuh.
4. User TIDAK punya display (Termux tanpa X11, ditolak sengaja). Kode
   Kivy TIDAK BISA dites visual sampai APK sungguhan ter-install (Tahap
   13). Satu-satunya tes yg mungkin sebelum itu: `python3 main.py` harus
   berhenti PERSIS di error "Unable to get a Window" -- itu tandanya
   semua modul ke-import benar, BUKAN bug.
5. Kalau user cuma bilang "Lanjut" (tanpa tempel error) setelah diminta
   menjalankan sesuatu, itu SUDAH BERARTI dia coba & berhasil. Jangan
   minta konfirmasi ulang.

## NEXT ACTION
Buat `config/theme.py` (palet warna light/dark terpusat) + deteksi dark
mode Android via pyjnius (`PythonActivity.mActivity` +
`Configuration.UI_MODE_NIGHT_MASK`, fallback ke light kalau gagal deteksi
-- pola API sudah diverifikasi lewat web search, lihat detail di
PROJECT_STATUS.md poin 9 kalau perlu), lalu refactor SEMUA warna
hardcoded (angka RGB langsung) di widgets/relay_card.py dan
screens/*.py supaya pakai `COLORS[...]` dari theme.py. Kemungkinan besar
perlu dipecah jadi beberapa kiriman (banyak file kesentuh).

## KALAU NEXT ACTION DI ATAS SUKSES
Lanjut Tahap 10-11 (testing/debugging -- realistisnya terbatas krn belum
ada display), lalu Tahap 12 (isi buildozer.spec, build APK sungguhan --
verifikasi visual PERTAMA KALI utk seluruh UI sejak awal Tahap 9).
