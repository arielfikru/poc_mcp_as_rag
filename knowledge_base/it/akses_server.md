# Kebijakan Akses Server Produksi

## Prinsip Least Privilege
Akses ke server produksi diberikan berdasarkan prinsip **least privilege**: setiap karyawan hanya mendapatkan akses minimum yang dibutuhkan untuk pekerjaannya.

## Matriks Akses Berdasarkan Role

| Role | Akses Server Produksi | Keterangan |
|------|----------------------|------------|
| **Staff** | ❌ Tidak Diizinkan | Tidak memiliki akses sama sekali |
| **Senior Staff** | ⚠️ Read-Only (Terbatas) | Hanya boleh melihat log, tidak bisa modifikasi |
| **Supervisor** | ⚠️ Read-Only | Akses monitoring dan log aplikasi |
| **Manager** | ✅ Akses Penuh (dengan approval) | Membutuhkan tiket approval dari Director |
| **Director** | ✅ Akses Penuh | Akses langsung tanpa approval tambahan |
| **DevOps / IT Admin** | ✅ Akses Penuh | Akses operasional penuh |

## Prosedur Permintaan Akses Darurat (Emergency Access)
1. Karyawan dengan role di bawah Manager yang membutuhkan akses mendesak harus mengajukan tiket darurat.
2. Tiket harus disetujui oleh minimal seorang Manager dan seorang IT Admin.
3. Akses darurat bersifat sementara, maksimum **4 jam**.
4. Semua aktivitas selama akses darurat diaudit dan dilaporkan ke Security Team.

## Larangan Keras
- Dilarang berbagi kredensial akses server produksi kepada siapapun.
- Dilarang mengakses server produksi dari jaringan publik tanpa VPN perusahaan.
- Pelanggaran dapat mengakibatkan pemutusan hubungan kerja.

## Audit Log
Seluruh akses ke server produksi direkam dan diaudit secara berkala oleh tim IT Security.
