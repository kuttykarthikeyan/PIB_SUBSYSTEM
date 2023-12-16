import fitz,os
from tqdm import tqdm
from ultralytics import YOLO
import cv2
import re
import shutil
from pathlib import Path
import concurrent.futures
from googletrans import Translator
import json
import pandas as pd
import spacy
import easyocr
from textblob import TextBlob
from nltk.tokenize import sent_tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

language_selection_dict = { "english_newspapers" : 'en' ,'telugu_newspapers' : 'te','hindi_newspapers':'hi' }

def delete_contents_of_directory(directory_path):
    try:
        # Remove all files and subdirectories
        shutil.rmtree(directory_path)
        
        # Recreate an empty directory
        os.mkdir(directory_path)
        
        print(f"Contents of '{directory_path}' deleted successfully.")
    except Exception as e:
        print(f"Error: {e}")

def analyze_sentiments(descriptions):
    results = []

    for text in descriptions:
        analyzer = SentimentIntensityAnalyzer()
        sentiment_score = analyzer.polarity_scores(text)
        sentiment_intensity = sentiment_score['compound']

        if sentiment_intensity >= 0.3:
            sentiment = "POSITIVE"
        elif sentiment_intensity <= -0.5:
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"

        results.append([sentiment, sentiment_intensity])

    return results

def clean_text(text,lang):
    global language_selection_dict
    df = {}
    # Remove unwanted characters and extra spaces
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    remove_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    blob = TextBlob(remove_text)
    cleaned_text = str(blob.correct())
    if is_government_related(cleaned_text):

        sentences = sent_tokenize(cleaned_text)
        sentiment_list = analyze_sentiments(sentences)
        sentences = language_translation(sentences,lang)
        df["full_text"] = cleaned_text
        df["sentances"] = sentences
        sen_result_list = [ i[0] for i in sentiment_list]
        df['SENTIMENT_ANALYSIS_RESULT'] = [ i[0] for i in sentiment_list]
        df['SENTIMENT_ANALYSIS_INTENSITY'] = [ i[1] for i in sentiment_list]
        df['positive_sentances'] = [ i for i,j in zip(sentences,sen_result_list) if j == "POSITIVE" ]
        df['negative_sentances'] = [ i for i,j in zip(sentences,sen_result_list) if j == "NEGATIVE" ]
        df['neutral_sentances'] = [ i for i,j in zip(sentences,sen_result_list) if j == "NEUTRAL" ]
        
        return df
    else:
        return False

def is_government_related(news_text):
    # List of government-related keywords
    government_keywords = [
        'government', 'governance', 'public service', 'public office', 'public sector', 'public policy',
        'political', 'politics', 'politician', 'democracy', 'election', 'political party', 'citizen', 'civic',
        'state', 'national', 'federal', 'municipal', 'local government', 'public official', 'public servant',
        'executive', 'administration', 'president', 'prime minister', 'cabinet', 'minister', 'secretary',
        'commissioner', 'governor', 'mayor', 'official', 'authority', 'policy maker', 'bureaucrat', 'regulator',
        'legislator', 'lawmaker', 'parliamentarian', 'representative', 'senator', 'congressman', 'congresswoman',
        'assemblyman', 'assemblywoman', 'diplomat', 'embassy', 'consulate', 'diplomacy', 'ambassador', 'foreign affairs',
        'international relations', 'treaty', 'summit', 'conference', 'convention', 'protocol', 'trade agreement',
        'bilateral', 'multilateral', 'trilateral', 'executive order', 'presidential decree', 'government agency',
        'department', 'ministry', 'bureau', 'office', 'commission', 'board', 'authority', 'committee', 'task force',
        'regulatory body', 'ombudsman', 'civil service', 'treasury', 'finance', 'budget', 'taxation', 'education',
        'health', 'public health', 'defense', 'national defense', 'justice', 'judiciary', 'law enforcement',
        'homeland security', 'border control', 'immigration', 'customs', 'transportation', 'infrastructure',
        'agriculture', 'environment', 'natural resources', 'energy', 'power', 'labor', 'employment', 'unemployment',
        'housing', 'urban development', 'rural development', 'commerce', 'trade', 'business', 'industry', 'technology',
        'information', 'communication', 'telecommunications', 'internet', 'interior', 'veterans affairs',
        'social services', 'welfare', 'social security', 'culture', 'arts', 'heritage', 'tourism', 'sports', 'recreation',
        'science', 'research', 'development', 'innovation', 'sustainability', 'climate change', 'foreign aid', 'aid',
        'human rights', 'civil liberties', 'constitution', 'constitutional', 'policy analysis', 'government program',
        'government initiative', 'public initiative', 'public project', 'government expenditure', 'public spending',
        'government revenue', 'public funds', 'government debt', 'public debt', 'public finance', 'political science'
    ]
    
    nlp = spacy.load("en_core_web_sm")

    doc = nlp(news_text)

    for ent in doc.ents:
        if ent.label_ in ["ORG", "PERSON", "GPE"]:
            return True

    for token in doc:
        if token.text.lower() in government_keywords:
            return True

    return False

def image_to_text_OCR(image_path):
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    text = pytesseract.image_to_string(image=image_path)
    return text

def language_translation(input_string,target_lag):
    language = {'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar', 'armenian': 'hy', 'azerbaijani': 'az', 'basque': 'eu', 'belarusian': 'be', 'bengali': 'bn', 'bosnian': 'bs', 'bulgarian': 'bg', 'catalan': 'ca', 'cebuano': 'ceb', 'chichewa': 'ny', 'chinese (simplified)': 'zh-cn', 'chinese (traditional)': 'zh-tw', 'corsican': 'co', 'croatian': 'hr', 'czech': 'cs', 'danish': 'da', 'dutch': 'nl', 'english': 'en', 'esperanto': 'eo', 'estonian': 'et', 'filipino': 'tl', 'finnish': 'fi', 'french': 'fr', 'frisian': 'fy', 'galician': 'gl', 'georgian': 'ka', 'german': 'de', 'greek': 'el', 'gujarati': 'gu', 'haitian creole': 'ht', 'hausa': 'ha', 'hawaiian': 'haw', 'hebrew': 'he', 'hindi': 'hi', 'hmong': 'hmn', 'hungarian': 'hu', 'icelandic': 'is', 'igbo': 'ig', 'indonesian': 'id', 'irish': 'ga', 'italian': 'it', 'japanese': 'ja', 'javanese': 'jw', 'kannada': 'kn', 'kazakh': 'kk', 'khmer': 'km', 'korean': 'ko', 'kurdish (kurmanji)': 'ku', 'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la', 'latvian': 'lv', 'lithuanian': 'lt', 'luxembourgish': 'lb', 'macedonian': 'mk', 'malagasy': 'mg', 'malay': 'ms', 'malayalam': 'ml', 'maltese': 'mt', 'maori': 'mi', 'marathi': 'mr', 'mongolian': 'mn', 'myanmar (burmese)': 'my', 'nepali': 'ne', 'norwegian': 'no', 'odia': 'or', 'pashto': 'ps', 'persian': 'fa', 'polish': 'pl', 'portuguese': 'pt', 'punjabi': 'pa', 'romanian': 'ro', 'russian': 'ru', 'samoan': 'sm', 'scots gaelic': 'gd', 'serbian': 'sr', 'sesotho': 'st', 'shona': 'sn', 'sindhi': 'sd', 'sinhala': 'si', 'slovak': 'sk', 'slovenian': 'sl', 'somali': 'so', 'spanish': 'es', 'sundanese': 'su', 'swahili': 'sw', 'swedish': 'sv', 'tajik': 'tg', 'tamil': 'ta', 'telugu': 'te', 'thai': 'th', 'turkish': 'tr', 'ukrainian': 'uk', 'urdu': 'ur', 'uyghur': 'ug', 'uzbek': 'uz', 'vietnamese': 'vi', 'welsh': 'cy', 'xhosa': 'xh', 'yiddish': 'yi', 'yoruba': 'yo', 'zulu': 'zu'}
    googletrans_translator = Translator()
    googletrans_result = googletrans_translator.translate(input_string,src= "auto", dest= language[target_lag])
    return googletrans_result.text

def ocr_easy(image_path,lang):
    reader = easyocr.Reader([lang])  
    results = reader.readtext(image_path)
    
    telugu_text = []
    for detection in results:
        text = detection[1]
        telugu_text.append(text)

    return "".join(telugu_text)

def e_print_function(newspaper_lang):
    
    global language_selection_dict

    model = YOLO(r"model_ocr\model_article_only.pt")
    classes_list = model.names


    folder_path = Path("pdfs/" + newspaper_lang)
    files_name_folder = [f.name for f in folder_path.iterdir() if f.is_file()]

    for file_name in files_name_folder[0:1]:
        
        doc = fitz.open("pdfs/" + newspaper_lang +"/"+ file_name)
        os.makedirs("OCR_results/" + file_name + "_pdf", exist_ok=True)
        
        dict_data = {}
        pages_dict = {}
        
        for id, page in enumerate(doc):
            
            pix = page.get_pixmap(matrix=fitz.Identity, dpi=None, colorspace=fitz.csRGB, clip=None, annots=True)
            
            pdf_img_path  = "pdfs/" + newspaper_lang + "/samplepdfimage-%i.jpg" % page.number
            pix.save(pdf_img_path)
            input_image = cv2.imread(pdf_img_path)

            results = model.predict(source=pdf_img_path, conf=0.20,iou=0.8)
            results_image = results[0].plot()
            
            os.makedirs("OCR_results/" + file_name + "_pdf" + "/page_"+str(id+1),exist_ok=True)
            cv2.imwrite("OCR_results/" + file_name + "_pdf" + "/page_"+str(id+1)+"/full_image.jpg", results_image)

            boxes = results[0].boxes.numpy().xyxy
            classes = results[0].boxes.numpy().cls
            
            img_num = 1
            art_num = 1
            art_dict = {}
            
            for b, c in zip(boxes, classes):
                if c == 0:
                    x1, y1 = b[0], b[1]  # Top-left corner
                    x2, y2 = b[2], b[3]  # Bottom-right corner
                    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                    cropped_image = input_image[y1:y2, x1:x2]
                    
                    if newspaper_lang == 'english_newspapers':
                        image_to_text = image_to_text_OCR(cropped_image)
                        
                    if newspaper_lang == 'telugu_newspapers':
                        image_to_text = ocr_easy(cropped_image,language_selection_dict[newspaper_lang])
                        image_to_text = language_translation(image_to_text,'english')
                    if newspaper_lang == 'hindi_newspapers':
                        image_to_text = ocr_easy(cropped_image,language_selection_dict[newspaper_lang])
                        image_to_text = language_translation(image_to_text,'english')
                        
                    analysis_text = clean_text(image_to_text,newspaper_lang)
                    
                    if analysis_text is not False:
                        art_dict["article_" + str(art_num)] = analysis_text
                        cv2.imwrite("OCR_results/" + file_name + "_pdf" + "/page_"+str(id+1)+"/article_" + str(art_num) + ".png", cropped_image)
                        art_num += 1
                
            
                # if c == 1:
                    
                #     x1, y1 = b[0], b[1]  # Top-left corner
                #     x2, y2 = b[2], b[3]  # Bottom-right corner
                #     x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                #     cropped_image = input_image[y1:y2, x1:x2]
                    
                #     article_text = image_to_text_OCR(cropped_image)
                #     cv2.imwrite("OCR_results/" + file_name + "_pdf" + "/page_"+str(id+1)+"/image_" + str(img_num) + ".png", cropped_image)
                #     img_num += 1
                
            
            pages_dict["page_"+str(id+1)] = art_dict    
            art_num = 1       
            img_num = 1
            art_dict = {}
           
            
        dict_data[file_name] = pages_dict
        pages_dict = {}    
            
        json_string = json.dumps(dict_data, indent=2)
        with open("OCR_results/" + file_name  +"_pdf/json_result.json", "w") as json_file:
            json.dump(json_string, json_file, indent=2)
          
    print("Successfully completed " + newspaper_lang +" !!!!!!!!!!!!!!!!!!!!!!")


        
def main():
    languages = ["english_newspapers", "telugu_newspapers", "hindi_newspapers"]
    delete_contents_of_directory(r"OCR_results")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(e_print_function, lang) for lang in languages]

        # Wait for all tasks to complete
        concurrent.futures.wait(futures)

main()