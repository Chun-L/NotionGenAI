import os
import requests
import datetime
from google import genai  # 切換到新的 SDK

# 1. 配置 API
# 注意：新版 SDK 使用不同的初始化方式
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["DATABASE_ID"]

def call_gemini_for_random_topic():
    # 使用目前最穩定的模型名稱 'gemini-2.0-flash' 或 'gemini-1.5-flash'
    model_id = "gemini-3-flash-preview" 
    
    prompt = """
    任務：請隨機挑選一位具有『獨特氛圍感』或『文字質感』的創作者（如村上春樹、Lana Del Rey、Taylor Swift、或是具備高度敘事感的漫畫家）。
    
    要求：
    1. 隨機性：每天挑選不同的對象，不要重複。
    2. 格式：請嚴格遵守以下格式輸出，不要有額外廢話：
       TITLE: [創作者姓名] - [具體作品名稱]
       AUTHOR: [創作者姓名]
       TECHNIQUES: [手法1, 手法2]
       CONTENT: [以娥蘇拉勒瑰恩sterring the craft的角度與方法，針對該作品寫作技巧、意象運用、或敘事結構等等內容做深度分析]
    
    範例：
    AUTHOR: 石黑一雄
    TECHNIQUES: 壓抑敘事, 第一人稱侷限視角
    """
    
    response = client.models.generate_content(
        model=model_id,
        contents=prompt
    )
    full_text = response.text
    
    # 解析 AI 回傳的標題與內容
    try:
        author = full_text.split("AUTHOR:")[1].split("TECHNIQUES:")[0].strip()
        techniques_raw = full_text.split("TECHNIQUES:")[1].split("CONTENT:")[0].strip()
        # 將手法字串轉為列表，例如 ["壓抑敘事", "第一人稱侷限視角"]
        tech_list = [t.strip() for t in techniques_raw.split(",")]
        
        title = full_text.split("TITLE:")[1].split("AUTHOR:")[0].strip()
        content = full_text.split("CONTENT:")[1].strip()
        
        # 合併所有標籤：作者 + 手法
        all_tags = [author] + tech_list
    except:
        title = "自動分析"
        content = full_text
        all_tags = ["未分類"]
        
    return title, content, all_tags

def write_to_notion(title_content, analysis_text,tags_list):
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": title_content}}]
            },
            "分析內容": {
                "rich_text": [{"text": {"content": analysis_text[:2000]}}]
            },
            # --- 處理多選標籤 ---
            "Tag": {
                "multi_select": [{"name": tag} for tag in tags_list if tag]
            },
            # --- 新增：寫入日期欄位 ---
            "Date": {
                "date": {"start": today_date}
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    
    # --- 偵錯核心開始 ---
    if response.status_code != 200:
        print(f"❌ 寫入失敗，狀態碼：{response.status_code}")
        print("🔍 詳細錯誤訊息：")
        print(response.json())  # 這行會印出 Notion 具體討厭哪裡
    else:
        print("✅ 成功寫入 Notion！")
    # --- 偵錯核心結束 ---
    return response.status_code

if __name__ == "__main__":
    # 加入這行來偵錯：
    #for m in client.models.list():
     #   print(f"可用模型: {m.name}")

    
    # 1. 修改這裡，增加一個變數來接收標籤列表 (tags)
    generated_title, generated_content, generated_tags = call_gemini_for_random_topic()
    
    print(f"AI 今日選題: {generated_title}")
    print(f"標籤內容: {generated_tags}")
    
    # 2. 同時也要記得把標籤傳給寫入函數
    status = write_to_notion(generated_title, generated_content, generated_tags)
    
    if status == 200:
        print("成功寫入 Notion！")
    else:
        print(f"寫入失敗，狀態碼：{status}")


