from celery import shared_task
from django.core.serializers import serialize
from django.shortcuts import render, redirect,HttpResponse
import requests
import subprocess
from scripts import *
import pandas as pd

from .serializers import *

from .scripts.optimized_states_wise import *
from .scripts.scrap_youtube_data import *
from .scripts.youtube_video_trimming_process import *



@shared_task
def scrap_youtube_videos():
    try:
        youtube_csv_content = scrap_data_from_youtube()
        json_youtube_csv_content = youtube_csv_content.to_json(orient='records')
        youtube_data_list = json.loads(json_youtube_csv_content)
        dataArray = []
        for content in youtube_data_list:
            title = content["title"]
            views = content["views"]
            thumbnail = content["thumbnail"]
            link = content["link"]
            published_time_ago = content["published_time_ago"]
            duration_of_video = content["duration_of_video"]
            channel_name = content["channel_name"]
            type_of_platform = content["type_of_platform"]
            try:
                youtube_video_data = youtube_video_trimming_process(link)
                summary_json = youtube_video_data.loc[:,['subtitle','SENTIMENT_ANALYSIS_RESULT']].to_json()
                youtube_data_list = youtube_video_data.to_json(orient='records')
                if youtube_data_list:
                    
                    youtube_data_obj = news_obj.objects.create(title=title,views=views,thumbnail=thumbnail,link=link,
                                                        published_time_ago=published_time_ago,duration_of_video=duration_of_video,
                                                        channel_name=channel_name,type_of_platform=type_of_platform,source_type='youtube')
                    youtube_data_obj.sentiment_analysis = youtube_data_list
                    youtube_data_obj.summary_json=summary_json
                    youtube_data_obj.save()
                    serialized_data = news_obj_serializer(youtube_data_obj).data
                    dataArray.append(serialized_data)
                    print(len(dataArray))
                    print('data pusheddddddddddddddddddddddddddddd')
                    
                else:
                    print('no data to analyse')
            except Exception as e:
                print("error occured while analysing video -->"+str(e))   
        for i in dataArray:
            print(i)
        print(type(dataArray))
        print(len(dataArray))         
        data = json.dumps(dataArray)
        print('sucesssssssssssssssssssssssssssssssss')
        print(data)
        try:
            post_url = 'http://10.1.75.45:8000/save_youtube_data/'  
            response = requests.post(post_url, data=data, headers={'Content-Type': 'application/json'})
           
            if response.status_code == 200:
                print('Data successfully posted to the URL')
            else:
                print(f'Error posting data. Status code: {response.status_code}, Response content: {response.text}')
                          
            return HttpResponse({'data': data})
        except Exception as e:
            print('error in posting youtube data to endpoint -->'+str(e))
            
            
    except Exception as e:
        print("error occured while scraping youtube data --> "+str(e))
        
        
    #    clustered_data = collect_data_for_state()
    #    print(type(clustered_data))
    #    print(clustered_data)
@shared_task
def scrap_websites_with_clusters():

    try:
        data_frame = scrap_cluster_news()
        print(data_frame)
        print('data recievedddddddddddddddddddddddddddddd')
        try:
            for index, row in data_frame.iterrows():
                print('data loooooooooooooooopeddddddddddd')
                print(type(data_frame))
                row_dict = row.to_dict()
                data = json.dumps(row_dict)
                try:
                    post_url = 'http://10.1.75.142:8000/scrap_news_clustered_data/'  
                    response = requests.post(post_url, data=data, headers={'Content-Type': 'application/json'})
                
                    if response.status_code == 200:
                        print('Data successfully posted to the URL')
                    else:
                        print(f'Error posting data. Status code: {response.status_code}, Response content: {response.text}')
                                
                    
                    # return HttpResponse({'data': data})
                except Exception as e:
                    print('error in posting youtube data to endpoint -->'+str(e))

        except Exception as e:
            print('error occured while posting clustered news obj'+str(e))
       
    except Exception as e:
        print('error while scrapping clusters from news-->'+str(e))
        
        
         