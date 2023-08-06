
![title](https://drive.google.com/uc?export=view&id=1kNTbXCojFechk1MKt1BPwVwoOWqE3kUW)

<br />
<div align="center">
<strong>
cari anime dan film subtitle Indonesia
</strong>
</div>

-------

Pernah terpikir untuk menonton film atau anime di website secara gratis tapi selalu direpotkan dengan iklan. atau jika ingin mendownload harus melalui shortlink ini itu, tenang melalui tool ini anda dapat dengan mudah mencari link download anime atau film yang anda inginkan tanpa harus  diganggu oleh iklan dan shortlink.

# instalasi
Menggunakan python package manager
```bash
python -m pip install lk21
```

bagaimana jika terdapat versi baru? tidak perlu khawatir `lk21` sudah dilengkapi dengan pemberitahuan yang akan muncul setelah program selesai dijalankan. Kamu bisa langsung memperbaharui menggunakan perintah berikut
```bash
python -m pip install --upgrade lk21
```

# daftar website
| no | name | site | tag |
|:---:|:---:|:---:|:---:|
| 1 | Anibatch | https://o.anibatch.me/ | anime |
| 2 | Anikyojin | https://anikyojin.net | anime |
| 3 | Animeindo | https://animeindo.asia | anime |
| 4 | Drivenime | https://drivenime.com | anime |
| 5 | Kusonime | https://kusonime.com | anime |
| 6 | Layarkaca21 | http://149.56.24.226/ | movie |
| 7 | Nekonime | https://nekonime.stream | anime |
| 8 | Oploverz | https://www.oploverz.in | anime |
| 9 | Otakudesu | https://otakudesu.tv | anime |
| 10 | Samehadaku | https://samehadaku.vip | anime |
| 11 | Wibudesu | https://wibudesu.com | anime |
| 13 | Riie | https://riie.jp | anime |
| 14 | Melongmovie | https://melongmovie.com | movie |
| 15 | Asuka_Zonawibu | https://asuka.zonawibu.net | anime |

# Penggunaan
Melalui terminal secara langsung, sebagai contoh saya akan mencari film `insurgent`.

```bash
$ lk21 insurgent
Mencari 'insurgent' -> 149.56.24.226 halaman 1
Total item terkumpul: 1 item dari total 1 halaman
Mengekstrak link unduhan: insurgent-2015
? Pilih: (Use arrow keys)
 » 1. Fembed
   2. 1fichier
   3. Cloudvideo
   4. Uptobox
   5. Mirrorace
   6. Go4up
   7. Embedupload
```

Sangat mudah bukan, saya menggunakan library [questionary](https://pypi.org/project/questionary/) untuk memilih link unduhan nya

# Library
lk21 juga dapat digunakan sebagai library. Artinya, Anda dapat mengimpornya ke aplikasi Anda sendiri.

```python
from lk21.extractors.layarkaca21 import Layarkaca21

scraper = Layarkaca21()
result = scraper.search("insurgent", page=1)
# [{'title': 'Insurgent (2015)', 'genre': ['thriller', 'sci-fi', 'adventure'], 'star': ['Kate Winslet', 'Jai Courtney', 'Mekhi Phifer', 'Shailene Woodley'], 'country': ['usa'], 'size': ['1080', ''], 'quality': ['bluray', ''], 'year': ['2015', ''], 'director': 'Robert Schwentke', 'id': 'insurgent-2015'}]

# parameter yang dibutuhkan id, type str
dl = scraper.extract(result[0]["id"])
# {'Fembed': {'360': 'https://layarkacaxxi.icu/f/l-pg1un3k-4zy0z', '480': 'https://layarkacaxxi.icu/f/l-pg1un3k-4zy0z', '720': 'https://layarkacaxxi.icu/f/l-pg1un3k-4zy0z', '1080': 'https://layarkacaxxi.icu/f/l-pg1un3k-4zy0z'}, '1fichier': {'1080': 'https://1fichier.com/?xmnyfjrgufsolwxot482'}, 'Cloudvideo': {'1080': 'https://cloudvideo.tv/d5dcgcmw48xr'}, 'Uptobox': {'1080': 'https://uptobox.com/4td03kyc6jw6'}, 'Mirrorace': {'1080': 'https://mirrorace.org/m/1Gb4z'}, 'Go4up': {'1080': 'http://dl.go4up.com/dl/071f635ef45857'}, 'Embedupload': {'1080': 'http://www.embedupload.com/?d=6YCHFCJDKT'}}
```


<i>Bantu saya memperbaiki dokumentasi module</i>

-------

lk21 is under MIT license
