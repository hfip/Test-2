# main.py
import os
import re
import base64
import urllib.parse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# استدعاء الفيتشر الخارق للتخطي بناءً على ملفاتك الرسمية
from scrapling.fetchers import StealthyFetcher

app = FastAPI(title="Universal Scrapling Solver API")

class UrlPayload(BaseModel):
    url: str

class SearchPayload(BaseModel):
    base_url: str
    query: str

@app.post("/solve")
async def solve_url(payload: UrlPayload):
    try:
        target_url = payload.url
        print(f"[Scrapling] Executing Stealthy Fetch for: {target_url}")
        
        # إطلاق الـ StealthyFetcher المحصن بـ Patchright لتخطي كلوود فلير تلقائياً بناءً على سورس ملفاتك
        response = StealthyFetcher.fetch(
            url=target_url,
            headless=True,
            disable_resources=True, # إسقاط الصور والملفات غير الضرورية لسرعة صاروخية
            block_ads=True
        )
        
        if not response or not response.text:
            raise HTTPException(status_code=500, detail="Failed to retrieve content from target")
            
        return {"html": response.text, "status": response.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_reverse")
async def search_reverse(payload: SearchPayload):
    try:
        search_query = payload.query
        custom_base = payload.base_url.rstrip('/')
        
        # تركيب رابط البحث ديناميكياً بناءً على الموقع المرسل من الإضافة
        search_url = f"{custom_base}/find/?q={urllib.parse.quote(search_query)}"
        print(f"[Scrapling] Executing Universal Search for: {search_url}")
        
        response = StealthyFetcher.fetch(
            url=search_url,
            headless=True,
            disable_resources=True,
            block_ads=True
        )
        
        if not response or not response.text:
            return {"target_url": ""}
            
        html = response.text
        # كشط أول نتيجة مطابقة تظهر في الشبكة بشكل عام
        match = re.search(r'href=["\'](' + re.escape(custom_base) + r'/[^"\']+)["\']', html)
        if match:
            return {"target_url": match.group(1)}
                
        return {"target_url": ""}
    except Exception as e:
        return {"target_url": ""}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
