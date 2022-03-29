from flask import Flask, render_template, redirect, request
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
#import seaborn as sns

obj = Flask(__name__) # Object name 'obj' of flask class

def plotting(x,y, filename, rate):
    ''' Plots data and returns the filename and rate '''
    plt.figure(figsize = (25,25))
    plt.plot(x, y, ':og')
    plt.grid()
    plt.ylabel("PRICE")
    plt.xlabel("DATE")
    plt.xticks(rotation=90)
    plt.title("Stock Market History: "+filename+" | Current Price: $"+str(rate))
    name = 'static/'+filename+'.jpg'
    plt.savefig(name)
    return name

def sanitize(lst) :
    ''' Sanitizing the values '''
    lst.remove(lst[0])# first
    lst.remove(lst[-1]) #last extraction
    p,d,r=[],[],[]

    for item in lst:
        price= item.find("td",attrs={'class':'Pstart(10px)'}).text
        if not "Dividend" in price and not "Stock split" in price:
            p.append(price)
            date= item.td.span.text
            d.append(date)
    for i in p: # To remove (,) from thousand figures.
        if "," in i:
            k=i.split(sep=',')
            dp=k[0]+k[1]
        else:
            dp=i    
        r.append(float(dp))
    d.reverse()
    r.reverse()
    return d, r

def scrapedata(page, logo) :
    ''' Scrapping data '''
    page=BeautifulSoup(page.text,'lxml')
    price = (page.find('div',attrs={'class':'D(ib) Fw(200) Mend(25px) Mend(20px)--lgv3'}))
    rate=price.span.text
    url="https://in.finance.yahoo.com/quote/"+logo+"/history?p="+logo
    page= requests.get(url)
    page= BeautifulSoup(page.text,'lxml')
    a=page.find('div',attrs={'id':'YDC-Col1'})
    lst=a.find_all('tr')
    return lst, rate

def search_company_logo(search) :
    ''' Get the company name of the searched.'''
    html_code = BeautifulSoup(search.text,'lxml')
    try : 
        s = html_code.find('div',attrs={'class':'Pos(r) smartphone_Mb(30px)'})
        lst = s.find_all('tr')[1]
        logo = lst.td.a.text
        co = lst.td.a
        c=str(co).find("title=")
        c=c+7
        p=''
        com=""
        while(not p=='>'):
            p=str(co)[c]
            com=com+p
            c=c+1
        com=com[:-2]
        return logo, com
    except Exception as e :
        return 'Error', 'Error2' # IF NO MATCH FOUND

def smart_search(co) :
    ''' smarty search for the given company name even there is a TYPO '''
    url = "https://finance.yahoo.com/lookup?s="+ co
    search = requests.get(url)# fetch above url data
    return search

@obj.route('/',methods=['POST','GET']) # Home Page
def home():
    if request.method == 'POST': # if user is posting a query
        co = request.form.get('company') # fetch
        if co:
            search = smart_search(co)
            if search.status_code == 200: #200: ok
                logo, com = search_company_logo(search)
                if logo != 'Error' :
                    
                    url="https://in.finance.yahoo.com/chart/" + logo
                    page=requests.get(url)
                    
                    if page.status_code==200:
                        lst, rate = scrapedata(page, logo)
                        d, r = sanitize(lst)
                        name = plotting(d, r, logo, rate)
                    else:
                        print(str(page.status_code)+" ERROR")
                    return render_template('Home.html', logo = logo, company = com, rate = rate)
                return render_template('Home.html', logo = None)
    return render_template('Home.html')

@obj.route('/about')
def about():
    return render_template('About.html')

if __name__  == '__main__':
    obj.run(debug=True)