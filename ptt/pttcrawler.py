import requests
from bs4 import BeautifulSoup
import json

url = "https://www.ptt.cc/bbs/Gossiping/index.html"
#只有首次點選才會post cookie
form_data={
    'from': '/bbs/Gossiping/index.html',
    'yes' : 'yes'    
}
#session->在此程式中持續記住header的東東
#基本參數
r = requests.session()
#詢問是否18頁網址 點選'是'後會post一個from_data 把這個data存到session裡
response = r.post("https://www.ptt.cc/ask/over18", data=form_data)
response = r.get(url)
soup = BeautifulSoup(response.text,"html.parser")
original_page = soup
#article_num = 1
all_dict=[]
for i in range(2):
    #開始找標題
    links = soup.find_all("div",{"class":"title"})
    for link in links:
        if link.a != None:
            #檢查發現抓下來的連結會少前面的部分 所以補上
            page_url = "https://www.ptt.cc"+link.a["href"]
            #進入頁面
            response = r.get(page_url)
            soup = BeautifulSoup(response.text,"html.parser")

            #抓作者、標題與時間
            
            datas = soup.find_all("div", {"class":"article-metaline"})
            print("totaldatas:{}".format(datas))
            if datas == None:
                break
            author = datas[0].find("span", {"class":"article-meta-value"}).string
            title = datas[1].find("span", {"class":"article-meta-value"}).string
            time = datas[2].find("span", {"class":"article-meta-value"}).string
            #內文
            main_content = soup.find("div", {"id":"main-content"})
            all_text = main_content.text
            #因為內文最後都有一個-- 以--為分割條件
            pretext = all_text.split("--")[:-1]
            pre_all = "--".join(pretext)
            #不要第一行作者等資訊
            backtext = pre_all.split("\n")[1:]
            finaltext = "\n".join(backtext)
            #後續發文
            messages = soup.find_all("div", {"class":"push"})
            #comment_num = 1

            push=[]
            normal=[]
            ssh=[]
            for message in messages:  
                user_tag = message.find("span", {"class":"push-tag"}).string
                user_id = message.find("span", {"class":"push-userid"}).string
                user_content = message.find("span", {"class":"push-content"}).string
                user_time = message.find("span", {"class":"push-ipdatetime"}).string
                # print(user_tag)
                # print(user_id)
                # print(user_content)
                # print(user_time)

                #在字典內新增 一則留言一個dict
                dict1={"user_id" : user_id, "user_content" : user_content, "user_time" : user_time}
                # comment_title = "comment "+str(comment_num)
                if user_tag == "推 ":
                    push.append(dict1)
                elif user_tag == "→ ":
                    normal.append(dict1)
                elif user_tag == "噓 ":
                    ssh.append(dict1)
                #comment_num = comment_num+1
            print("Author: "+author)
            print("Title: "+title)
            print("Time: "+time)
            print(finaltext)
            print("")
            print("推 :")
            for i in push:
                print(i)
            print("→ :")
            for i in normal:
                print(i)
            print("噓 :")
            for i in ssh:
                print(i)

            #全存在一個dic內
            # article_title = "article "+str(article_num)
            comment_dict = {"push":push, "→":normal, "ssh":ssh}
            end_dict = {"author":author, "title":title, "time":time, "main-content":finaltext, "comments":comment_dict}
            all_dict.append(end_dict)
            # clear會出問題!!? 因為是有連接的?
            # push.clear()
            # normal.clear()
            # ssh.clear()
            # comment_dict.clear()
            # end_dict.clear()
            #article_num = article_num+1
    #換頁
    next_page = original_page.find_all("a", {"class":"btn wide"})
    #print(next_page)
    next_utl = "https://www.ptt.cc"+next_page[1]["href"]
    response = r.get(next_utl)
    soup = BeautifulSoup(response.text,"html.parser")
    original_page = soup
#最終dict
print(all_dict)
with open('data.json', 'w' , encoding='utf-8') as f:
    json.dump(all_dict, f)