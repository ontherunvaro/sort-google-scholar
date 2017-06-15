#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code creates a database with a list of publications data from Google 
Scholar.
The data acquired from GS is Title, Citations, Links and Rank.
It is useful for finding relevant papers by sorting by the number of citations
This example will look for the top 100 papers related to the keyword 
'non intrusive load monitoring', so that you can rank them by the number of citations

As output this program will plot the number of citations in the Y axis and the 
rank of the result in the X axis. It also, optionally, export the database to
a .csv file.

Before using it, please update the initial variables

"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import argparse


def get_citations(content):
    out = 0
    for char in range(0, len(content)):
        if content[char:char + 9] == 'Cited by ':
            init = char + 9
            for end in range(init + 1, init + 6):
                if content[end] == '<':
                    break
            out = content[init:end]
    return int(out)


def get_year(content):
    for char in range(0, len(content)):
        if content[char] == '-':
            out = content[char - 5:char - 1]
    if not out.isdigit():
        out = 0
    return int(out)


def get_author(content):
    for char in range(0, len(content)):
        if content[char] == '-':
            out = content[2:char - 1]
            break
    return out


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Search Google Scholar and order by citations')

    parser.add_argument('query', action='store', help='the query to search')
    parser.add_argument('-n', action="store", dest='count', type=int, default=100,
                        help='number of articles to fetch, 100 by default')
    parser.add_argument('-f', action="store", dest="filename", help='store the resulting database in FILENAME')

    input_args = parser.parse_args()

    keyword = input_args.query
    number_of_results = input_args.count

    save_database = False
    if (input_args.filename is not None):
        save_database = True
        path = input_args.filename

    # Start new session
    session = requests.Session()

    # Variables
    links = list()
    title = list()
    citations = list()
    year = list()
    rank = list()
    author = list()
    rank.append(0)  # initialization necessary for incremental purposes

    # Get content from 1000 URLs
    for n in range(0, number_of_results, 10):
        url = 'https://scholar.google.com/scholar?start=' + str(n) + '&q=' + keyword.replace(' ', '+')
        page = session.get(url)
        c = page.content

        # Create parser
        soup = BeautifulSoup(c, 'html.parser')

        # Get stuff
        mydivs = soup.findAll("div", {"class": "gs_r"})

        for div in mydivs:
            try:
                links.append(div.find('h3').find('a').get('href'))
            except:  # catch *all* exceptions
                links.append('Look manually at: https://scholar.google.com/scholar?start=' + str(
                    n) + '&q=non+intrusive+load+monitoring')

            try:
                title.append(div.find('h3').find('a').text)
            except:
                title.append('Could not catch title')

            citations.append(get_citations(str(div.format_string)))
            year.append(get_year(div.find('div', {'class': 'gs_a'}).text))
            author.append(get_author(div.find('div', {'class': 'gs_a'}).text))
            rank.append(rank[-1] + 1)

    # Create a dataset and sort by the number of citations
    data = pd.DataFrame(list(zip(author, title, citations, year, links)), index=rank[1:],
                        columns=['Author', 'Title', 'Citations', 'Year', 'Source'])
    data.index.name = 'Rank'

    data_ranked = data.sort_values('Citations', ascending=False)
    print(data_ranked)

    # Save results
    if save_database:
        data_ranked.to_csv(path, encoding='utf-8')  # Change the path
