import re
import nltk
import heapq
from twilio.rest import Client
import smtplib
import requests
from requests.exceptions import HTTPError
import speech_recognition as sr

#speech to text module
rec = sr.Recognizer()
audioFile = "audio file from the API"
with sr.AudioFile(audioFile) as sourceFile:
    audio = rec.record(sourceFile) 
try:
    text = rec.recognize_google(audio)
except Exception as e:
    print(e)    

#preprocessing the data
text = re.sub(r'\[[0-9]*\]',' ',text)
text = re.sub(r'\s+',' ',text)
clean_text = text.lower()
clean_text = re.sub(r'\W',' ',clean_text)
clean_text = re.sub(r'\d',' ',clean_text)
clean_text = re.sub(r'\s+',' ',clean_text)

sentences = nltk.sent_tokenize(text)

stop_words = nltk.corpus.stopwords.words('english')    

#Figuring out cancer terms and medicine prescribed in the conversation
#tokenizing the sentences
words = nltk.word_tokenize(text)

#applying part of speech on each individual word
tagged_words = nltk.pos_tag(words)

#collecting all the nouns in a seperate list
word_tags=[]
for tw in tagged_words:
    if tw[1] == "NN" or tw[1] == "NNS" or tw[1] == "NNP" or tw[1] == "NNPS":
        word_tags.append(tw[0])
        
        
#fetching cancer terms meaning from the API's
health_terms={}       
for wt in word_tags:
    try:
        response = requests.post('http://34.68.232.47/meaning', json={'word':wt})
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        json_response = response.json()
        if(json_response is not None):
            health_terms.update({wt:json_response['meaning']})
        else:
            continue
          
#checking if the medicine is present in the database through API's
medicines=[]      
for wt in word_tags:
    try:
        response = requests.post('http://34.68.232.47/medicine', json={'word':wt})
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        json_response = response.json()
        if(json_response is not None):
            medicines.append(json_response['words'])
        else:
            continue
                 

#Applying TF-IDF model
word2count = {}
for word in nltk.word_tokenize(clean_text):
    if word not in stop_words:
        if word not in word2count.keys():
            word2count[word] = 1 
        else:
            word2count[word] += 1
            
for key in word2count.keys():
    word2count[key] = word2count[key]/max(word2count.values())
            
#Overall summary of the conversation
sent2score = {}
sent3score = {}
for sentence in sentences:
    for word in nltk.word_tokenize(sentence.lower()):
        if word in word2count.keys():
            if len(sentence.split(' ')) < 30:
                if sentence not in sent2score.keys():
                    for ht in health_terms.keys():
                        if word in ht:                
                            sent2score[sentence] = 10
                            
                            
#Medicine related summary of the conversation
for sentence in sentences:
    for word in nltk.word_tokenize(sentence.lower()):
        if word in word2count.keys():
            if len(sentence.split(' ')) < 30:
                if sentence not in sent3score.keys():
                    for m in medicines:
                        if word in m:
                            sent3score[sentence] = 10
                  
best_sentences = heapq.nlargest(5,sent2score,key=sent2score.get)
best_sentence = heapq.nlargest(5,sent3score,key=sent3score.get)

#converting list into string of cancer terms
string_health_terms = '\n'.join(health_terms)

#converting list into string of medicine prescribed
string_medicine = '\n'.join(medicines)
 

#Overall Summary
string_overall_summary = ''
for sentence in best_sentences:
    string_overall_summary = string_overall_summary + sentence + '\n'
    
#Medicine Summary
string_medicine_summary = ''
for sentence in best_sentence:
    string_medicine_summary = string_medicine_summary + sentence + '\n'  
    
    
#fetching patient information from API's
try:
    response = requests.post('http://34.68.232.47/patient', json={"id":"3"})
except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}')  # Python 3.6
else:
    json_response = response.json()
    email = json_response['email']
    phoneNumber = json_response['phone']    
            
#SMS Notification service 
# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account_sid = 'AC7a2b65e083d198102faa11d2c843b8d6'
auth_token = '79df71c72260a725c3eae0ae9a5963b6'
summary = 'Cancer Terms: \n'+string_health_terms + '\n\n Medicine Prescribed: \n' + string_medicine+ '\n\n Overall Summary: \n'+ string_overall_summary+ '\n Medicine Summary: \n'+ string_medicine_summary
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body=summary,
                     from_='+12019322596',
                     to=phoneNumber
                 )

#Email Notification
email_from = "ekohealthsolutions@gmail.com"
email_to = email
message = summary
password = "ekohealth2019"

server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(email_from,password)
server.sendmail(email_from,email_to,message)
server.quit()

