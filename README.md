# Moja pretraživalica za praćenje članaka

Ovo je jednostavna Python aplikacija koja ti pomaže pratiti gdje se na webu pojavljuju tvoji članci sa bloga.

Aplikacija:
* pročita tvoje objave s bloga
* za svaku objavu generira nekoliko upita
* šalje upite na serper.dev (Google Search API)
* za pronađene stranice dohvaća tekst i računa sličnost s izvornim člankom
* rezultate prikazuje u Streamlit sučelju i omogućuje izvoz u CSV

## Brzi početak

1. Kreiraj virtualno okruženje i instaliraj ovisnosti:

```bash
cd leonarda_news_monitor
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Uzmi serper.dev API ključ (free tier, ~250 upita/mj.) na https://serper.dev, pa ga postavi kao varijablu okruženja:

```bash
export SERPER_API_KEY="tvoj_ključ"   # Windows (PowerShell):  $Env:SERPER_API_KEY="tvoj_ključ"
```

3. Pokreni aplikaciju:

```bash
streamlit run app.py
```

4. Otvorit će ti se preglednik sa Streamlit sučeljem gdje možeš:
* promijeniti adresu bloga ako želiš
* promijeniti prag sličnosti
* pokrenuti pretraživanje
* preuzeti rezultate u CSV formatu

## Napomena

Struktura koda je jednostavna i namjerno čitka kako bi ju lako mogla prilagođavati.
Ako želiš:
* dodati druge izvore pretraživanja
* spremati rezultate u SQLite
* automatizirati izvođenje kroz cron
možeš nadograditi postojeće module ili dodati nove.
