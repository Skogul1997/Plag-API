from bs4 import BeautifulSoup
import requests


def getResponse(url):
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'lxml')
    percent = {}

    for tr in soup.find_all('tr')[1:]:
        tds = tr.find_all('td')
        a, b = tds[0].text.rstrip("%)\n\r").split(
            "("), tds[1].text.rstrip("%)\n\r").split("(")
        student1, percent1 = a[0].split('.')[0], int(a[1])
        student2, percent2 = b[0].split('.')[0], int(b[1])
        if student1 in percent.keys():
            if percent1 > percent[student1]:
                percent[student1] = percent1
        else:
            percent[student1] = percent1
        if student2 in percent.keys():
            if percent2 > percent[student2]:
                percent[student2] = percent2
        else:
            percent[student2] = percent2

    return percent
