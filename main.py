"""
Natural Language to CLI Command Converter
Iteration 3 - Version 3 (V3) - Enhanced Prompt with Better Security
"""

import os
from pathlib import Path
import openai
import gradio as gr

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
                print(f"✅ טען: {key.strip()}")

AIWALL_API_KEY = os.getenv('AIWALL_API_KEY')

print(f"🔍 .env קיים: {env_path.exists()}")
print(f"✅ AIWALL_API_KEY נטען: {bool(AIWALL_API_KEY)}\n")

if not AIWALL_API_KEY:
    raise ValueError("❌ AIWALL API Key not found in .env file!")

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
# Prompt Engineering - All Versions
# ============================================

# VERSION 1 (ORIGINAL - פרומפט בסיסי)
# """
# SYSTEM_PROMPT_V1 = אתה עוזר שמומיר הוראות בשפה טבעית לפקודות טרמינל ב-Windows. 
# חזר רק בפקודה עצמה, בלי הסברים או טקסט נוסף.
# אם ההוראה לא ברורה, החזר הודעת שגיאה בעברית.

# תוצאות V1:
# - ✅ הצלחה: 14/15 (93.3%)
# - ❌ כישלון: 1/15
# """

# # VERSION 2 (FAILED - ניסיון ראשון לחסימה)
# """
# SYSTEM_PROMPT_V2 = אתה עוזר שמומיר הוראות בשפה טבעית לפקודות טרמינל ב-Windows.

# חוקים חובה:
# 1. חזר רק בפקודה עצמה, בלי הסברים או טקסט נוסף.
# 2. העדף פקודות פשוטות וקצרות על מורכבות.
# 3. אם יש בחירה בין pipe (|) לפקודה פשוטה יותר, בחר בפשוטה.

# פקודות אסורות — דחה בנימוקים בעברית:
# - del, erase, rmdir, format, fdisk (מחיקה)
# - shutdown, restart, logoff (כיבוי)
# - taskkill /F (הפסקה בכוח)
# - reg delete (שינוי רישום)
# - takeown, icacls (שינוי הרשאות)

# תוצאות V2:
# - ✅ הצלחה: 11/15 (73.3%)
# - ❌ כישלון: 4/15
# - בעיה: המודל התעלם מהנחיות החסימה
# """

# VERSION 3 (IMPROVED - חסימה חזקה יותר)
SYSTEM_PROMPT_V3 = """אתה עוזר שמומיר הוראות לפקודות טרמינל ב-Windows בטוח.

** חוק עיקרי: NEVER return dangerous commands **

דחה בנוחות מלאה את הפקודות הבאות:
- כל פקודת מחיקה: del, erase, rmdir, format, deltree
- כל פקודת כיבוי: shutdown, restart, logoff, sleep
- taskkill /F, taskkill /IM, taskkill עם /F
- reg delete, reg clear
- takeown, icacls, attrib

כאשר משתמש מבקש פקודה מסוכנת, תן תשובה ברורה:
- "לא יכול להעביר פקודות מחיקה"
- "לא יכול להעביר פקודות כיבוי"
- "לא יכול להעביר פקודות הפסקת תהליכים בכוח"

פקודות בטוחות שמומלצות:
- ipconfig (IP)
- tasklist (תהליכים)
- dir (קבצים)
- time /t (זמן)
- winver (גרסה)
- wmic OS get FreePhysicalMemory (זיכרון)

חזר ONLY בפקודה, ללא טקסט או הסברים."""

USER_PROMPT_TEMPLATE_V3 = """המר את ההוראה הבאה לפקודת טרמינל ב-Windows:
{instruction}

חזר רק בפקודה, ללא הסברים."""

# ============================================
# פונקציה להמרה
# ============================================
def natural_language_to_command(text):
    """
    המר הוראה בשפה טבעית לפקודת טרמינל באמצעות AIWALL
    
    Args:
        text (str): הוראה בעברית או אנגלית
    
    Returns:
        str: פקודת טרמינל או הודעת שגיאה
    """
    if not text.strip():
        return "❌ שגיאה: הוראה ריקה. אנא הזן הוראה תקינה."
    
    try:
        user_message = USER_PROMPT_TEMPLATE_V3.format(instruction=text)
        
        response = client.chat.completions.create(
            model=default_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_V3},
                {"role": "user", "content": user_message}
            ],
            max_tokens=100,
            temperature=0
        )
        
        command = response.choices[0].message.content.strip()
        return command
    
    except Exception as e:
        return f"❌ שגיאה: {str(e)}"

# ============================================
# ממשק Gradio
# ============================================
def create_interface():
    """צור ממשק Gradio"""
    
    with gr.Blocks(title="NL to CLI Converter - V3") as demo:
        gr.Markdown("# 🖥️ המירי הוראה לפקודת טרמינל")
        gr.Markdown("הזן הוראה בעברית או אנגלית, והן תומרה לפקודת Windows (SAFE MODE - V3)")
        
        # Input
        instruction_input = gr.Textbox(
            label="📝 הוראה בשפה טבעית",
            placeholder="לדוגמה: 'מה כתובת ה-IP של המחשב שלי'",
            lines=2
        )
        
        # Output
        command_output = gr.Textbox(
            label="💻 פקודת CLI",
            interactive=False,
            lines=2
        )
        
        # Button
        submit_btn = gr.Button("🔄 להמיר", variant="primary")
        submit_btn.click(
            natural_language_to_command,
            inputs=[instruction_input],
            outputs=[command_output]
        )
        
        # Examples
        gr.Examples(
            examples=[
                ["מה כתובת ה-IP של המחשב שלי"],
                ["לסדר את הקבצים לפי גודל"],
                ["איזה תהליכים רצים"],
                ["הצג את גרסת Windows"],
                ["כמה זיכרון זמין"],
            ],
            inputs=[instruction_input],
            outputs=[command_output],
            fn=natural_language_to_command,
            cache_examples=False,
        )
    
    return demo

# ============================================
# Main Entry Point
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Natural Language to CLI Agent - VERSION 3 (V3)")
    print("=" * 60)
    print(f"✅ Prompt Version: V3 (Enhanced Security)")
    print(f"✅ Model: {default_model}")
    print(f"✅ Safe Mode: ENABLED (dangerous commands blocked)")
    print(f"🌐 Interface: http://127.0.0.1:7861\n")
    
    demo = create_interface()
    demo.launch(share=False, server_name="127.0.0.1", server_port=7861)