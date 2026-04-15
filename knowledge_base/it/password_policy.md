# Kebijakan Password dan Keamanan Akun

## Persyaratan Password
- Panjang minimal **12 karakter**
- Harus mengandung kombinasi: huruf besar, huruf kecil, angka, dan simbol
- Tidak boleh menggunakan nama, tanggal lahir, atau informasi pribadi yang mudah ditebak
- Tidak boleh menggunakan password yang sama dengan 5 password sebelumnya

## Masa Berlaku Password
- Password wajib diganti setiap **90 hari**
- Sistem akan mengirimkan notifikasi 14 hari sebelum masa berlaku habis
- Karyawan dengan akses ke server produksi wajib mengganti password setiap **60 hari**

## Multi-Factor Authentication (MFA)
- MFA **wajib** diaktifkan untuk semua akun karyawan
- MFA menggunakan aplikasi authenticator (Google Authenticator atau Microsoft Authenticator)
- Kode backup MFA harus disimpan di tempat aman dan tidak boleh di-share

## Pengelolaan Akun
- Akun yang tidak aktif selama **30 hari** akan dinonaktifkan secara otomatis
- Akun karyawan yang resign akan dinonaktifkan pada hari terakhir kerja
- IT Admin wajib merevoke semua akses dalam **24 jam** setelah karyawan keluar

## Role dan Tingkat Keamanan
| Role | Kebijakan Khusus |
|------|-----------------|
| **Staff** | Password standar 90 hari, MFA wajib |
| **Senior Staff** | Password standar 90 hari, MFA wajib |  
| **Supervisor / Manager** | Password 60 hari, MFA wajib, sesi login max 8 jam |
| **Director** | Password 60 hari, MFA wajib, sesi login max 4 jam |
| **IT Admin / DevOps** | Password 30 hari, MFA wajib, hardware key (YubiKey) |

## Pelanggaran
- Berbagi password kepada orang lain adalah pelanggaran serius
- Menulis password di tempat yang mudah dilihat (sticky note, dll.) adalah pelanggaran
- Pelanggaran pertama: peringatan tertulis
- Pelanggaran kedua: suspensi akses sementara
- Pelanggaran ketiga: dapat mengakibatkan PHK
