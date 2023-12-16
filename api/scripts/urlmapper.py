from newspaper import Article
import nltk

#A new article from TOI

url = 'https://news.google.com/rss/articles/CBMicmh0dHBzOi8vd3d3Lm1pbGxlbm5pdW1wb3N0LmluL2JlbmdhbC90bWMtc251YnMtYmpwLWFmdGVyLWZsaWdodC1jYXJyeWluZy1vdmVyLTEwMC10bWMtbGVhZGVycy13YXMtY2FuY2VsbGVkLTUzNDkzONIBdmh0dHBzOi8vd3d3Lm1pbGxlbm5pdW1wb3N0LmluL2FtcC9iZW5nYWwvdG1jLXNudWJzLWJqcC1hZnRlci1mbGlnaHQtY2Fycnlpbmctb3Zlci0xMDAtdG1jLWxlYWRlcnMtd2FzLWNhbmNlbGxlZC01MzQ5Mzg?oc=5&hl=en-IN&gl=IN&ceid=IN:en'
#For different language newspaper refer above table

def get_summary_of_particular_news(url):
    nltk.download('punkt')
    final_dict = {}
    toi_article = Article(url, language="en") # en for English

    #To download the article
    toi_article.download()

    #To parse the article
    toi_article.parse()

    #To perform natural language processing ie..nlp
    toi_article.nlp()
    
    #To extract title
    final_dict['Title'] = toi_article.title
  
    #  "Article's image:"
    final_dict['Image'] = toi_article.top_image

    #To extract text Article's Text:
    final_dict['main_text'] = toi_article.text
   
    #To extract summary Article's Summary:
    final_dict['Summary_article'] = toi_article.summary
    final_dict['keywords_article'] = toi_article.keywords


    # Article's publish_date:"
    final_dict['publish_date'] = toi_article.publish_date
    
    print(final_dict)
    return final_dict



