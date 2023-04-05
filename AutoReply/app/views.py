import openai
from rest_framework import views
# from rest_framework.response import Response
from django.http import JsonResponse

from langdetect import detect
from textblob import TextBlob
import nltk



openai.api_key = "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"

# =========== XXXXXXXXXXXXXX ==============
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch

def summarize_text(input_text):
    
    tokenizer = T5Tokenizer.from_pretrained('t5-small')
    model = T5ForConditionalGeneration.from_pretrained('t5-small')
    input_ids = tokenizer.encode(input_text, return_tensors='pt')
    output = model.generate(input_ids, max_length=50, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(output[0], skip_special_tokens=True)
    
    return summary


class AutoReplyView(views.APIView):
    def post(self, request):
        message = request.data.get("message", "")
        prompt = f"Suggest an auto-reply message for the following email:\n\n{message}\n\n"
        completions = openai.Completion.create(
            engine="text-curie-001",
            prompt=prompt,
            max_tokens=500,
            n=5,
            stop=None,
            temperature=0.7,
        )
     
        suggestions = completions.choices
        list = []
        for i in range(5):
            n = suggestions[i].text.strip().split("\n")
            
            sentences = nltk.sent_tokenize(n[0])
            for i in sentences:
                if 'Hi there!' or 'Thanks for considering us!' or 'Thank you for your interest!' or 'Thank you for reaching out' in i:
                    sentences.remove(i)
            
            paragraph = ' '.join(sentences)
            response = summarize_text(paragraph)
            print('response = '+response)
            if response != '' or ' ':
                language = detect(response)
                if language != 'en':
                    blob = TextBlob(response)
                    translated_text = blob.translate(from_lang=language, to='en')
                    list.append(str(translated_text))
                else :
                    list.append(response)

        return JsonResponse({"suggestions": list})


