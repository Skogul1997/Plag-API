import mosspy
import os
import webscraper
import multiprocessing
import time
import telnetlib
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

    p.start()

    # start_time = time.time()
    while(True):
        if(p.is_alive()):
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
