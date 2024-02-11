"""

projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Zdeněk Korvas

email: korvasz@seznam.cz

discord: Zdeněk.K#9428

"""
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import sys


def main():
    if len(sys.argv) != 3:
        print("Wrong number of arguments. Use: python script.py <link> <output_file.csv>")
        return
    link = sys.argv[1]
    output_file = sys.argv[2]
    if not link.startswith('https://volby.cz'):
        print("Neplatný odkaz. Zadejte odkaz obsahující 'https://volby.cz'")
        return
    number = get_number(link)
    website_common = link

    # first data frame
    data = {
        'Number': get_number(website_common),
        'City': get_city(website_common),
    }
    data2 = []
    # generate url for each city
    link_endings = get_link_end(website_common)
    for idx, link_end in zip(number, link_endings):
        url = f'https://volby.cz/pls/ps2017nss/{link_end}'
        # second data frame
        data_rows = {
            'Number': idx,
            'Valid': get_valid(url),
            'Registered': get_registered(url),
            'Envelopes': get_envelopes(url)
        }
        data2.append(data_rows)
        political_parties = get_political_party(url)
        votes = get_votes(url)
        for party, vote in zip(political_parties, votes):
            data[party] = data.get(party, []) + [vote]
    df = pd.DataFrame(data)
    df2 = pd.DataFrame(data2)
    # merging frames on row 'Number'
    merge_df = pd.merge(df2, df, on='Number')
    final_df = swap_columns(merge_df, 'Valid', 'City')
    final_df.to_csv(output_file, index=False)
    data = pd.read_csv(output_file)
    # use function clean_values to all data in frame:
    for column in data.columns:
        data[column] = data[column].apply(clean_values)
    # replace csv with new
    data.to_csv(output_file, index=False)


def clean_values(value):
    """
    cleaning values in .csv file
    :param value: each value in file
    :return: cleaned value
    """
    if isinstance(value, str):
        value = value.replace('[', '').replace(']', '').replace('\\xa0', '')
        return value
    else:
        value = str(value).replace('\xa0', '')
        return value


def swap_columns(df, col1, col2):
    """
    swaping columns in dataframe
    :param df: original dataframe
    :param col1:
    :param col2:
    :return: dataframe with swaped columns
    """
    col_list = list(df.columns)
    x, y = col_list.index(col1), col_list.index(col2)
    col_list[y], col_list[x] = col_list[x], col_list[y]
    df = df[col_list]
    return df


def get_link_end(website):
    link_ending = []
    results = get_results(website)
    for result in results:
        try:
            link_ending.append(result.find('td', {'class': 'cislo'}).find('a')['href'])
        except:
            continue
    return link_ending


def get_results(website):
    """
    function is reading html, making soup object and then finding all 'tr' elements
    :param website: link
    """
    response = requests.get(website)
    soup = bs(response.content, features='html.parser')
    results = soup.find_all('tr')
    return results


def get_city(website: str) -> list:
    """
    Funkce pro získání jedinečných jmen obvodů ze stránky.
    :param website: URL adresa stránky
    :return: Seznam jedinečných jmen obvodů
    """
    cities = []

    results = get_results(website)
    for result in results:
        try:
            city = result.find('td', {'class': 'overflow_name'}).get_text()
            if city not in cities:
                cities.append(city)
        except:
            pass

        try:
            city_alternate = result.find('td', {'headers': 't2sa1 t2sb2'}).find('a').get_text()
            if city_alternate and city_alternate not in cities:
                cities.append(city_alternate)
        except:
            pass

        try:
            city_t1sa1_t1sb2 = result.find('td', {'headers': 't1sa1 t1sb2'}).get_text()
            if city_t1sa1_t1sb2 and city_t1sa1_t1sb2 not in cities:
                cities.append(city_t1sa1_t1sb2)
        except:
            pass

    return cities


def get_number(website: str) -> list:
    """
    function made to scrap city numbers from website
    :param website: volby.cz
    :return: list of city numbers
    """
    number = []
    results = get_results(website)
    for result in results:
        try:
            number.append(result.find('td', {'class': 'cislo'}).get_text())
        except:
            continue
    return number


def get_envelopes(website: str) -> list:
    """
    function scraping envelopes for each city
    :param website: volby.cz
    :return: list
    """
    envelopes = []
    city_results = get_results(website)
    for result in city_results:
        try:
            envelopes.append(result.find('td', {'data-rel': 'L1', 'headers': 'sa3'}).get_text().strip())

        except:
            continue
    return envelopes


def get_registered(website: str) -> list:
    """
    function gathering total number of registered user for voting
    :param website: volby.cz
    :return: list of numbers
    """
    registered = []
    results = get_results(website)
    for result in results:
        try:
            registered.append(result.find('td', {'data-rel': 'L1', 'headers': 'sa2'}).get_text().strip())
        except:
            continue
    return registered


def get_valid(website: str) -> list:
    """
    function gathering total number of valid votes in each city
    :param website: volby.cz
    :return: list of numbers
    """
    valid = []
    results = get_results(website)
    for result in results:
        try:
            valid.append(result.find('td', {'data-rel': 'L1', 'headers': 'sa6'}).get_text().strip())
        except:
            continue
    return valid


def get_political_party(website: str) -> list:
    """
    function getting names of political parties from volby.cz for each region
    :param website: volby.cz
    :return: list of political parties
    """
    politicals = []
    party_results = get_results(website)
    for result in party_results:
        try:
            politicals.append(result.find('td', {'class': 'overflow_name'}).get_text())
        except:
            continue
    return politicals


def get_votes(website: str) -> list:
    """
    function scraping number of votes for political parties from volby.cz for each region
    :param website: volby.cz
    :return: list of votes
    """
    votes = []
    party_results = get_results(website)
    for result in party_results:

        try:
            votes.append(result.find('td', {'class': 'cislo', 'headers': 't1sa2 t1sb3'}).get_text().strip())

        except:
            votes.append(result.find('td', {'class': 'cislo', 'headers': 't2sa2 t2sb3'}).get_text().strip())
        finally:
            continue
    return votes


if __name__ == '__main__':
    main()
