# BSM307 – Bilgisayar Ağları Dönem Projesi
## Çok Amaçlı Ağ Yönlendirme Problemi


## 👤 Öğrenci Bilgileri
- **Ad Soyad:** Muhammed Enes Köylü / 19640310011
- **Ders:** BSM307 – Bilgisayar Ağları  



## Projenin Amacı
Bu projede bilgisayar ağlarında iki düğüm arasındaki veri iletimi sırasında
**gecikme (delay)**, **güvenilirlik (reliability)** ve **kaynak kullanımı (bandwidth)**
kriterlerini aynı anda dikkate alan **çok amaçlı yönlendirme problemi**
ele alınmıştır.

Amaç, bu kriterleri dengeleyerek en uygun iletişim yolunu bulmak ve
klasik algoritmalar ile sezgisel (meta-sezgisel) algoritmaların
performanslarını karşılaştırmalı olarak incelemektir.


## Kullanılan Algoritmalar

### Dijkstra Algoritması (Baseline)
- En kısa yol problemleri için kullanılan klasik bir algoritmadır.
- Bu projede karşılaştırma amacıyla **baseline** olarak kullanılmıştır.
- Kenar ağırlıkları gecikme ve bant genişliği bilgilerine göre hesaplanmıştır.

### Genetik Algoritma (Genetic Algorithm – GA)
- Doğadan esinlenen sezgisel bir optimizasyon algoritmasıdır.
- Popülasyon tabanlı çalışır ve seçim, çaprazlama (crossover) ve mutasyon adımlarını içerir.
- Çok amaçlı maliyet fonksiyonu kullanılarak uygulanmıştır.
- Farklı ağırlık senaryoları ile deneyler gerçekleştirilmiştir.

### Simulated Annealing (SA)
- Fizikteki tavlama (annealing) sürecinden esinlenen sezgisel bir algoritmadır.
- Yerel minimumlardan kaçabilme yeteneğine sahiptir.
- Tek çözüm üzerinden iteratif iyileştirme yapar.
- GA ve Dijkstra sonuçları ile karşılaştırılmıştır.


## Kullanılan Teknolojiler
- **Programlama Dili:** Python 3  
- **Kütüphaneler:**
  - `networkx` – Ağ modelleme
  - `numpy` – Sayısal işlemler
  - `random` – Rastgelelik ve seed kontrolü


## Proje Dosya Yapısı
network_generator.py # Rastgele ağ oluşturma ve örnek testler
metrics.py # Gecikme, güvenilirlik ve kaynak maliyetleri
ga.py # Genetik Algoritma implementasyonu
sa.py # Simulated Annealing implementasyonu
experiments.py # Deneylerin toplu olarak çalıştırılması
results/
├── results.csv
└── results_summary.csv
README.md

Deneylerin tekrarlanabilir olması için tüm algoritmalarda
**sabit seed değeri (`seed = 42`)** kullanılmıştır.

## Deneyler ve Senaryolar
Genetik Algoritma için üç farklı senaryo uygulanmıştır:

- **Gecikme odaklı senaryo**
- **Güvenilirlik odaklı senaryo**
- **Bant genişliği (kaynak) odaklı senaryo**

Elde edilen sonuçlar;
- Dijkstra (baseline),
- Genetik Algoritma (GA),
- Simulated Annealing (SA)

algoritmaları arasında karşılaştırmalı olarak analiz edilmiştir.
Deney sonuçları CSV dosyaları halinde kaydedilmiştir.
