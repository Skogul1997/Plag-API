import mosspy
import os
import webscraper
import multiprocessing
import time
import telnetlib
from datetime import datetime
# https://group13-plagiarism-api.herokuapp.com/
# MOSS userID = 669827647
userID = int(os.environ.get("MOSS_USER_ID"))


def findUrl(userID, lang, q, directory, path, a):
    m = mosspy.Moss(userID, lang)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        m.addFile(filename)
        a[filename.split('.')[0]] = 0
    q.put(a)
    q.put(m.send())


def getURL(path, lang):

    a = {}

    # m = mosspy.Moss(userID, lang)
    q = multiprocessing.Queue()
    directory = os.path.join(os.getcwd(), path)
    os.chdir(path)

    try:
        tn = telnetlib.Telnet('moss.stanford.edu', 7690)
    except:
        return {'status': "Fail", 'error': "MOSS server not available."}, 503

    # for file in os.listdir(directory):
    #     filename = os.fsdecode(file)
    #     m.addFile(filename)
    #     a[filename.split('.')[0]] = 0

    p = multiprocessing.Process(
        target=findUrl, args=(userID, lang, q, directory, path, a))
    start_time = datetime.now()
    p.start()

    # start_time = time.time()
    while(True):
        if(p.is_alive()):
            if((datetime.now()-start_time).total_seconds()>=180):
                p.terminate()
                p.join()
                return {'status': "Fail", 'error': "Server taking too long to process."}, 503
                break
            continue
        else:
            break
    # time.sleep(150)
    # try:
    a = q.get()
    url = q.get()
    b = webscraper.getResponse(url)
    a.update(b)
    return {'status': 'Success', 'results': a, 'detailed_report_url': url}, 200
    # except:
    #     return {'status': "Fail", 'error': "MOSS server not available."}, 503

    # if (p.is_alive() == False):
    #     a = q.get()
    #     url = q.get()
    #     b = webscraper.getResponse(url)
    #     a.update(b)
    #     return {'status': 'Success', 'results': a, 'detailed_report_url': url}, 200

    # else:
    #     p.terminate()
    #     p.join()
    #     return {'status': "Fail", 'error': "MOSS server not available."}, 503
