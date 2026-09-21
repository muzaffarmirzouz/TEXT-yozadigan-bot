# Ko'p-kanalli avtomatik izoh (caption) boti

Botni istalgan sondagi kanalga admin qilib qo'shishingiz mumkin — har bir kanal
uchun **alohida-alohida** izoh matni belgilanadi. Kanalga video yoki rasm
tashlanganda, bot o'sha kanal uchun sozlangan matnni avtomatik ravishda
postning izohiga (caption) qo'shib qo'yadi. Agar postda odam qo'lda yozgan
izoh bo'lsa, sizning matningiz uning **pastiga** qo'shib yoziladi.

Bundan tashqari, bot **lotin tilida yozilgan matnni avtomatik o'zbek
kirillchasiga o'giradi** — bu ham admin qo'shgan izohga, ham postning o'z
(boshqa odam yozgan) izohiga qo'llaniladi.

## 1. Bot yaratish

1. Telegram'da [@BotFather](https://t.me/BotFather) ga yozing.
2. `/newbot` buyrug'ini yuboring, nom va username bering.
3. Sizga beriladigan **tokenni** saqlab qo'ying (`BOT_TOKEN`).

## 2. O'zingizning Telegram ID'ingizni topish

1. [@userinfobot](https://t.me/userinfobot) ga `/start` yozing — u sizning shaxsiy ID'ingizni beradi.
2. Bir nechta admin bo'lsa, ID'larni vergul bilan ajrating: `111111111,222222222`.

## 3. Mahalliy sinov (ixtiyoriy)

```bash
pip install -r requirements.txt
cp .env.example .env
# .env faylini o'z BOT_TOKEN va ADMIN_IDS qiymatlaringiz bilan to'ldiring
python bot.py
```

## 4. Railway'da doimiy xotira (Volume) — MUHIM

Railway konteyneri har deploy'da yangidan yaratiladi, shu sabab oddiy fayllar
(bizning `captions.db`imiz — barcha kanallar va izohlar shu yerda) **har
push'dan keyin o'chib ketadi**, agar Volume ulanmagan bo'lsa.

1. Railway loyihangizda servisni oching → **Settings → Volumes → New Volume**.
2. Mount path sifatida `/data` yozing (istalgan nom, faqat keyingi qadamda
   moslashtiring).
3. **Variables**'ga yangi o'zgaruvchi qo'shing: `DB_PATH=/data/captions.db`.
4. Qayta deploy qiling.

Shundan keyin ma'lumotlar (kanallar ro'yxati, har birining izohi) deploy'lar
orasida saqlanib qoladi.

## 5. GitHub + Railway'ga joylash

1. Ushbu papkani GitHub'dagi repo'ga yuklang (eski fayllar o'rniga).
2. Railway'da **New Project → Deploy from GitHub repo** orqali shu repo'ni ulang
   (yoki mavjud loyihangizga push qiling — avtomatik qayta deploy bo'ladi).
3. Railway loyihasining **Variables** bo'limiga quyidagilarni qo'shing:
   - `BOT_TOKEN`
   - `ADMIN_IDS`
   - `DB_PATH` (4-bo'limga qarang)
   - `CHANNEL_ID` — **faqat** avvalgi (bitta kanalli) versiyadan o'tayotgan bo'lsangiz,
     eski kanalingiz ID'sini shu yerga qo'ying (bir martalik migratsiya uchun).
4. Railway `Procfile`ni o'zi tanib, botni `worker` sifatida ishga tushiradi.

## 6. Kanal qo'shish

1. Kanalingizga o'ting → **Administratorlar** → **Admin qo'shish** → botni tanlang.
2. Berilgan huquqlar orasida **"Xabarlarni tahrirlash" (Edit Messages)** ni
   albatta yoqing.
3. Shu zahoti bot kanalni avtomatik ro'yxatga oladi va sizga (adminga) xabar
   yuboradi. Buni istalgancha kanal uchun takrorlashingiz mumkin.

## 7. Foydalanish

Botning shaxsiy chatiga o'ting (admin sifatida) va:

- `/setcaption` — kanal ro'yxatidan birini tanlaysiz, so'ng shu kanal uchun
  izoh matnini yuborasiz (formatlash va emojilar bilan). Lotin tilida yozsangiz,
  saqlashdan oldin avtomatik kirillga o'giriladi.
- `/caption` — kanal tanlab, uning joriy izohini ko'rasiz
- `/clearcaption` — kanal tanlab, avtomatik izoh qo'shishni to'xtatasiz
- `/channels` — ro'yxatga olingan barcha kanallar va ularda izoh bor-yo'qligi

Shundan keyin har bir kanalga tashlangan **yangi video, rasm yoki albom**ga
o'sha kanal uchun belgilangan matn avtomatik qo'shilib boradi.

## Lotin → kirill o'girish qanday ishlaydi

- `transliterate.py` faylida qoida-asoslangan (tashqi kutubxonasiz) o'girish
  mexanizmi bor — shu sabab Railway'da qo'shimcha pip paketi kerak emas.
- Standart o'zbekcha qoidalarga amal qiladi: `sh→ш`, `ch→ч`, `o'→ў`, `g'→ғ`,
  `yo/yu/ya→ё/ю/я`, so'z boshidagi `e→э` va h.k.
- **Tegilmaydigan narsalar:** URL'lar, `@mention`lar, `#hashtag`lar, telefon
  raqamlari va HTML formatlash teglari (qalin, kursiv, havola) — bularning
  ichidagi matn (masalan havola manzili) o'zgarishsiz qoladi.
- Allaqachon kirill yozuvidagi matnga tegilmaydi — faqat lotin harflari (A-Z)
  topilgan joylarda ishlaydi.

## Eslatmalar

- Caption uzunligi Telegram tomonidan 1024 belgigacha cheklangan; undan uzun
  bo'lsa, tahrirlash muvaffaqiyatsiz tugasa, bot avtomatik faqat o'z izohini
  qo'yishga urinadi (eski izoh o'rniga).
- Premium (custom) emojilar Telegramning o'z cheklovi tufayli kanal
  postlarida oddiy ko'rinishda chiqadi — bu bot emas, Telegram tomonidan
  qo'yilgan cheklov.
- Albom (bir vaqtda yuborilgan bir nechta video/rasm) uchun izoh faqat
  birinchi elementga qo'shiladi — Telegram butun albom uchun shuni ko'rsatadi.
