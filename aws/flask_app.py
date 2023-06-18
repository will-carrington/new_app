
from flask import Flask, render_template, request, Response
import csv
from io import StringIO
import pandas as pd
import requests
import bs4
import re
import time
import random
import time
import datetime
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')



def targeted_user_emails(ddf,topics_,length):
  states = []
  cities = []
  topics = []
  for i in range(len(topics_.split(','))):
    topics.append(topics_.split(',')[i])

  target_length = int(length)
  print('-')
  email = []
  link=[]
  for ii in range(1000):
    city = ddf['Cities'][ii]
    state = ddf['States'][ii]
    name = ddf['Names'][random.randint(0,283)]
    topic = topics[random.randint(0,len(topics)-1)]
    urln = 'https://www.google.com/search?q=%22'+topic.replace(' ','+')+'%22%2C+'+name+'%2C++%22facebook.com%22+%22%40gmail.com%22+'+city+',+'+state
    html = requests.get(urln, headers = headers).text
    soupc = str(bs4.BeautifulSoup(html, "html.parser"))
    spli = soupc.split('<div class="yuRUbf"><a data-ved="')
    time.sleep(random.uniform(45,60))
    for i in range(len(spli)-1):
      url = spli[i+1].split('href="')[1].split('"')[0]
      url_check1 = url.split('//')[1].split('/')[0].replace('.com','',).replace('www.','')
      if url_check1 == 'facebook':
        ee = spli[i+1].split('<em>gmail')[0].replace('<em>','').replace('</em>','').split(' ')[-1].split('>')[-1].split('"')[-1].split('...')[-1].split(':')[-1].split('=')[-1]
        if len(ee)>=3:
          email.append(ee.replace('(','').replace(')','').replace('[','').replace(']','')+'gmail.com')
          try:
            link.append(spli[1].split('url=')[1].split('"')[0].replace('"','').split('?')[0].split('&amp')[0])
          except:
            link.append('nan')

          cities.append(city)
          states.append(state)

    print('Current # of Emails Collected: '+str(len(pd.DataFrame(email).drop_duplicates())))
    if len(pd.DataFrame(email).drop_duplicates())>=target_length:
      break

  today = datetime.date.today()
  month = today.month
  day = today.day
  year = today.year

  formatted_date = f"{month}_{day}_{year}"

  df_final = pd.DataFrame()
  df_final['Email'] = email
  df_final['Aprx State Location'] = states
  df_final['Aprx City Location'] = cities
  df_final['Link Email Scraped From'] = link

  df_final = df_final.drop_duplicates(subset = 'Email')

  return df_final

@app.route('/convert', methods=['POST'])
def convert():
    # Get the CSV data and process it
    csv_data = request.form['csv_data']
    csv_num = request.form['email_count']

    # Set the absolute file path
    file_path = 'https://raw.githubusercontent.com/will-carrington/new_app/edit/main/aws/data_.csv'

    # Read the CSV file using pandas
    ddf = pd.read_csv(file_path)

    # Call targeted_user_emails() with the required arguments
    df_final = targeted_user_emails(ddf, csv_data, csv_num)

    # Create a writable file object
    file_obj = StringIO()

    # Write the DataFrame to the file object as a CSV
    df_final.to_csv(file_obj, index=False)

    # Create a Flask Response object with the file contents
    response = Response(file_obj.getvalue(), mimetype='text/csv')

    # Set the file name for the download
    response.headers.set('Content-Disposition', 'attachment', filename='converted_data.csv')

    return response

import socket

def get_ip_address():
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Connect to a remote server (doesn't actually send any data)
        sock.connect(("8.8.8.8", 80))

        # Get the local IP address from the socket
        ip_address = sock.getsockname()[0]
    except socket.error:
        ip_address = "Unknown"

    finally:
        # Close the socket
        sock.close()

    return ip_address

# Call the function to get the IP address
ip = get_ip_address()


if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host=ip, port=port, debug=True)
