import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)


# 把调用 AI 的逻辑封装成一个函数，方便网页调用
def get_ai_reply(product_info):
    url = "https://api.deepseek.com/chat/completions"
    my_api_key = os.getenv("DEEPSEEK_KEY")
    headers = {
        "Authorization": f"Bearer {my_api_key}",
        "Content-Type": "application/json"
    }
    prompt = f"""
    请作为小红书爆款文案专家，帮我改写以下产品介绍。
    要求：
    1. 必须带夸张的标题。
    2. 多用Emoji表情。
    3. 最后加上5个热门标签。
    产品原始信息：{product_info}
    """
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    # 如果报错，直接把报错信息返回，防止网页崩溃
    if "choices" not in result:
        return f"调用失败: {result}"
    return result["choices"][0]["message"]["content"]


# 页面路由，允许 GET（打开网页）和 POST（提交表单）
@app.route("/", methods=["GET", "POST"])
def home():
    ai_text = ""  # 存放 AI 生成的文本

    # 如果用户点击了提交按钮（发出了 POST 请求）
    if request.method == "POST":
        # 获取网页上叫 "product" 的输入框里的内容
        user_input = request.form.get("product", "")
        if user_input:
            ai_text = get_ai_reply(user_input)  # 调用刚才的函数

    # 返回一个 HTML 网页给用户
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI 爆款文案生成器</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial; max-width: 600px; margin: 50px auto; }}
            textarea {{ width: 100%; height: 100px; padding: 10px; }}
            button {{ padding: 10px 20px; background-color: #ff2442; color: white; border: none; cursor: pointer; }}
            .result {{ margin-top: 20px; padding: 15px; background-color: #f9f9f9; border-left: 4px solid #ff2442; white-space: pre-wrap; }}
        </style>
    </head>
    <body>
        <h1>🔥 小红书爆款文案生成器</h1>
        <form method="POST">
            <textarea name="product" placeholder="请在这里输入你的产品介绍...">{request.form.get('product', '')}</textarea>
            <br><br>
            <button type="submit">一键生成文案</button>
        </form>

        <!-- 如果 AI 生成了文本，就显示在这个框里 -->
        {"<div class='result'>" + ai_text + "</div>" if ai_text else ""}
    </body>
    </html>
    """


if __name__ == "__main__":
