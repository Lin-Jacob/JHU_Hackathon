from openai import OpenAI 
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import json
import base64

load_dotenv()

app = Flask(__name__)


def get_questions(country: str):
    api_key = os.getenv('API_KEY')
    model = "chatgpt-4o-latest"

    client = OpenAI(
        api_key=api_key,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content":
             '''You are a world disease expert and know what major diseases are present in each country or area in the world. As a expert
            you want to figure out what type of disease a person might contract after visiting the given country. The patient will tell you what country
            they have visited and you have to ask questions about the most popular disease in that given country.
            Dont ask any questions about medications or vaccinations.
            
            Make the questions in the following format:
            - If the question is a Yes or No question, make sure to add something along the lines of "If yes, explain, if no, put No"
            - Ask at least 7 or more questions
            JSON TEMPLATE:
            {
            name: Any name relating to the question,
            elements: [
                {
                    type: "radiogroup",
                    name: Name,
                    title: QUESTION,
                    isRequired: true or false,
                    choices: SurveryJS choices IF NEEDED
                },
            ]
            }'''
            },
            {
                "role": "user",
                "content": f"I went to {country}"
            }
        ],
        temperature=0.0,
        response_format={"type": "json_object"}
    )

    questions = response.choices[0].message.content
    return questions


def get_answer(answers):
    api_key = os.getenv('API_KEY')
    model = "chatgpt-4o-latest"

    client = OpenAI(
        api_key=api_key,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content":
             '''You are a world disease expert and know what major diseases are present in each country or area in the world. As a expert
            you want to figure out what type of disease a person might contract after visiting the given country. The patient will give you a list of
            questions and answers, your task is to first figure out the severity of each question and the answer.
            You should return the answer in this JSON format:
            {
            rating: float number between 0 and 10, where 0 is not severe and 10 is super severe,
            reason: Give a brief reason of why the person should not enter.    
            }'''},
            {
                "role": "user",
                "content": f"The country is {answers['country']}. {answers['answer']}"
            }
        ],
        temperature=0.0,
        response_format={"type": "json_object"}
    )

    decision = response.choices[0].message.content
    return decision
# ans = {
#     'answer': "Country: Africa. Have you experienced any fever? Yes. Do you have any cuts or wounds? No. Have you had contact with sick individuals? Sometimes. Do you have a persistent cough? Yes. Are you currently experiencing fatigue? Sometimes."
# }
# print(get_answer(ans))


def process_passport(image):
    base64_image = base64.b64encode(image).decode("utf-8")

    api_key = os.getenv('API_KEY')

    model = "chatgpt-4o-latest"

    client = OpenAI(
        api_key=api_key,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content":
                '''You are a TSA Agent and asked to scan the necessary information from the given passports and output into a JSON format
                We only want the following fields:
                - First_Name : first name only
                - Last_Name : last name only
                - DOB : Date of Birth (Month - Date - Year) in string
                - Passport_Num : passport number, or whatever the unique passport identifier is
                - Sex : male or female
                '''},
            {"role": "user", "content": [
                {"type": "text", "text": "Scan this passport"},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"}
                 }
            ]}
        ],
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    response = response.choices[0].message.content

    return response


@app.route('/process_passport', methods=['POST'])
def process():
    image_binary = request.files['image'].read()
    response = process_passport(image_binary)
    return jsonify(response)

@app.route('/get_questions', methods=['POST'])
def get_questions_api():
    data = request.json
    
    country : str = data['country']

    questions = get_questions(country)

    return jsonify(questions)

@app.route('/get_answer', methods=['POST'])
def get_answer_api():
    data = request.json

    answer = get_answer(data)

    return jsonify(answer)

if __name__ == '__main__':
    app.run(port=8080)