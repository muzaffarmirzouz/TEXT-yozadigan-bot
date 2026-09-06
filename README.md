# Ko'p-kanalli avtomatik izoh (caption) boti

Botni istalgan sondagi kanalga admin qilib qo'shishingiz mumkin — har bir kanal
uchun **alohida-alohida** izoh matni belgilanadi. Kanalga video yoki rasm
tashlanganda, bot o'sha kanal uchun sozlangan matnni avtomatik ravishda
postning izohiga (caption) qo'shib qo'yadi. Agar postda odam qo'lda yozgan
izoh bo'lsa, sizning matningiz uning **pastiga** qo'shib yoziladi.

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
orasida saqlanib qoladi — endi push qilganingizda kanallarni qayta
ro'yxatdan o'tkazish yoki izohlarni qayta yozish shart bo'lmaydi.

**Eslatma:** agar Volume'ni hozir qo'shsangiz, oldingi ma'lumotlar
(sozlagan kanallar/izohlar) allaqachon yo'qolgan bo'lishi mumkin — Volume
ulangandan keyin ikkala kanalni ham bittа marta qayta ro'yxatdan o'tkazish
kifoya: har birida botni admin huquqidan olib tashlab, qayta admin qilib
qo'shsangiz (yoki "Xabarlarni tahrirlash" huquqini o'chirib-yoqsangiz), bot
uni qayta avtomatik ro'yxatga oladi, so'ng `/setcaption` bilan matnlarni
qayta kiritasiz — bundan keyin bu takrorlanmaydi.

## 5. GitHub + Railway'ga joylash

1. Ushbu papkani GitHub'dagi yangi repo'ga yuklang.
2. Railway'da **New Project → Deploy from GitHub repo** orqali shu repo'ni ulang.
3. Railway loyihasining **Variables** bo'limiga quyidagilarni qo'shing:
   - `BOT_TOKEN`
   - `ADMIN_IDS`
   - `CHANNEL_ID` — **faqat** avvalgi (bitta kanalli) versiyadan o'tayotgan bo'lsangiz,
     eski kanalingiz ID'sini shu yerga qo'ying (bir martalik migratsiya uchun). Yangi
     o'rnatish uchun bu shart emas.
4. Railway `Procfile`ni o'zi tanib, botni `worker` sifatida ishga tushiradi.

## 6. Kanal qo'shish

1. Kanalingizga o'ting → **Administratorlar** → **Admin qo'shish** → botni tanlang.
2. Berilgan huquqlar orasida **"Xabarlarni tahrirlash" (Edit Messages)** ni
   albatta yoqing.
3. Shu zahoti bot kanalni avtomatik ro'yxatga oladi va sizga (adminga) xabar
   yuboradi. Buni istalgancha kanal uchun takrorlashingiz mumkin — kodga yoki
   Railway sozlamalariga tegishning hojati yo'q.

## 7. Foydalanish

Botning shaxsiy chatiga o'ting (admin sifatida) va:

- `/setcaption` — kanal ro'yxatidan birini tanlaysiz, so'ng shu kanal uchun
  izoh matnini yuborasiz (formatlash va emojilar bilan)
- `/caption` — kanal tanlab, uning joriy izohini ko'rasiz
- `/clearcaption` — kanal tanlab, avtomatik izoh qo'shishni to'xtatasiz
- `/channels` — ro'yxatga olingan barcha kanallar va ularda izoh bor-yo'qligi

Shundan keyin har bir kanalga tashlangan **yangi video, rasm yoki albom**ga
o'sha kanal uchun belgilangan matn avtomatik qo'shilib boradi. Har bir kanal
mustaqil ishlaydi — birining izohi boshqasiga ta'sir qilmaydi.

## Eslatmalar

- Caption uzunligi Telegram tomonidan 1024 belgigacha cheklangan; undan uzun
  bo'lsa, tahrirlash muvaffaqiyatsiz tugasa, bot avtomatik faqat o'z izohini
  qo'yishga urinadi (eski izoh o'rniga).
- Premium (custom) emojilar Telegramning o'z cheklovi tufayli kanal
  postlarida oddiy ko'rinishda chiqadi — bu bot emas, Telegram tomonidan
  qo'yilgan cheklov.
- Albom (bir vaqtda yuborilgan bir nechta video/rasm) uchun izoh faqat
  birinchi elementga qo'shiladi — Telegram butun albom uchun shuni ko'rsatadi.
