# this is a streamlit app
import streamlit as st
import pandas as pd

# import libraries
import requests
from bs4 import BeautifulSoup
import cohere



# create a function that scrapes the folder names of a github repository
# and returns a database of folders
# the folders are stored in a class = 'js-navigation-open Link--primary'
# append 'https://github.com' to the beginning of the folder path
# the strings contianing '/tree/' are folders and should be stored in the column folder
# the strings containing '/blob/' are files and should be ignored


def scrape_github_repo_folder(repo_url):
    # create a list to store the folder names
    folder_list = []

    # extract the html from the url
    html = requests.get(repo_url).text

    # create a soup object
    soup = BeautifulSoup(html, 'html.parser')

    # extract the folder names
    for link in soup.find_all('a', {'class': 'js-navigation-open Link--primary'}):
        folder_list.append(link.get('href'))

    # create a dataframe to store the folder names
    df = pd.DataFrame(folder_list, columns=['folder'])

    # remove the files from the dataframe
    df = df[~df['folder'].str.contains('/blob/')]
    df['folder'] = 'https://github.com' + df['folder']

    return df

# run the function on each of the urls in the dataframe, return a new dataframe contining a column for the folder and a column for the new subfolders
# the new subfolders are stored in a class = 'js-navigation-open Link--primary'

def scrape_github_repo_subfolders(df):
    # create a list to store the folder names
    folder_list = []

    # loop through the urls in the dataframe
    for url in df['folder']:
        # extract the html from the url
        html = requests.get(url).text

        # create a soup object
        soup = BeautifulSoup(html, 'html.parser')

        # extract the folder names
        for link in soup.find_all('a', {'class': 'js-navigation-open Link--primary'}):
            folder_list.append(link.get('href'))

    # create a dataframe to store the folder names
    df = pd.DataFrame(folder_list, columns=['folder'])

    # remove the files from the dataframe
    df = df[~df['folder'].str.contains('/blob/')]
    df['sub_folder'] = 'https://github.com' + df['folder']

    return df

# crawl the subfolders and return a dataframe containing the urls of the files
# the files are stored in a class = 'js-navigation-open Link--primary'

def scrape_github_repo_files(df):
    # create a list to store the folder names
    file_list = []

    # loop through the urls in the dataframe
    for url in df['sub_folder']:
        # extract the html from the url
        html = requests.get(url).text

        # create a soup object
        soup = BeautifulSoup(html, 'html.parser')

        # extract the folder names
        for link in soup.find_all('a', {'class': 'js-navigation-open Link--primary'}):
            file_list.append(link.get('href'))

    # create a dataframe to store the folder names
    df = pd.DataFrame(file_list, columns=['file'])

    # remove the files from the dataframe
    df = df[df['file'].str.contains('/blob/')]
    df['file'] = 'https://github.com' + df['file']

    return df

# crete a function that extracts the code from a github file
# the code is stored in a class = 'blob-code blob-code-inner js-file-line'
# the code in each file is a row in the dataframe

def scrape_github_repo_code(df):
    # create a list to store the code
    code_list = []

    # loop through the urls in the dataframe
    for url in df['file']:
        # extract the html from the url
        html = requests.get(url).text

        # create a soup object
        soup = BeautifulSoup(html, 'html.parser')

        # extract the code, it is all stored in a single div and we want to concatenate the code into one string
        code = ''
        for link in soup.find_all('td', {'class': 'blob-code blob-code-inner js-file-line'}):
            code = code + link.text

        # append the code to the list
        code_list.append(code)

    # create a dataframe to store the code
    df = pd.DataFrame(code_list, columns=['code'])

    # add the url names to the dataframe
    df['file'] = files['file']

    return df


co = cohere.Client('bE6Is3wvtmXyHtgnCQocDIgdH7PcYwdR21ZhnXgN')

# the following function will iterate over each row when I call apply to a dataframe and return the response.generations[0]. text into a new column
# add an error handler for 'CohereError:' and returns 'text too large' if the text is too large

def cohere_ai(text):
    try:
        response = co.generate(
                model='command-xlarge-20221108',
                prompt=f'{text}+\n\nWhat does this file do?',
                max_tokens=200,
                temperature=0.6,
                k=0,
                p=0.75,
                frequency_penalty=0,
                presence_penalty=0,
                stop_sequences=[],
                return_likelihoods='NONE')
        return response.generations[0].text
    except:
        return 'text too large'

# the user inputs a github url
url = st.text_input('Enter a github url')

# the user clicks a button to scrape the github url
if st.button('Scrape Github'):
    # scrape the github url
    df = scrape_github_repo_folder(url)

    # display the dataframe
    st.dataframe(df)

# the user clicks a button to scrape the subfolders
if st.button('Scrape Subfolders'):
    # scrape the subfolders
    df = scrape_github_repo_subfolders(df)

    # display the dataframe
    st.dataframe(df)

# the user clicks a button to scrape the files
if st.button('Scrape Files'):
    # scrape the files
    df = scrape_github_repo_files(df)

    # display the dataframe
    st.dataframe(df)

# the user clicks a button to run the 'scrape_github_repo_files' function on the dataframe
if st.button('Scrape Files'):
    # scrape the files
    df = scrape_github_repo_files(df)

    # display the dataframe
    st.dataframe(df)

# the user clicks a button to run the 'scrape_github_repo_code' function on the dataframe
if st.button('Scrape Code'):
    # scrape the code
    df = scrape_github_repo_code(df)

    # display the dataframe
    st.dataframe(df)

 # the user clicks a button to run the 'cohere_ai' function on the dataframe
if st.button('Generate Text'):
    # generate the text
    df['text'] = df['code'].apply(cohere_ai)

    # display the dataframe
    st.dataframe(df)

# return a list of urls and the text generated by cohere.ai
if st.button('Return List'):
    # create a list to store the urls and text
    url_list = []
    text_list = []

    # loop through the dataframe
    for index, row in df.iterrows():
        # append the url and text to the list
        url_list.append(row['file'])
        text_list.append(row['text'])

    # create a dataframe to store the urls and text
    df = pd.DataFrame(list(zip(url_list, text_list)), columns =['url', 'text'])

    # display the dataframe
    st.dataframe(df)   


