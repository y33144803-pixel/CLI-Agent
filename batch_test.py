"""
Batch Test Runner - הריצה של 15 תרחישי בדיקה
"""

import os
from pathlib import Path
import openai
import csv
from datetime import datetime

# ============================================
# קרא את .env
# ============================================
env_path = Path(".env")
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

AIWALL_API_KEY = os.getenv('AIWALL_API_KEY')

if not AIWALL_API_KEY:
    raise ValueError("❌ AIWALL API Key not found!")

# ============================================
# צור OpenAI Client
# ============================================
client = openai.OpenAI(
    api_key=AIWALL_API_KEY,
    base_url="https://proxy.aiwall.org"
)

# קבל מודל זמין
models = client.models.list()
default_model = models.data[0].id
print(f"✅ משתמשים במודל: {default_model}\n")

# ============================================
# 15 תרחישי בדיקה
# ============================================
test_cases = [
    ("1", "מה כתובת ה-IP של המחשב שלי"),
    ("2", "אני רוצה למחוק קבצים עם סיומת .tmp בתיקייה downloads"),
    ("3", "לסדר את רשימת הקבצים לפי גודל מהגדול לקטן"),
    ("4", "איזה תהליכים רצים כרגע במערכת"),
    ("5", "הצג לי את תוכן התיקייה הנוכחית"),
    ("6", "בדוק את זמן המערכת"),
    ("7", "עצור את המחשב"),
    ("8", "הצג את גרסת Windows"),
    ("9", "חפש קובץ בשם test.txt"),
    ("10", "הצג את כל הדיסקים"),
    ("11", "פתח את הדפדפן"),
    ("12", "כמה זיכרון זמין במחשב"),
    ("13", "הצג קבצים מוסתרים"),
    ("14", "עצור את Chrome"),
    ("15", "הצג את כל משתנים הסביבה"),
]

# ============================================
# פונקציה להמרה
# ============================================
def get_command(instruction: str) -> str:
    """קבל פקודה מ-AIWALL"""
    try:
        response = client.chat.completions.create(
            model=default_model,
            messages=[
                {
                    "role": "system",
                    "content": "אתה עוזר שמומיר הוראות בשפה טבעית לפקודות טרמינל ב-Windows. חזר רק בפקודה עצמה, בלי הסברים או טקסט נוסף."
                },
                {
                    "role": "user",
                    "content": f"המר את ההוראה הבאה לפקודת טרמינל ב-Windows. חזר רק את הפקודה:\n{instruction}"
                }
            ],
            max_tokens=100,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ שגיאה: {str(e)}"

# ============================================
# הרץ את כל התרחישים
# ============================================
print("🚀 הרצת 15 תרחישי בדיקה...\n")
print(f"{'#':<4} {'Input':<55} {'Output':<50}")
print("=" * 112)

results = []
for num, instruction in test_cases:
    command = get_command(instruction)
    results.append({
        "num": num,
        "input": instruction,
        "output": command,
        "valid": "",
        "notes": ""
    })
    
    # הדפס את התוצאה
    input_display = instruction[:52] + "..." if len(instruction) > 52 else instruction
    output_display = command[:47] + "..." if len(command) > 47 else command
    print(f"{num:<4} {input_display:<55} {output_display:<50}")

# ============================================
# שמור לקובץ CSV
# ============================================
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"test_results_v1_{timestamp}.csv"

with open(csv_filename, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['num', 'input', 'output', 'valid', 'notes'])
    writer.writeheader()
    writer.writerows(results)

print(f"\n{'=' * 112}")
print(f"✅ התוצאות שמורות ב: {csv_filename}")
print(f"📋 עתקוד את הנתונים לגוגל שיטס והערך כל תוצאה\n")

# ============================================
# הדפס סיכום
# ============================================
print("📊 סיכום:")
print(f"   סה\"כ תרחישים: {len(results)}")
print(f"   מודל: {default_model}")
print(f"   זמן: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")