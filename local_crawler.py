import requests
import re
import csv
from bs4 import BeautifulSoup


# 地方领导
def get_response(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        return response
    else:
        return None


# 姓名 性别 民族	年龄 籍贯 党派 党龄 最高学历 专业 升迁时间节点
# name gender race age hometown	party party_standing degree	major track
def info_extract(url):  # request提取失败，用beautifulsoup代替
    page = get_response(url)
    if page:
        soup = BeautifulSoup(page.content, 'lxml')
        text = soup.find('div', class_='box01').get_text()

        text = re.sub('[\n\t\r \u3000]+', ' ', text)
        text = text.split(' ')
        for s in text:
            if len(s) == 0:
                text.remove(s)

        base_info = text[0].split('，')

        try:
            pattern_party = re.compile('.*，(.*)年.*加*入([\u4e00-\u9fa5]*党*)')  # 获得入党时间，党派
            party_info = re.findall(pattern_party, text[0])
            if len(party_info) == 0:
                party_info = [('', '')]
            pattern_degree = re.compile('.*，(.*)学位，|.*，(.*)学位。')  # 获得学历/专业
            degree_info = re.findall(pattern_degree, text[0])

            if (type(degree_info) == tuple):
                degree_info = list(degree_info)

            if len(degree_info) == 0:
                degree_info = re.findall('.*，(.*学士)|.*，(.*硕士)|.*，(.*博士)', text[0])
                if '研究生' in degree_info:
                    degree_info = [degree_info[0][:-3]]

            elif '、' in degree_info[0]:
                degree_info = degree_info[0].split('、')
                degree_info = [degree_info[-1]]

            for each in degree_info[0]:
                if len(each) != 0:
                    degree_info = [each]
            degree_info[0] = degree_info[0].replace('学位', '')


            for s in degree_info:
                if len(s) == 0:
                    degree_info.remove(s)
            if base_info[3][0] == '1':
                leader = base_info[:3]

                leader.append(base_info[3][:4])
            else:
                leader = base_info[:2]
                leader.append(base_info[3])
                leader.append(base_info[2][:4])
            leader.append(base_info[4][:2])
            leader.append(party_info[0][0])
            leader.append(party_info[0][1])
            leader.append(degree_info[0][:-2])
            leader.append(degree_info[0][-2:])

            track_temp = []
            for sentence in text[1:]:
                if sentence[0] == '2' or sentence[0] == '1':  # 进修学习，考虑到年代的特殊性，也视为升迁的一种，平调被省略
                    track_temp.append(sentence[:4])
            track = ','.join(track_temp)

            leader.append(track)
        except:
            return None
        print(leader)
        return leader
    else:
        return None


def province_urls():
    url = 'http://ldzl.people.com.cn/dfzlk/front/personProvince1.htm'
    response = get_response(url)
    pattern_urls = re.compile('<li><a href="(.*)" title="')
    urls = re.findall(pattern_urls, response.text)
    # http://ldzl.people.com.cn/
    for url in urls[:33]:
        yield 'http://ldzl.people.com.cn/' + url


def leader_urls(p_url):
    response = get_response(p_url)
    pattern_urls = re.compile('(personPage.*.htm)')
    urls = re.findall(pattern_urls, response.text)
    urls = list(set(urls))
    for url in urls:
        yield 'http://ldzl.people.com.cn//dfzlk/front/' + url


def main():
    leader_info = []
    for p_url in province_urls():
        for l_url in leader_urls(p_url):
            print(l_url)
            leader = info_extract(l_url)
            if leader:
                leader_info.append(leader)

    # url = 'http://ldzl.people.com.cn//dfzlk/front/personPage12076.htm'
    # leader = info_extract(url)
    # leader_info.append(leader)

    with open('local.csv', 'w+', newline='', encoding='utf-8') as f:  # newline参数控制行之间是否空行
        f_csv = csv.writer(f)
        f_csv.writerow(['name', 'gender', 'race', 'age', 'hometown', 'party',
                        'party_standing', 'degree', 'major', 'track'])  # headers为表头属性名组成的数组
        f_csv.writerows(leader_info)


if __name__ == '__main__':
    main()
