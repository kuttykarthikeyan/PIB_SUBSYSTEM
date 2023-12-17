from tqdm import tqdm
from multiprocessing import Pool
from tqdm import tqdm
import pandas as pd
from gnews import GNews
from newspaper import Article
import json
import pandas as pd
from datetime import datetime  


from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
google_news = GNews()

def sentiment_analysis(descriptions):
    list_results = []
    for text in descriptions:
        results = {}
        sen_list = ['POSITIVE','NEGATIVE','NEUTRAL']
        analyzer = SentimentIntensityAnalyzer()
        sentiment_score = analyzer.polarity_scores(text)
        sentiment_intensity = sentiment_score['compound']

        if sentiment_intensity >= 0.3:
            sentiment = "POSITIVE"
        elif sentiment_intensity <= -0.5:
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"
            
        sen_list.remove(sentiment)
        
        sentiment_intensity = abs(sentiment_intensity)
        
        results['SENTIMENT_LABEL'] = sentiment
        results[sentiment] = round(sentiment_intensity * 100,2)
        results[sen_list[0]] = 0
        results[sen_list[1]] = 0
        
        list_results.append(results)
        
        
    return list_results

def time_age_function(publist_date):
    from datetime import datetime

    # Define the target datetime
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # target_datetime = datetime.strptime(publist_date, date_format)
    target_datetime = publist_date

    # Get the current datetime
    current_datetime = datetime.now()

    # Calculate the time difference
    time_difference = current_datetime - target_datetime

    # Extract the time difference components (days, seconds, etc.)
    days = time_difference.days
    seconds = time_difference.seconds

    # Calculate hours, minutes, and remaining seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Print the time difference
    return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds ago"
    
def get_summary_of_particular_news(url):
    
    global google_news
    
    final_dict = {}
   
    toi_article = google_news.get_full_article(url)
    #  "Article's image:"
    final_dict['image'] = [ i for i in list(toi_article.images) if  i[-4:] == ".jpg" ][0]
    

    #To extract text Article's Text:
    final_dict['main_text'] = toi_article.text
    
    final_dict['summary_article'] = "none"
   

    return final_dict

def clustering_news_data_scrape_function(news_tittle,language,max_results,past_no_of_hours):
    
    global google_news
    date_format = "%a, %d %b %Y %H:%M:%S GMT"

    google_news.period =  str(past_no_of_hours)+ 'h'  # News from last 7 days
    google_news.max_results = max_results  # number of responses across a keyword
    google_news.country = 'India'  # News from a specific country 
    google_news.language = language  # News in a specific language
    google_news.exclude_websites = ['yahoo.com', 'cnn.com']
    json_resp = google_news.get_news(news_tittle + " when:"+str(past_no_of_hours)+"h")
    
    youtube_json_resp = google_news.get_news(news_tittle + " site:https://www.youtube.com" + " when:"+str(past_no_of_hours)+"h")
    if len(youtube_json_resp) != 0:
        val_d = [ pd.DataFrame([i]) for i in youtube_json_resp]
        youtube_df = pd.concat(val_d)
        youtube_df['publisher'] = [ i['title']  for i in youtube_df['publisher']]
        youtube_df['published date']  = [ datetime.strptime(i, date_format) for i in youtube_df['published date']]
        youtube_df["published time ago"] = [ time_age_function(i)  for i in youtube_df['published date']]
        youtube_df['published date'] = pd.to_datetime(youtube_df['published date'])
        youtube_df.sort_values('published date',ascending=False)
        youtube_df.columns = ['title','description','published_date','url','source_name','published_time_ago']
    else:
        youtube_df = pd.DataFrame()
    

    if len(json_resp) != 0:
        d = []
        
        for dis_1 in json_resp:
             
            try:
                particular_url_data = get_summary_of_particular_news(dis_1['url'])
                split_list = particular_url_data['main_text'].split(".") 
                split_list_analysis = sentiment_analysis(split_list)
                
                
                dict_analysis = { i:j['SENTIMENT_LABEL'] for i,j in zip(split_list,split_list_analysis)}                      

                particular_url_data['positive_sentence'] = [ i for i,j in dict_analysis.items() if j == 'POSITIVE' ]
                particular_url_data['neutral_sentence'] = [ i for i,j in dict_analysis.items() if j == 'NEUTRAL' ]
                particular_url_data['negative_sentence'] = [ i for i,j in dict_analysis.items() if j == 'NEGATIVE' ]
                
                particular_url_data['POSITIVE'] = [ i['POSITIVE'] for i in split_list_analysis]
                particular_url_data['NEUTRAL'] = [ i['NEUTRAL'] for i in split_list_analysis]
                particular_url_data['NEGATIVE'] = [ i['NEGATIVE'] for i in split_list_analysis]
                particular_url_data['cluster_sentiment_analysis_result'] = [ i['SENTIMENT_LABEL'] for i in split_list_analysis]
                
                
                dis_1.update(particular_url_data)
                dataframe_dis = pd.DataFrame([dis_1])

                d.append(dataframe_dis)
                    
            except:
                dis_1.update({'image':'none', 'main_text': dis_1['title'], 'summary_article': dis_1['title'],'positive_sentence': 'none','neutral_sentence': 'none','negative_sentence': 'none','POSITIVE':'NONE','NEUTRAL':'NONE','NEGATIVE':'NONE','cluster_sentiment_analysis_result':'NONE'})
                dataframe_dis = pd.DataFrame([dis_1])
  
                d.append(dataframe_dis)
               
        df = pd.concat(d)
        df['publisher'] = [ i['title']  for i in df['publisher']]
        df['published date']  = [ datetime.strptime(i, date_format) for i in df['published date']]
        df["published time ago"] = [ time_age_function(i)  for i in df['published date']]
        df['published date'] = pd.to_datetime(df['published date'])
        df.sort_values('published date',ascending=False)
        df['published date'] = df['published date'].astype(str)
        
        
        df.columns = ['title', 'description', 'published_date', 'url', 'publisher', 'image', 'main_text', 'summary_article', 'positive_sentence', 'neutral_sentence', 'negative_sentence','POSITIVE','NEUTRAL','NEGATIVE','cluster_sentiment_analysis_result', 'published_time_ago']
        
        return df,youtube_df
    else:
        return pd.DataFrame(),youtube_df
  
def state_wise_news_for_each_department(state,department,language,max_results,past_no_of_hours):
    global google_news
    date_format = "%a, %d %b %Y %H:%M:%S GMT"

    google_news.period =  str(past_no_of_hours)+ 'h'  # News from last 7 days
    google_news.max_results = max_results  # number of responses across a keyword
    google_news.country = 'India'  # News from a specific country 
    google_news.language = language  # News in a specific language
    google_news.exclude_websites = ['yahoo.com', 'cnn.com']
    json_resp = google_news.get_news( department + " related news in Government of " + state + " when:"+str(past_no_of_hours)+"h")


        
    if len(json_resp) != 0:
        d = []
        
        for dis_1 in json_resp:
            
            try:
                particular_url_data = get_summary_of_particular_news(dis_1['url'])
                split_list = particular_url_data['main_text'].split(".") 
                split_list_analysis = sentiment_analysis(split_list)
                dict_analysis = { i:j['SENTIMENT_LABEL'] for i,j in zip(split_list,split_list_analysis)}                      
        
                particular_url_data['positive_sentence'] = [ i for i,j in dict_analysis.items() if j == 'POSITIVE' ]
                particular_url_data['neutral_sentence'] = [ i for i,j in dict_analysis.items() if j == 'NEUTRAL' ]
                particular_url_data['negative_sentence'] = [ i for i,j in dict_analysis.items() if j == 'NEGATIVE' ]
                
                dis_1.update(particular_url_data)
                dataframe_dis = pd.DataFrame([dis_1])
                
                
                if dataframe_dis is not None:
                    d.append(dataframe_dis)
                    
            except:
                
                dis_1.update({'image':"none", 'main_text': dis_1['description'], 'summary_article': dis_1['description'],'positive_sentence': 'none','neutral_sentence': 'none','negative_sentence': 'none'})
                dataframe_dis = pd.DataFrame([dis_1])
                
                if dataframe_dis is not None:
                    d.append(dataframe_dis)
       
                  
        df = pd.concat(d)
        
        df['publisher'] = [ i['title']  for i in df['publisher']]
        df['published date']  = [ datetime.strptime(i, date_format) for i in df['published date']]
        df["published time ago"] = [ time_age_function(i)  for i in df['published date']]
        df['published date'] = pd.to_datetime(df['published date'])
        df.sort_values('published date',ascending=False)
        df['State'] = [ state for i in range(len(df))]
        df['Department'] = [ department for i in range(len(df))]
        
        # website_data,youtube_data = clustering_news_data_scrape_function(news_tittle=dis_1['title'],language="english", max_results=5, past_no_of_hours=10)
        
        list_website_data_clustering = [ ]
        list_youtube_data_clustering = [ ]
        
        for i in df['title']:
            w,y = clustering_news_data_scrape_function(news_tittle=i,language="english", max_results=5, past_no_of_hours=10)
            w = w.to_json(orient='records')
            y = y.to_json(orient='records')
            list_website_data_clustering.append(w)
            list_youtube_data_clustering.append(y)
            
        df['website_data_clustering'] = list_website_data_clustering
        df['youtube_data_clustering'] = list_youtube_data_clustering

        return df
    else:
        return []
 

# states_list = ['Delhi','Bengaluru' , 'Mumbai', 'Hyderabad', 'Chennai', 'Chandigarh', 'Kolkata', 'Bengaluru', 'Bhubaneswar', 'Ahmedabad', 'Guwahati', 'Thiruvananthpuram', 'Imphal', 'Aizawl', 'Agartala', 'Gangtok', 'Kohima', 'Shillong', 'Itanagar', 'Lucknow', 'Bhopal', 'Jaipur', 'Patna', 'Ranchi', 'Shimla', 'Raipur']
states_list = ['Delhi', 'Karnataka', 'Maharashtra', 'Telangana', 'Tamil Nadu', 'Chandigarh', 'West Bengal', 'Odisha', 'Gujarat', 'Assam', 'Kerala', 'Manipur', 'Mizoram', 'Tripura', 'Sikkim', 'Nagaland', 'Meghalaya', 'Arunachal Pradesh', 'Uttar Pradesh', 'Madhya Pradesh', 'Rajasthan', 'Bihar', 'Jharkhand', 'Himachal Pradesh', 'Chhattisgarh']
text_content = ["President's Secretariat", "Vice President's Secretariat", "Prime Minister's Office", "Cabinet", "Cabinet Committee Decisions", "Cabinet Committee on Economic Affairs (CCEA)", "Cabinet Secretariat", "Cabinet Committee on Infrastructure", "Cabinet Committee on Price", "Cabinet Committee on Investment", "AYUSH", "Other Cabinet Committees", "Department of Space", "Department of Ocean Development", "Department of Atomic Energy", "Election Commission", "Finance Commission", "Ministry of Agriculture & Farmers Welfare", "Ministry of Agro & Rural Industries",  "Ministry of Chemicals and Fertilizers", "Ministry of Civil Aviation", "Ministry of Coal", "Ministry of Commerce & Industry", "Ministry of Communications", "Ministry of Company Affairs", "Ministry of Consumer Affairs, Food & Public Distribution", "Ministry of Cooperation", "Ministry of Corporate Affairs", "Ministry of Culture", "Ministry of Defence", "Ministry of Development of North-East Region", "Ministry of Disinvestment", "Ministry of Drinking Water & Sanitation", "Ministry of Earth Sciences", "Ministry of Education", "Ministry of Electronics & IT", "Ministry of Environment, Forest and Climate Change", "Ministry of External Affairs", "Ministry of Finance", "Ministry of Fisheries, Animal Husbandry & Dairying", "Ministry of Food Processing Industries", "Ministry of Health and Family Welfare", "Ministry of Heavy Industries", "Ministry of Home Affairs", "Ministry of Housing & Urban Affairs", "Ministry of Information & Broadcasting", "Ministry of Jal Shakti", "Ministry of Labour & Employment", "Ministry of Law and Justice", "Ministry of Micro, Small & Medium Enterprises", "Ministry of Mines", "Ministry of Minority Affairs", "Ministry of New and Renewable Energy", "Ministry of Overseas Indian Affairs", "Ministry of Panchayati Raj", "Ministry of Parliamentary Affairs", "Ministry of Personnel, Public Grievances & Pensions", "Ministry of Petroleum & Natural Gas", "Ministry of Planning", "Ministry of Power", "Ministry of Railways", "Ministry of Road Transport & Highways", "Ministry of Rural Development", "Ministry of Science & Technology", "Ministry of Ports, Shipping and Waterways", "Ministry of Skill Development and Entrepreneurship", "Ministry of Social Justice & Empowerment", "Ministry of Statistics & Programme Implementation", "Ministry of Steel", "Ministry of Surface Transport", "Ministry of Textiles", "Ministry of Tourism", "Ministry of Tribal Affairs", "Ministry of Urban Development", "Ministry of Water Resources, River Development and Ganga Rejuvenation", "Ministry of Women and Child Development", "Ministry of Youth Affairs and Sports", "NITI Aayog", "PM Speech", "EAC-PM", "UPSC", "Special Service and Features", "PIB Headquarters", "Office of Principal Scientific Advisor to GoI", "National Financial Reporting Authority", "Competition Commission of India", "IFSC Authority", "National Security Council Secretariat"]

# states_list = ["Tamil Nadu",'Karnataka']
# text_content = ["Prime Minister's Office"]
    
    
# Define your functions (time_age_function and state_wise_news_for_each_department) here...

def collect_data_for_state(state):
    global text_content
    final_dataframe_list = []
    for department in text_content:
        result = state_wise_news_for_each_department(state=state, department=department, language="english", max_results=5, past_no_of_hours=5)
        if len(result) != 0:
            final_dataframe_list.append(result)
            print("------------------------------ Data taken for " + state + " for " + department + " ----------------------------------------")
        else:
            print("------------------------------ Data not came for " + state + " for " + department + " ----------------------------------------")
            
    return final_dataframe_list


if __name__ == '__main__':
    
    # Number of processes to run concurrently
    num_processes = 15  # You can adjust this based on your system's capabilities
    
    results = []
    # Using a for loop with multiprocessing
    with Pool(num_processes) as pool:
        for result in tqdm(pool.imap(collect_data_for_state, states_list), total=len(states_list)):
            results.append(result)
            

    # results = []
    # for state in states_list:
    #     val = collect_data_for_state(state=state)
    #     results.append(val)
         
    final_dataframe_list = [item for sublist in results for item in sublist if len(item) != 0]
    
    if len(final_dataframe_list) != 0:
        final_data = pd.concat([i for i in final_dataframe_list], ignore_index=True)
        
        sentiment_analysis_result = sentiment_analysis(final_data['description'].tolist())
        final_data['POSITIVE'] = [ i['POSITIVE'] for i in sentiment_analysis_result]
        final_data['NEUTRAL'] = [ i['NEUTRAL'] for i in sentiment_analysis_result]
        final_data['NEGATIVE'] = [ i['NEGATIVE'] for i in sentiment_analysis_result]
        final_data['SENTIMENT_ANALYSIS_RESULT'] = [ i['SENTIMENT_LABEL']  for i in sentiment_analysis_result]
        
        
        final_data.columns = ['title', 'description', 'published_date', 'url', 'publisher', 'image',
        'main_text', 'summary_article', 'positive_sentence', 'neutral_sentence',
        'negative_sentence', 'published_time_ago', 'state', 'department',
        'website_data_clustering', 'youtube_data_clustering', 'POSITIVE',
        'NEUTRAL', 'NEGATIVE', 'SENTIMENT_ANALYSIS_RESULT']      
        
        final_data.to_csv("last_final_data_new.csv",index=False)
    else:
        print("----------------------- Data not came ----------------------------")