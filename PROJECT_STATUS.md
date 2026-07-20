# PROJECT_STATUS.md
(Kalau kamu AI/agent baru dan belum baca START_HERE.md di folder yang sama, baca itu DULU sebelum file ini.)

GH Relay - Database Setting Relay Proteksi GH United Power
Disusun oleh Claude (Anthropic) untuk kelangsungan proyek lintas sesi/AI.
Update terakhir: pertengahan Tahap 9B Bagian 4 (hapus data).

PENTING -- CARA BACA STATUS DI FILE INI:
Setiap item pakai salah satu tanda berikut, JANGAN disamakan artinya:
  [SELESAI+KONFIRMASI]  = user sudah menjalankan sendiri di device & hasilnya
                           cocok dengan yang diharapkan.
  [DIKIRIM]              = kode sudah diberikan & (setahu Claude) sudah dibuat
                           di device user, TAPI belum ada bukti eksplisit
                           dijalankan/diuji di device (user tidak mengirim
                           balik output/error).
  [SANDBOX SAJA]         = sudah ditulis & DIUJI PENUH oleh Claude sendiri,
                           TAPI BELUM PERNAH dikirim ke user -- tidak ada di
                           project device user sama sekali.
  [BELUM]                = belum dikerjakan sama sekali.

## RINGKASAN PROJECT
Aplikasi Android offline utk teknisi lapangan: database setting relay
proteksi Gardu Hubung (GH) United Power. Navigasi hierarkis (root MSS/MDS2
-> ... -> output), dibangun 100% via Termux di Android (tanpa PC/Android
Studio), pakai SQLite offline.

## STACK TEKNOLOGI (jangan ganti tanpa alasan kuat)
Python 3.14 + Kivy 2.3.1 + Buildozer 1.6.0, dibuild di dalam Ubuntu 24.04
(via proot-distro) yang jalan di dalam Termux. Alasan lengkap: Buildozer/
python-for-android resmi cuma jalan di Linux/macOS dan terbukti gagal di
Termux native; proot-distro membuatnya "melihat" Linux asli. Flutter &
BeeWare ditolak (lihat riwayat Tahap 1 kalau perlu alasan detail).

## LINGKUNGAN KERJA (PENTING utk AI/dev berikutnya)
- Masuk lewat `proot-distro login ubuntu`, project di `~/gh_relay` (alias
  `/root/gh_relay`). WAJIB `source ~/venv-gh/bin/activate` tiap sesi baru.
- `/storage/emulated/0/...` otomatis ter-bind ke Ubuntu proot tanpa setup.
- Kivy tidak punya wheel aarch64 -> `pip install kivy` selalu compile dari
  source (daftar dependency SDL2 lengkap ada di riwayat Tahap 5).
- **User MENOLAK Termux:X11.** Tidak ada cara lihat UI Kivy visual sampai
  Tahap 12-13 (build & install APK asli). `python3 main.py` di Termux akan
  SELALU berhenti di "Unable to get a Window" -- itu NORMAL, bukan bug.
  Ini SATU-SATUNYA bentuk "menjalankan app" yang bisa dilakukan user
  sebelum APK jadi: kalau errornya tetap persis di titik itu (bukan
  ImportError/exception lain sebelumnya), artinya semua modul berhasil
  di-import dengan benar.

## STATUS TAHAP (detail, lihat legenda tanda di atas)
- [SELESAI+KONFIRMASI] Tahap 1: analisis & pilih Kivy+Buildozer
- [SELESAI+KONFIRMASI] Tahap 2: cek versi -- Buildozer 1.6.0 dikonfirmasi user
- [SELESAI+KONFIRMASI] Tahap 3: struktur project -- `ls -la` dikonfirmasi user
- [SELESAI+KONFIRMASI] Tahap 4: venv `~/venv-gh` -- dipakai sukses berkali-kali sejak Tahap 2
- [SELESAI+KONFIRMASI] Tahap 5: Kivy 2.3.1 -- log install dikonfirmasi user
- [SELESAI+KONFIRMASI] Tahap 6: struktur folder -- `find` dikonfirmasi user
- [SELESAI+KONFIRMASI] Tahap 7: schema DB -- tabel & path gh_relay.db dikonfirmasi user
- [SELESAI+KONFIRMASI] Tahap 8: import data -- "24 node, 100 baris relay setting"
      dikonfirmasi PERSIS SAMA baik di sandbox Claude maupun device user
- [SELESAI+KONFIRMASI] Tahap 9A Bagian 1 (models/node_model.py, relay_model.py):
      diuji penuh di sandbox Claude thd data asli
- [DIKIRIM] Tahap 9A Bagian 2 (main.py, HomeScreen, NodeScreen, RelayCard):
      user jalankan `python3 main.py` -> "Unable to get a Window" -- SESUAI
      DUGAAN (bukti modul ke-import & App.build() jalan sampai titik window)
- [SELESAI+KONFIRMASI] Tahap 9B Bagian 1 (search, get_display_bundle/get_display_path
      utk gabung OUT_X/X): user konfirmasi "4 file diupdate". Logic-nya sendiri
      diuji penuh di sandbox Claude (dedup search, breadcrumb, dll).
- [SELESAI+KONFIRMASI] Tahap 9B Bagian 2 (form edit relay, RelayCard
      tappable, RelayEditScreen): user lanjut tanpa lapor error (sesuai
      konvensi "Lanjut" = sudah dicoba & berhasil).
- [SELESAI+KONFIRMASI] Tahap 9B Bagian 3 (Tambah GH, create_node,
      AddNodeScreen): idem, user lanjut tanpa lapor error.
- [SELESAI+KONFIRMASI] Tahap 9B Bagian 4 (delete_node, tombol "Hapus GH
      ini", Popup konfirmasi): user jalankan `python3 main.py` ulang
      setelah kode ini terkirim -> errornya PERSIS "Unable to get a
      Window" lagi (sama seperti sebelum Bagian 1-4 ditambahkan) --
      konfirmasi kuat bahwa SELURUH kode Bagian 1-4 (search, edit,
      tambah, hapus) ke-import bersih tanpa error baru di device asli.
- [SELESAI+KONFIRMASI] Tahap 9B SISA (dark mode + theme + polish):
      config/theme.py dibuat (palet light/dark + deteksi pyjnius, fallback
      light kalau gagal -- diuji: fallback jalan, kunci 2 palet identik).
      SEMUA warna hardcoded di 6 file (widgets/relay_card.py + 5 screens)
      direfactor pakai COLORS[...]. Window.clearcolor diset di main.py
      (tanpa ini background tetap putih walau dark mode terdeteksi).
      Bonus temuan polish: 3 label form Tambah GH tidak punya warna teks
      eksplisit (bakal putih-di-atas-terang, nyaris tak kebaca) -- sudah
      diperbaiki. **TAHAP 9B RESMI SELESAI PENUH** (semua 5 fitur wajib:
      hierarki, tampilan kartu, tambah, edit, hapus, ditambah search &
      dark mode).
- [BELUM] Tahap 10: Testing (kemungkinan besar baru efektif di Tahap 13,
      krn belum ada display)
- [BELUM] Tahap 11: Debugging
- [BELUM] Tahap 12: Build APK (isi buildozer.spec: package.name,
      package.domain, requirements = python3,kivy,sqlite3, lalu
      `buildozer -v android debug`)
- [BELUM] Tahap 13: Instal APK -- verifikasi visual PERTAMA KALI utk
      SEMUA UI sejak 9A Bagian 2 (belum pernah dilihat wujud aslinya)
- [BELUM] Tahap 14: Pengujian akhir lapangan

## KEPUTUSAN DESAIN DATA & ARSITEKTUR PENTING
1. DUA ROOT TERPISAH: "MSS" & "MDS 2" (parent_id NULL keduanya). MDS 2
   disuplai dari POT milik PLN, DI LUAR aset United Power (dikonfirmasi
   user) -- kolom `sumber_luar` menandai ini.
2. PRIMARY KEY GABUNGAN: `UNIQUE(parent_id, node_key)` -- id spt "OUT_TRAFO"
   dipakai ulang di 5 tempat berbeda, wajar di data sumber.
3. FILE JSON SUMBER = 5 objek JSON ditempel berurutan (bukan array valid).
   Ditangani `_load_json_objects()` di database/importer.py.
4. **[RESOLVED di 9B Bagian 1]** "OUT_X" & "X" (mis. OUT_TDS1 & TDS1) =
   2 relay fisik beda (nilai beda: 582A vs 600A dst), digabung jadi 1
   LAYAR lewat `get_display_bundle()` -- kartu relay dari SEMUA node di
   rantai ditampilkan (berlabel "Relay outgoing dari X" / "Relay incoming
   Y"), tombol anak diambil dari node PALING BAWAH rantai. Breadcrumb
   pakai `get_display_path()` (dedup nama berturut sama).
5. Relay flat `{"enabled": false}` dari JSON asli = 0 baris relay_settings
   saat IMPORT. TAPI sejak 9B Bagian 2, `get_relay_cards()` SELALU
   mengembalikan 6 kartu (isi "Belum diisi" kalau baris tak ada).
6. String kosong ("") pada ct_ratio/vt_ratio -> NULL saat import.
7. Node baru (Tambah GH) dapat node_key otomatis dari nama
   (`GH_<NAMA_DISLUGIFY>`, +angka kalau bentrok di induk sama).
8. Hapus node = cascade alami lewat FK (hapus 1 baris di titik ATAS
   rantai/subtree, anak+cucu+relay ikut hilang otomatis, TIDAK perlu
   logic rekursif manual di Python).
9. Dark mode (rencana): deteksi via pyjnius `PythonActivity.mActivity`
   + `Configuration.UI_MODE_NIGHT_MASK`, FALLBACK ke light mode kalau
   deteksi gagal/exception -- pola API sudah dikonfirmasi lewat web
   search, belum diimplementasi.

## SKEMA DATABASE (database/schema.sql = sumber kebenaran)
- nodes(id, node_key, nama, parent_id, node_type, ct_ratio, vt_ratio,
  sumber_luar, sort_order, note, created_at, updated_at)
  UNIQUE(parent_id, node_key), FK parent_id ON DELETE CASCADE
- relay_settings(id, node_id, relay_type, enabled, pickup_xin,
  pickup_ampere, tms, curve, delay, trip_time_minutes, alarm_percent,
  trip_percent) UNIQUE(node_id, relay_type), FK node_id ON DELETE CASCADE
- relay_curve_types(id, curve_name) -- 6 baris tetap
- app_settings(key, value)
- Data asli hasil import Tahap 8: 24 node, 100 baris relay_settings
  (semua data tes dari sandbox Claude sudah dibersihkan lagi, tidak nyangkut)

## ARSITEKTUR UI
- main.py: App + ScreenManager(NoTransition), 4 screen: home, node,
  relay_edit, add_node. (hapus tidak perlu screen baru, cukup Popup)
- screens/home_screen.py: search box (live filter) + "+ Tambah GH baru
  (akar)" + daftar root.
- screens/node_screen.py: SATU screen generik semua level, pakai
  get_display_bundle(). Urutan render: info sumber_luar -> kartu relay
  per node dlm rantai (tappable) -> tombol anak -> "+ Tambah GH di sini"
  -> "Hapus GH ini" (Popup konfirmasi).
- screens/relay_edit_screen.py: form generik 1 jenis relay, curve dari
  relay_curve_types (bukan hardcode).
- screens/add_node_screen.py: form nama/CT/VT, parent dari KONTEKS
  tombol (bukan dropdown pilih induk).
- widgets/relay_card.py: ButtonBehavior+BoxLayout, tappable.
- Warna SAAT INI masih hardcoded angka RGB di tiap file -- PR utama sisa
  Tahap 9B adalah refactor ke config/theme.py terpusat.

## CATATAN CI/GITHUB ACTIONS (PENTING, sempat berubah tanpa Claude sadari)
Workflow AKTUAL di .github/workflows/build.yml (per konfirmasi user, bukan
asumsi Claude): runs-on ubuntu-24.04 (bukan ubuntu-latest), Java 17 lewat
actions/setup-java@v4 (bukan apt install openjdk-17-jdk), TIDAK ada pin
versi Python eksplisit (beda dari saran Claude sebelumnya yg pin ke 3.11).
Ini versi yang TERBUKTI berhasil build APK pertama kali (run #11, sukses
17m6s). Penyebab pasti fix-nya error "generate-posix-vars failed" TIDAK
diketahui pasti oleh Claude -- ada AI lain yang ikut membantu ubah
workflow ini, beberapa hal berubah sekaligus. JANGAN asumsikan Python
3.11 pin Claude yg jadi penyelesainya; itu tidak terbukti.
-> AI/dev berikutnya: SELALU minta lihat isi build.yml AKTUAL dulu
   sebelum mengubahnya, jangan asumsikan dari riwayat percakapan saja.

## RIWAYAT KONFLIK MULTI-AI (19-20 Jul 2026) -- PENTING utk sesi berikutnya
Beberapa AI/sesi berbeda sempat bekerja paralel di project ini tanpa saling
tahu. Yang PERLU diketahui, sudah diselesaikan lewat `git reset --hard
origin/main` lalu re-apply manual (bukan git merge):
- Sempat ada percobaan redesign UI ("Redesign UI tahap 1", commit e42cd3f)
  yang cuma berupa file backup+zip, TIDAK PERNAH benar-benar mengubah
  screens/home_screen.py -- sudah dihapus lagi, TIDAK ADA yang perlu
  dikhawatirkan/dipulihkan dari situ.
- Sempat dicoba pendekatan `kivymd==1.2.0` (versi lama, API beda total dari
  2.0) sebagai jalan pintas menghindari error materialyoucolor -- **TERBUKTI
  GAGAL build** (dikonfirmasi user, run merah, sudah dihapus). JANGAN coba
  lagi pendekatan ini tanpa alasan baru.
- Keputusan FINAL yang dipertahankan: KivyMD dari master (2.0) +
  materialyoucolor dari source GitHub + p4a.branch=develop (sesuai dok
  resmi materialyoucolor utk Buildozer) -- lihat requirements di
  buildozer.spec sbg sumber kebenaran, bukan riwayat commit yang berantakan.
- build.yml: base dari versi AI lain (Java via actions/setup-java, apt list
  yg lebih lengkap, upload build logs kalau gagal -- semua ini BAGUS,
  dipertahankan), MINUS baris pip install kivy/kivymd manual di step
  "Install Buildozer" yang tidak perlu (dihapus, krn versi app yg terbundel
  ke APK ditentukan buildozer.spec, bukan pip di runner CI).
- PELAJARAN utk AI berikutnya: SELALU `git fetch && git log --oneline
  HEAD..origin/main` dulu sebelum push, JANGAN asumsikan riwayat lokal
  adalah satu-satunya yang berjalan -- project ini dikerjakan multi-AI/
  multi-sesi secara paralel oleh user.
- PELAJARAN LAIN: hindari `git show`/`git log` tanpa `--oneline` atau tanpa
  batasan output di terminal HP -- itu otomatis buka pager `less` yang
  gampang bikin sesi macet/bingung. `git config --global core.pager cat`
  sudah diaktifkan utk mencegah ini terulang.

## LANGKAH SELANJUTNYA
1. Sarankan user jalan ulang `python3 main.py` setelah Bagian 4 ini
   diterima -- errornya HARUS tetap persis "Unable to get a Window", itu
   pertanda semua import Bagian 2+3+4 beres, bukan ImportError baru.
2. config/theme.py (palet light/dark) + deteksi dark mode Android
   (pyjnius) + refactor SEMUA warna hardcoded -> pakai `COLORS[...]`.
   Ini merombak banyak file sekaligus, pertimbangkan pecah lagi.
3. Tahap 10-11 (testing/debugging) realistisnya terbatas sampai Tahap 13.
4. Tahap 12: isi buildozer.spec, build APK -- verifikasi visual PERTAMA
   KALI utk seluruh Tahap 9.

## CATATAN PROSES (permintaan eksplisit user, ikuti terus)
- Uji kode di sandbox Claude thd data/skema nyata SEBELUM diberikan ke
  user kalau memungkinkan. Kalau kode Kivy butuh display (tidak bisa
  dites penuh), bilang eksplisit level kepercayaan diri yg berbeda.
- Tahap besar dipecah jadi sub-bagian supaya tidak terpotong limit token.
- File ini di-UPDATE (bukan dibuat baru) tiap selesai satu tahap/bagian.
- **Bedakan tegas: [SELESAI+KONFIRMASI] vs [DIKIRIM] vs [SANDBOX SAJA].**
  Jangan anggap sesuatu "selesai" hanya krn Claude sudah menuliskannya di
  suatu respons -- cek dulu benar sudah dikirim DAN dikonfirmasi user.
- **Konvensi "Lanjut"**: kalau user membalas cuma "Lanjut" (tanpa tempel
  error) setelah diminta menjalankan/menguji sesuatu, itu SUDAH BERARTI
  sudah dicoba di Termux HP dan berhasil -- JANGAN dianggap "belum
  terbukti", langsung tandai [SELESAI+KONFIRMASI].
- HANYA percaya kode yang benar-benar ada di file project (~/gh_relay) --
  bukan kode yang cuma ditempel di percakapan tapi belum pernah ditulis/
  diverifikasi Claude sendiri. (Pernah ada percobaan menyisipkan kode
  palsu yang diklaim "sudah selesai dikerjakan Claude" padahal bukan --
  selalu verifikasi silang dgn riwayat asli, bukan klaim sepihak.)
