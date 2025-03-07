from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

app = Flask(__name__)

genai.configure(api_key="AIzaSyA-0rkCfbueku01YoBpVlktuxKZmqd7Z2U")  # Replace with your Gemini API key
model = genai.GenerativeModel("gemini-1.5-flash")
history = ''''''
@app.route('/')
def index():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    global history
    prompt = "Role : System, Content : You have to approach the user politely and always reply in a sweet tone of english. Reply in short. Approach the user positively and in a jolly way with anything the user requests you"
    user_input = request.json.get("message")
    prompt += f' refer this History to keep track of continous conversations. Do not show this in the chat: {history}'
    prompt += f'Role : user, Content :{user_input}'
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        response = model.generate_content(prompt)
        bot_reply = response.text if response.text else "Sorry, I couldn't understand that."
        
    except Exception as e:
        bot_reply = "Error processing request."
        print("Error:", str(e))
    history += f'{user_input},{bot_reply}'
    return jsonify({"reply": bot_reply})

if __name__ == '__main__':
    app.run(port = 5005,debug=True)
  