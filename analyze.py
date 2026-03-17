import os
import requests
import google.generativeai as genai
from google.generativeai import GenerativeModel

# 1. 配置 API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["DATABASE_ID"]

def call_gemini_for_random_topic():
    model = GenerativeModel("gemini-1.5-flash")
    
    # 核心指令：要求 AI 隨機挑選對象並直接產出標題與內容
    prompt = """
    任務：請隨機挑選一位具有『獨特氛圍感』或『文字質感』的創作者（如村上春樹、Lana Del Rey、Taylor Swift、或是具備高度敘事感的漫畫家）。
    
    要求：
    1. 隨機性：每天挑選不同的對象，不要重複。
    2. 格式：請嚴格遵守以下格式輸出，不要有額外廢話：
       TITLE: [創作者姓名] - [具體作品名稱]
       CONTENT: [以娥蘇拉勒瑰恩sterring the craft的角度與方法，針對該作品寫作技巧、意象運用、或敘事結構等等內容做深度分析]
    """
    
    response = model.generate_content(prompt)
    full_text = response.text
    
    # 解析 AI 回傳的標題與內容
    try:
        title = full_text.split("TITLE:")[1].split("CONTENT:")[0].strip()
        content = full_text.split("CONTENT:")[1].strip()
    except:
        title = "每日隨機寫作分析"
        content = full_text
        
    return title, content

def write_to_notion(title_content, analysis_text):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": { # 這是 Notion 資料庫預設的標題欄位
                "title": [{"text": {"content": title_content}}]
            },
            "分析內容": { # 請確保你的 Notion 資料庫有這個文字欄位
                "rich_text": [{"text": {"content": analysis_text[:2000]}}]
            }
        }
    }
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    # 讓 AI 決定標題與內容
    generated_title, generated_content = call_gemini_for_random_topic()
    
    print(f"AI 今日選題: {generated_title}")
    write_to_notion(generated_title, generated_content)
