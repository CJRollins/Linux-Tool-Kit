# 𐌻𐌹𐌽𐌿𐌺𐍃-𐍄𐌴𐍅𐌰

**Linux-Tewa** · *Linux Tool Kit*

> 𐌷𐌰𐌹𐌻𐍃! · *Hails!* — Greetings.
>
> Þata ist sō bōka andbahtjē — Tewa Andbahtē faur þō razda Linux.
> Her gameliþa standand managa waurstwa jah skōhsla, þōei briggand
> frōþein jah hilpa du þaim þaiei brūkjand þana baúrgs-ahman.
>
> *This is the book of services — the Tool Kit for the Linux tongue.
> Herein are written many works and instruments which bring wisdom
> and help to those who use the system.*

---

## 𐌹𐌽𐌰𐌲𐌴𐌹𐌽𐍃 — *Inageins* (Introduction)

Þō bōkō habaiþ taikneis fram aldjai Gutiskai razdai unte modernai
ƕeilai. Andnimiþ jah brūkeiþ ana frijis wiljins; ni waíhts kaúpōþ ist.

*This collection holds tools from the ancient Gothic tongue through to
the modern hour. Take and use freely; nothing is sold.*

---

## 𐌰𐌽𐌳𐌱𐌰𐌷𐍄𐌾𐌰 — *Andbahtja* (The Tools)

### 𐌲𐌿𐍄𐌹𐍃𐌺𐌰 𐌲𐌰𐌼𐌴𐌻𐌾𐌰𐌽𐌳𐍃 · `gothic_translator.py`
*Gutiska Gameljands* — The Gothic Translator.

Sa gameljands inmaideiþ waurda du þrim wisam:

- **Ƕahjandō Razda** — *whispered speech* (audio synthesis metadata)
- **Ƕahjands Stibna** — *whispered tone* (stylistic transformation)
- **Lox Gameleins** — *Lox code* (Wren-base language output)

```bash
python3 gothic_translator.py "Skadus jah riqis kunnun mik"
python3 gothic_translator.py "thy secrets" --format whisper_speech --tone dark
python3 gothic_translator.py "ancient tome" --format lox -o tome.lox
```

Saiƕ þō bōka `GOTHIC_TRANSLATOR_README.md` faur all gakunþi.
*See the file `GOTHIC_TRANSLATOR_README.md` for full knowledge.*

### 𐌲𐌿𐍄𐌾𐌰𐌽 · `gothicize`
*Gutjan* — To Make Gothic.

Straumiu-sīleins ize gawandeiþ waurda du Gutiskai stibnai. Glōseis
status jah waurda tekniska wairþand swē kandeil-liuhaþ.

*A stream filter that turns words into the Gothic register. Status
glyphs and technical vocabulary become as candlelight.*

```bash
./some_script.sh   | ./gothicize
apt update 2>&1    | ./gothicize
./gothicize < report.txt > report.gothic.txt
```

### 𐌱𐌴𐍄𐌴𐌹𐌽𐍃 · `bless`
*Bēteins* — The Blessing.

Gajuks `gothicize` — akei her wairþand waurda swē sunnō-liuhaþ. Airzeis
wisand jainþrō airzeis; iþ briggand uns swē friþa-skalks.

*The twin of `gothicize` — but here words become sunlight. Errors
remain errors; yet they are delivered as by a kindly chaplain.*

```bash
./some_script.sh | ./bless
./bless < report.txt > report.blessed.txt
```

### 𐌷𐌰𐌿𐍃𐌾𐌰𐌽𐌳𐍃 · `auscultation.sh`
*Hausjands* — The Listener.

Skōhsl þatei hauseiþ ana baurgsmaurgnai (system) jah saggweiþ haila
manageinō: kuntōs, baúgōs, jah þō nēƕa mikilein gaminþjō.

*A tool that listens upon the system and reports its health:
processes, services, and the close measure of memory.*

```bash
./auscultation.sh
```

Habaiþ jah miþgaman `auscultation_lox.lox` — Lox-gameleins.
*Has also `auscultation_lox.lox` — a Lox companion script.*

### 𐌲𐍀𐌿-𐌲𐌰𐍃𐌰𐌹𐍈𐌰𐌽𐌳𐍃 · `gpu-diagnostics.sh`
*GPU-Gasaiƕands* — The Looker upon the Graphic Engines.

Gasaiƕiþ ana þaim raiþeim gramman (GPU) jah uskannjiþ saiwala-
frōþein ize: ƕēh, marka, kjuls, jah filu maiza.

*Looks upon the graphical engines (GPU) and makes known their
soul-wisdom: heat, mark, driver, and much more.*

```bash
./gpu-diagnostics.sh
./gpu-diagnostics.sh > gpu-out.txt
```

---

## 𐌱𐍉𐌺𐍉𐍃 — *Bōkōs* (Files)

| 𐍆𐌹𐌻𐌿 · *Filu* (File)        | 𐌹𐌽𐌺𐌹𐌻𐌸𐍉 · *Inkilþō* (Purpose)             |
| ----------------------------- | ---------------------------------------------- |
| `gothic_translator.py`        | Gutiska gameljands · *Gothic translator*       |
| `gothicize`                   | Straumiu-sīleins Gutiska · *Gothic filter*     |
| `bless`                       | Bēteins-sīleins · *Blessing filter*            |
| `auscultation.sh`             | Hausjands baúrgs · *System listener*           |
| `auscultation_lox.lox`        | Lox-gameleins hausjandins · *Lox companion*    |
| `gpu-diagnostics.sh`          | GPU-gasaiƕands · *GPU diagnostics*             |
| `gpu-out.txt`                 | Mēleins gpu · *GPU output sample*              |
| `GOTHIC_TRANSLATOR_README.md` | Bōka gameljandins · *Translator manual*        |
| `README.md`                   | Sō bōka · *This book*                          |

---

## 𐌸𐌰𐍂𐌱𐌰 — *Þarba* (Requirements)

- **Python 3.7+** — faur þō Gutiska gameljand, `gothicize`, jah `bless`.
- **bash** — faur þō skripteis `.sh`.
- **`nvidia-smi`** aiþþau swēleika — jabai wileis GPU-frōþein.

*Python 3.7+ for the translator and filters; bash for the shell scripts;
`nvidia-smi` or similar if you wish GPU wisdom.*

---

## 𐌱𐍂𐌿𐌺𐌴𐌹𐌽𐍃 — *Brūkeins* (Usage at a Glance)

```bash
# Gutiska gameleins — Gothic translation
python3 gothic_translator.py "Þū gaggis in riqis"

# Straumiu Gutiska — Gothic stream
echo "starting service" | ./gothicize

# Straumiu bēteinai — Blessed stream
echo "fatal error" | ./bless

# Hausjan baúrgs — Listen to the system
./auscultation.sh

# Saiƕan GPU — Look upon the GPU
./gpu-diagnostics.sh
```

---

## 𐍃𐌻𐌰𐌷𐍃 — *Slahs* (License)

Frijai jah unkaúpōs. Brūkei jah inmaidei swē þus liubaiþ.

*Free and unbought. Use and modify as is pleasing to you.*

---

## 𐌷𐌰𐌹𐌻𐌾𐌰𐌽𐌳𐍃 — *Hailjands* (Author)

Gameliþs miþ hilpai Claude (claude.ai/code) jah þaim þaiei iup
brūkjand þō Linux-tewa.

*Composed with the help of Claude and those who take up the Linux
tool kit.*

> 𐌲𐌿𐌸 𐍆𐍂𐌹𐌾𐍉𐌸 𐌹𐌶𐍅𐌹𐍃 — *Guþ frijōþ izwis.* — May God love you.
