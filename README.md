# 🩸 Image-to-CSV Data Extractor

Extract structured data from card images (donor cards, ID cards, etc.) into CSV or Excel files using Claude Vision AI.

---

## 📁 Project Structure

```
image_to_csv/
│
├── main.py                  # ▶ Entry point — run this
├── requirements.txt         # Dependencies
├── .env.example             # API key template
├── .env                     # Your API key (create from .env.example)
│
├── config/
│   └── fields.json          # Define what fields to extract
│
├── modules/
│   ├── image_loader.py      # Load & preprocess images
│   ├── extractor.py         # Claude Vision AI extraction
│   └── exporter.py          # Save to CSV or Excel
│
├── input_images/            # 📷 Drop your card images here
├── output/                  # 📄 Output files saved here
└── tests/
    └── test_setup.py        # Verify your setup
```

---

## ⚙️ Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your API key
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
# Get one at: https://console.anthropic.com
```

### 3. Verify setup
```bash
python tests/test_setup.py
```

---

## 🚀 Usage

### Extract from a folder of images → CSV
```bash
python main.py --input ./input_images/ --config ./config/fields.json
```

### Extract from a single image → Excel
```bash
python main.py --input ./input_images/card1.jpg --format excel
```

### Override fields dynamically (no config edit needed)
```bash
python main.py --input ./input_images/ --fields name age blood_group phone
```

### Preview extracted data in terminal before saving
```bash
python main.py --input ./input_images/ --preview
```

### Debug mode (saves preprocessed images)
```bash
python main.py --input ./input_images/ --debug
```

---

## ⚙️ Dynamic Field Configuration

Edit `config/fields.json` to change what data gets extracted:

**For Blood Donor Cards:**
```json
{
  "output_file": "donors",
  "output_format": "csv",
  "fields": ["name", "age", "sex", "blood_group", "address", "phone"]
}
```

**For Employee ID Cards:**
```json
{
  "output_file": "employees",
  "output_format": "excel",
  "fields": ["employee_id", "name", "department", "designation", "email"]
}
```

**For Student Cards:**
```json
{
  "output_file": "students",
  "output_format": "csv",
  "fields": ["student_id", "name", "faculty", "year", "roll_number"]
}
```

Just change the config — the system adapts automatically!

---

## 📋 Output Example

| name | age | sex | blood_group | address | phone | _source_file |
|------|-----|-----|-------------|---------|-------|--------------|
| Ram Bahadur | 28 | Male | O+ | Kathmandu | 9841XXXXXX | card1.jpg |
| Sita Sharma | 34 | Female | A+ | Lalitpur | 9851XXXXXX | card2.jpg |
