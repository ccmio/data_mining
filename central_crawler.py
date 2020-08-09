import requests
import re
import csv

# 中央领导
def get_one_leader(url):
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
def extract_type1(text):
    leader = []
    pattern_all = re.compile('2em;*">\s*(.*)</p>?')  # 问题：正则匹配获取有用信息
    all_info = re.findall(pattern_all, text)

    pattern_party = re.compile('.*，(.*)年.*加入([\u4e00-\u9fa5]*)，')  # 获得入党时间，党派
    party_info = re.findall(pattern_party, all_info[0])
    if len(party_info) == 0:
        party_info = [('', '')]

    pattern_degree = re.compile('.*，(.*)学位')  # 获得学历/专业
    degree_info = re.findall(pattern_degree, all_info[0])
    if len(degree_info) == 0:
        degree_info = re.findall('.*，(.*)学历', all_info[0])
        if '研究生' in degree_info[0]:
            degree_info = [degree_info[0][:-3]]
    elif '、' in degree_info[0]:
        degree_info = degree_info[0].split('、')
        degree_info = [degree_info[-1]]

    splited = all_info[0].split('，')

    leader.append(splited[0])
    leader.append(splited[1])
    leader.append(splited[2])
    leader.append(splited[3][:4])
    leader.append(splited[4][:2])
    leader.append(party_info[0][0])
    leader.append(party_info[0][1])
    leader.append(degree_info[0][:-2])
    leader.append(degree_info[0][-2:])

    track_temp = []
    for sentence in all_info:
        if sentence[0] == '2' or sentence[0] == '1':  # 进修学习，考虑到年代的特殊性，也视为升迁的一种，平调被省略
            track_temp.append(sentence[:4])
    track = ','.join(track_temp)
    leader.append(track)
    print(leader)

    return leader


def extract_type2(text):
    leader = []
    name = re.findall('.*center;">\s*([\u4e00-\u9fa5]*·*[\u4e00-\u9fa5]*)</p>\s', text)  # 获取名字
    pattern_all = re.compile('2em;*">\s*(.*)</p>?')  # 问题：正则匹配获取有用信息
    all_info = re.findall(pattern_all, text)

    pattern_party = re.compile('.*，(.*)年.*加入([\u4e00-\u9fa5]*)，')  # 获得入党时间，党派
    party_info = re.findall(pattern_party, all_info[0])
    if len(party_info) == 0:
        party_info = [('', re.findall('.*，(.*)成员', all_info[0])[0])]
    pattern_degree = re.compile('.*，(.*)学位')  # 获得学历/专业
    degree_info = re.findall(pattern_degree, all_info[0])
    if len(degree_info) == 0:
        degree_info = re.findall('.*，(.*)学历', all_info[0])
        if '研究生' in degree_info[0]:
            degree_info = [degree_info[0][:-3]]
    elif '、' in degree_info[0]:
        degree_info = degree_info[0].split('、')
        degree_info = [degree_info[-1]]

    splited = all_info[0].split('，')

    leader.append(name[0])
    leader.append(splited[0])
    leader.append(splited[1])
    leader.append(splited[2][:4])
    leader.append(splited[3][:2])
    leader.append(party_info[0][0])
    leader.append(party_info[0][1])
    leader.append(degree_info[0][:-2])
    leader.append(degree_info[0][-2:])

    track_temp = []
    for sentence in all_info:
        if sentence[0] == '2' or sentence[0] == '1':  # 进修学习，考虑到年代的特殊性，也视为升迁的一种，平调被省略
            track_temp.append(sentence[:4])
    track = ','.join(track_temp)
    leader.append(track)
    print(leader)

    return leader


def main():
    leader_info = []

    for i in range(3, 50):
        if i < 10:
            offset = '0' + str(i)
        else:
            offset = str(i)
        url = 'http://cpc.people.com.cn/n1/2017/1025/c414940-296088' + offset + '.html'

        response = get_one_leader(url)
        if response:
            temp = extract_type1(response.content.decode('gb18030'))  # gb18030防止乱码
            leader_info.append(temp)

    for i in range(2, 15):
        offset = str(i)
        url = 'http://cpc.people.com.cn/n1/2018/0318/c64094-29873799-' + offset + '.html'

        response = get_one_leader(url)
        if response:
            temp = extract_type2(response.content.decode('gb18030'))  # gb18030防止乱码
            leader_info.append(temp)

    for i in range(2, 6):
        offset = str(i)
        url = 'http://cpc.people.com.cn/n1/2018/0320/c64094-29877085-' + offset + '.html'
        response = get_one_leader(url)
        if response:
            temp = extract_type1(response.content.decode('gb18030'))  # gb18030防止乱码
            leader_info.append(temp)

    for i in range(2, 25):
        offset = str(i)
        url = 'http://cpc.people.com.cn/n1/2018/0315/c64387-29868408-' + offset + '.html'
        response = get_one_leader(url)
        if response:
            temp = extract_type1(response.content.decode('gb18030'))  # gb18030防止乱码
            leader_info.append(temp)

    for i in range(2, 15):
        offset = str(i)
        url = 'http://cpc.people.com.cn/n1/2018/0315/c64387-29868408-' + offset + '.html'
        response = get_one_leader(url)
        if response:
            temp = extract_type1(response.content.decode('gb18030'))  # gb18030防止乱码
            leader_info.append(temp)

    with open('central.csv', 'w+', newline='', encoding='utf-8') as f:  # newline参数控制行之间是否空行
        f_csv = csv.writer(f)
        f_csv.writerow(['name', 'gender', 'race', 'age', 'hometown', 'party',
                        'party_standing', 'degree', 'major', 'track'])  # headers为表头属性名组成的数组
        f_csv.writerows(leader_info)


if __name__ == '__main__':
    main()
