# Panduan Monitoring Sistem & SLA Auresys

## 1. Definisi & Tujuan Monitoring

Monitoring sistem adalah proses pengawasan berkelanjutan terhadap infrastruktur IT, performa aplikasi, dan keamanan data. Tujuannya:
- Mendeteksi anomali dan insiden sebelum berdampak ke pengguna
- Memastikan ketersediaan layanan sesuai SLA (Service Level Agreement)
- Merekam jejak audit (audit trail) untuk kebutuhan investigasi

## 2. SLA (Service Level Agreement) Perusahaan

| Layanan | Target Uptime | Max Downtime/Bulan | Respons Insiden |
|---|---|---|---|
| Aplikasi Core (Produksi) | 99.9% | 43 menit | < 15 menit |
| Database Utama | 99.95% | 22 menit | < 10 menit |
| Email & Komunikasi | 99.5% | 3.6 jam | < 30 menit |
| Sistem HR & Payroll | 99.0% | 7.2 jam | < 1 jam |
| Portal Internal | 95.0% | 36 jam | < 4 jam |

**SLA Breach** terjadi jika target uptime tidak tercapai dalam satu bulan kalender → wajib lapor ke Direktur IT & Auditor dalam 24 jam.

## 3. Metrik Kunci yang Dipantau

### Infrastruktur
- CPU Usage: Alert jika > 80% selama 5 menit berturut-turut
- Memory Usage: Alert jika > 85%
- Disk Usage: Alert jika > 90%, Critical jika > 95%
- Network Latency: Alert jika > 100ms (intra-network)

### Keamanan
- Failed Login Attempts: Alert jika > 5 kali gagal dalam 10 menit (per user)
- Unauthorized Access: Alert immediate jika role Staff akses sistem produksi
- Data Export Volume: Alert jika satu user mengeksport > 10.000 baris data dalam 1 jam

### Aplikasi
- API Response Time: Alert jika P95 > 500ms
- Error Rate: Alert jika > 1% dari total request
- Queue Depth: Alert jika antrian task > 1.000 item

## 4. Prosedur Respons Insiden

### Severity 1 (Critical) — SLA Breach / Data Loss
1. Notifikasi otomatis ke On-Call Engineer + Manajer IT + Auditor
2. War room meeting dalam 30 menit
3. Status page diupdate setiap 15 menit
4. Post-mortem wajib dalam 48 jam setelah resolved

### Severity 2 (High) — Degradasi Performa Signifikan
1. Notifikasi ke Tim IT
2. Eskalasi ke Manajer jika tidak resolved dalam 2 jam
3. Post-mortem opsional

### Severity 3 (Medium/Low) — Anomali Minor
1. Ticket dibuat di sistem helpdesk
2. Diselesaikan dalam SLA normal (next business day)

## 5. Alat Monitoring yang Digunakan

| Alat | Fungsi |
|---|---|
| Grafana + Prometheus | Visualisasi metrik infrastruktur |
| ELK Stack (Elasticsearch, Logstash, Kibana) | Log aggregation dan analisis |
| PagerDuty | Alerting dan on-call management |
| Sentry | Error tracking aplikasi |
| Uptime Robot | External availability monitoring |

## 6. Retensi Log & Data Audit

- Log aplikasi: Disimpan **90 hari** (live), kemudian diarsipkan 1 tahun
- Log akses sistem: Disimpan **1 tahun** (persyaratan kepatuhan)
- Log transaksi keuangan: Disimpan **7 tahun** (persyaratan hukum)
- Backup database: Retensi **30 hari** untuk daily backup, **12 bulan** untuk monthly backup
