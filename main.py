import requests
import fake_useragent
from lxml import etree
import os
import pandas as pd
import re

ua = fake_useragent.UserAgent()
headers = {"User-Agent": ua.Chrome}
s = requests.Session()
s.headers.update(headers)


def record_question(question: dict):
    db_path = './db.csv'
    if not os.path.exists(db_path):
        df = pd.DataFrame(columns=['title', 'choices', 'answer'])
        df.to_csv(db_path, index=False)
    db = pd.read_csv(db_path)
    # if this question is already in the db, do nothing
    if question['title'] in db['title'].values:
        return False
    db = db.append(question, ignore_index=True)
    db.to_csv(db_path, index=False)
    return True


base_url = "http://121.192.191.91/"
testing_url = base_url + "redir.php?catalog_id=6&cmd=testing"
dati_url = base_url + "redir.php?catalog_id=6&cmd=dati"
tikubh = [1436, 1467, 1471, 1484, 1485, 1486, 4199, 4200, 516700]

def get_answer(tikubh: int):
    tiku_url = testing_url + f"&tikubh={tikubh}"
    s.get(testing_url)
    ### 提交空白答案
    s.get(tiku_url)
    payload = {"runpage": 0, "page": 1, "direction": None, "tijiao": 1, "postflag": 1, "mode": "test"}
    response = s.post(dati_url, data=payload)
    response.encoding = "gbk"
    html = etree.HTML(response.text)
    result_entrance = html.xpath("//div[@class='nav']//a")[0]
    result_url = base_url + result_entrance.values()[0]

    response = s.get(result_url)
    response.encoding = "gbk"
    html = etree.HTML(response.text)
    shiti = html.xpath("//div[@class='shiti']")

    num_newer = 0
    for st in shiti:
        title = st.getchildren()[2].text
        total_html = etree.tostring(st, encoding="utf-8").decode("utf-8")
        answer = re.findall("标准答案：&#13;\n(.*?)&#13", total_html)[0].strip()
        choices = []
        if st.find("ul") is not None:
            ul = st.find("ul").find("li")
            choices = [etree.tostring(x, encoding="utf-8").decode("utf-8").replace("<br />\n", "") for x in
                       ul.getchildren()]
        question = {
            "title": title,
            "answer": answer,
            "choices": choices
        }
        num_newer += record_question(question)
    print("Add {} new questions".format(num_newer))
    return num_newer


for tikubh in tikubh:
    while 1:
        if get_answer(tikubh) == 0:
            break
