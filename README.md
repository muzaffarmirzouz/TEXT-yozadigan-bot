# Ko'p foydalanuvchili avtomatik izoh (caption) boti

Bu bot **omma uchun ochiq** — istalgan Telegram foydalanuvchisi botni o'z
kanaliga admin qilib qo'shib, faqat o'zi ko'radigan/boshqaradigan izoh
sozlashi mumkin. Har bir kanal faqat uni botga qo'shgan odamga tegishli —
boshqa foydalanuvchilar bir-birining kanaliga kira olmaydi.

Kanalga video yoki rasm tashlanganda, bot o'sha kanal egasi sozlagan matnni
avtomatik ravishda postning izohiga (caption) qo'shib qo'yadi. Agar postda
odam qo'lda yozgan izoh bo'lsa, izoh uning **pastiga** qo'shib yoziladi.
Bundan tashqari, bot **lotin tilida yozilgan matnni avtomatik o'zbek
kirillchasiga o'giradi** — bu ham admin qo'shgan izohga, ham postning o'z
izohiga qo'llaniladi.

## 1. Bot yaratish

1. Telegram'da [@BotFather](https://t.me/BotFather) ga yozing.
2. `/newbot` buyrug'ini yuboring, nom va username bering.
3. Sizga beriladigan **tokenni** saqlab qo'ying (`BOT_TOKEN`).

## 2. O'zingizning Telegram ID'ingizni topish (operator sifatida)

1. [@userinfobot](https://t.me/userinfobot) ga `/start` yozing — u sizning shaxsiy ID'ingizni beradi.
2. Buni `ADMIN_IDS` sifatida saqlang (bir nechta bo'lsa vergul bilan ajrating).
   Bu ID(lar) botning "operatori" hisoblanadi: `/stats` buyrug'ini ko'ra oladi
   va eski (bu yangilanishdan oldin qo'shilgan) kanallar shularga bog'lanadi.
   Oddiy foydalanuvchilar uchun bu shart emas — ular botni o'zlari o'z
   kanaliga qo'shib, darhol foydalana boshlaydi.

## 3. Mahalliy sinov (ixtiyoriy)

```bash
pip install -r requirements.txt
cp .env.example .env
# .env faylini o'z BOT_TOKEN va ADMIN_IDS qiymatlaringiz bilan to'ldiring
python bot.py
```

## 4. Railway'da doimiy xotira (Volume) — MUHIM

Railway konteyneri har deploy'da yangidan yaratiladi, shu sabab oddiy fayllar
(bizning `captions.db`imiz) **har push'dan keyin o'chib ketadi**, agar Volume
ulanmagan bo'lsa.

1. Railway loyihangizda servisni oching → **Settings → Volumes → New Volume**.
2. Mount path sifatida `/data` yozing.
3. **Variables**'ga yangi o'zgaruvchi qo'shing: `DB_PATH=/data/captions.db`.
4. Qayta deploy qiling.

## 5. GitHub + Railway'ga joylash

1. Ushbu papkani GitHub'dagi repo'ga yuklang (eski fayllar o'rniga).
2. Railway'da **New Project → Deploy from GitHub repo** orqali shu repo'ni
   ulang (yoki mavjud loyihangizga push qiling — avtomatik qayta deploy bo'ladi).
3. Railway loyihasining **Variables** bo'limiga quyidagilarni qo'shing:
   - `BOT_TOKEN`
   - `ADMIN_IDS` — sizning (operator) Telegram ID'ingiz
   - `DB_PATH` (4-bo'limga qarang)
   - `REQUIRED_CHANNEL` — standart holatda `@namanganliklar_uz` (6-bo'limga qarang);
     boshqa kanal kerak bo'lsa shu yerda o'zgartirasiz.
   - `CHANNEL_ID` — **faqat** eng birinchi (bitta kanalli) versiyadan
     to'g'ridan-to'g'ri o'tayotgan bo'lsangiz kerak.
4. Railway `Procfile`ni o'zi tanib, botni `worker` sifatida ishga tushiradi.

**Muhim (bir martalik migratsiya):** birinchi marta shu yangi versiya bilan
ishga tushganda, bot avvalgi (omma uchun ochilishidan oldin qo'shilgan)
barcha kanallarni avtomatik ravishda `ADMIN_IDS`dagi birinchi ID'ga
(ya'ni sizga) bog'lab qo'yadi — hech narsa qo'lda qilish shart emas, eski
kanallaringiz va izohlaringiz ishlashda davom etadi.

## 6. Majburiy obuna (@namanganliklar_uz) — MUHIM

Bot endi faqat **@namanganliklar_uz** kanaliga obuna bo'lgan foydalanuvchilarga
xizmat qiladi — obuna bo'lmagan odam hech qanday buyruqni ishlata olmaydi
(hatto /start ham "avval obuna bo'ling" deb javob beradi).

**Buning ishlashi uchun bitta shart bor: shu botning o'zi ham
@namanganliklar_uz kanaliga qo'shilgan bo'lishi kerak** (kamida oddiy a'zo
sifatida — admin bo'lishi shart emas, faqat a'zolikni tekshira olishi
uchun). Aks holda Telegram bot API a'zolikni tekshirishga ruxsat bermaydi.

1. @namanganliklar_uz kanaliga o'ting → Administratorlar → Admin qo'shish
   (yoki oddiy a'zo sifatida qo'shsangiz ham yetarli) → shu caption-botni
   tanlang.
2. Boshqa hech qanday sozlash shart emas — bot o'zi avtomatik tekshiradi.

Agar boshqa kanalga obuna talab qilmoqchi bo'lsangiz, Railway'dagi
`REQUIRED_CHANNEL` o'zgaruvchisini o'sha kanalning username'iga
(`@boshqa_kanal` ko'rinishida) o'zgartiring.

**Eslatma:** agar bot biror sababdan @namanganliklar_uz'dagi a'zolikni
tekshira olmasa (masalan hali qo'shilmagan bo'lsa), xatolik yuz berib,
botdan foydalanish **hamma uchun** vaqtincha ochiq qolib ketadi (tizim
qulab qolmasligi uchun ataylab shunday qilingan) — shu sabab bot doim
@namanganliklar_uz'ga qo'shilgan holda turishi kerak.

## 7. Botni foydalanuvchilarga ulashish

Endi botni istalgan odamga (masalan botning username'ini @kanal yoki
guruhlarda ulashib) tavsiya qilishingiz mumkin. Har bir yangi foydalanuvchi:

1. Botni o'z kanaliga **admin** qilib qo'shadi.
2. **"Xabarlarni tahrirlash" (Edit Messages)** huquqini yoqadi.
3. Botning shaxsiy chatida `/setcaption` bilan o'z izohini belgilaydi.

Bot avtomatik ravishda o'sha odamni kanalning egasi deb hisoblaydi (chunki
aynan o'sha botni admin qilib qo'shgan) — boshqa hech kim (operator ham)
o'sha kanalning izohini ko'ra yoki o'zgartira olmaydi.

## 8. Buyruqlar

- `/start` yoki `/help` — botni tanishtirish va qo'llanma
- `/setcaption` — o'z kanallaringizdan birini tanlab, izoh belgilash
- `/caption` — o'z kanallaringizdan birining joriy izohini ko'rish
- `/clearcaption` — o'z kanallaringizdan birining avtomatik izohini to'xtatish
- `/translit` — o'z kanallaringizdan biri uchun o'girish yo'nalishini tanlash
  (Lotin→Kirill / Kirill→Lotin / O'chirilgan)
- `/channels` — sizga tegishli kanallar ro'yxati, izoh va o'girish holati
- `/stats` — **faqat operator (`ADMIN_IDS`) uchun** — jami kanallar va
  foydalanuvchilar soni

## Lotin ↔ kirill o'girish qanday ishlaydi

- `transliterate.py` faylida qoida-asoslangan (tashqi kutubxonasiz) o'girish
  mexanizmi bor — shu sabab Railway'da qo'shimcha pip paketi kerak emas.
- Har bir kanal uchun **alohida** yo'nalish tanlanadi (`/translit` orqali):
  - **Lotin → Kirill** (standart) — `sh→ш`, `ch→ч`, `o'→ў`, `g'→ғ`,
    `yo/yu/ya/ye→ё/ю/я/е`, so'z boshidagi `e→э` va h.k.
  - **Kirill → Lotin** — teskari yo'nalish (`ш→sh`, `ў→o'`, `ғ→g'` va h.k.)
  - **O'chirilgan** — hech narsa o'girilmaydi, matn qanday yozilgan bo'lsa
    shundayligicha qoladi
- O'zbek klaviaturasida ishlatiladigan **barcha apostrof variantlarini**
  taniydi — jumladan iPhone/Android avtokorrektsiyasi yozadigan "aylanma"
  apostrofni (`’`) ham.
- **Tegilmaydigan narsalar:** URL'lar, `@mention`lar, `#hashtag`lar, telefon
  raqamlari va HTML formatlash teglari (qalin, kursiv, havola).
- Bu o'girish ham admin qo'shgan izohga, ham postning o'z (boshqa odam
  yozgan) izohiga qo'llaniladi — ikkalasi ham shu kanal uchun tanlangan
  bitta yo'nalishda o'giriladi.

## Xavfsizlik / izolyatsiya

- Har bir kanal faqat bitta "egasi" (botni o'sha kanalga admin qilib
  qo'shgan Telegram foydalanuvchisi)ga bog'lanadi.
- `/setcaption`, `/caption`, `/clearcaption` buyruqlari faqat chaqiruvchining
  o'z kanallarini ko'rsatadi; boshqa birovning kanal ID'sini taxmin qilib
  yuborishga urinish ham serverda tekshirilib rad etiladi.
- Bot kanaldan olib tashlansa (yoki admin huquqidan tushirilsa), o'sha
  kanal va uning izohi avtomatik ravishda ma'lumotlar bazasidan o'chiriladi.

## Eslatmalar

- Caption uzunligi Telegram tomonidan 1024 belgigacha cheklangan; undan uzun
  bo'lsa, bot avtomatik faqat o'z izohini qo'yishga urinadi (eski izoh o'rniga).
- Premium (custom) emojilar Telegramning o'z cheklovi tufayli kanal
  postlarida oddiy ko'rinishda chiqadi — bu Telegram tomonidan qo'yilgan
  cheklov, bot bunga ta'sir qila olmaydi.
- Albom (bir vaqtda yuborilgan bir nechta video/rasm) uchun izoh faqat
  birinchi elementga qo'shiladi — Telegram butun albom uchun shuni ko'rsatadi.
