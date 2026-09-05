# Kanal uchun avtomatik izoh (caption) boti

Kanalga video yoki rasm tashlanganda, bot avtomatik ravishda siz belgilagan matnni
postning izohiga (caption) qo'shib qo'yadi. Agar postda odam qo'lda yozgan izoh
bo'lsa, sizning matningiz uning **pastiga** qo'shib yoziladi (o'chirilmaydi).

## 1. Bot yaratish

1. Telegram'da [@BotFather](https://t.me/BotFather) ga yozing.
2. `/newbot` buyrug'ini yuboring, nom va username bering.
3. Sizga beriladigan **tokenni** saqlab qo'ying (`BOT_TOKEN`).

## 2. Botni kanalga admin qilib qo'shish

1. Kanalingizga o'ting → **Administratorlar** → **Admin qo'shish** → botni tanlang.
2. Berilgan huquqlar orasida **"Xabarlarni tahrirlash" (Edit Messages)** ni
   albatta yoqing — bot shu huquq orqali kanaldagi postlarni tahrirlaydi.

## 3. Kanal ID'ni topish

1. Kanaldagi istalgan postni [@userinfobot](https://t.me/userinfobot) ga forward qiling —
   u sizga kanal ID'sini ko'rsatadi (odatda `-100` bilan boshlanadi, masalan `-1001234567890`).

## 4. O'zingizning Telegram ID'ingizni topish

1. [@userinfobot](https://t.me/userinfobot) ga `/start` yozing — u sizning shaxsiy ID'ingizni beradi.
2. Bir nechta admin bo'lsa, ID'larni vergul bilan ajrating: `111111111,222222222`.

## 5. Mahalliy sinov (ixtiyoriy)

```bash
pip install -r requirements.txt
cp .env.example .env
# .env faylini o'z BOT_TOKEN, CHANNEL_ID, ADMIN_IDS qiymatlaringiz bilan to'ldiring
python bot.py
```

## 6. GitHub + Railway'ga joylash

1. Ushbu papkani GitHub'dagi yangi repo'ga yuklang.
2. Railway'da **New Project → Deploy from GitHub repo** orqali shu repo'ni ulang.
3. Railway loyihasining **Variables** bo'limiga quyidagilarni qo'shing:
   - `BOT_TOKEN`
   - `CHANNEL_ID`
   - `ADMIN_IDS`
4. Railway `Procfile`ni o'zi tanib, botni `worker` sifatida ishga tushiradi.

## 7. Foydalanish

Botning shaxsiy chatiga o'ting (admin sifatida) va:

- `/setcaption` — bot izoh matnini so'raydi; keyingi xabaringizni (qalin/kursiv
  shrift, havolalar, premium/custom emojilar bilan) yuborsangiz, aynan o'sha
  ko'rinishda saqlanadi. Bekor qilish uchun `/cancel`.
- `/caption` — joriy izohni (formatlash bilan) ko'rsatadi
- `/clearcaption` — avtomatik izoh qo'shishni to'xtatadi

Shundan keyin kanalga tashlangan **har bir yangi video yoki rasmga** bu matn
avtomatik qo'shilib boradi. Eski (avvaldan turgan) postlarga ta'sir qilmaydi —
faqat yangi tashlanganlariga ishlaydi.

## Eslatmalar

- Caption uzunligi Telegram tomonidan 1024 belgigacha cheklangan; undan uzun
  matn avtomatik qisqartiriladi.
- Bot faqat `CHANNEL_ID` da ko'rsatilgan kanaldagi postlarga ishlov beradi.
- Video yoki rasm o'rniga boshqa turdagi fayllar (hujjat, audio va h.k.) uchun
  `bot.py` faylidagi `@dp.channel_post(F.video | F.photo)` qatoridagi filterga
  kerakli turni qo'shsangiz bo'ladi (masalan `F.document`).
