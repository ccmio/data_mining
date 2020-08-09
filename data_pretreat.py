import pandas as pd
import csv
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import random
import pickle
pd.set_option('display.max_columns', 1000, 'max_rows', 100000, 'expand_frame_repr', False)

data = pd.read_csv('data.csv', header=0, index_col=0)
data = data[data['track'].notnull()]  # 删除track为nan的行
data.drop_duplicates(['name'], inplace=True)  # 不同数据库中因为官员兼任，去除重复项

# 删除履历过少的对象并求平均升迁时间
avg_list = []
for row in data.iterrows():
    temp = row[1]['track'].split(',')
    temp = list(map(int, temp))
    r_list = []
    for idx, year in enumerate(temp):  # 删除同年时间
        while (idx < len(temp)-1):
            idx += 1
            if temp[idx] <= year:
                r_list.append(idx)
    temp = [temp[i] for i in range(0, len(temp)) if i not in r_list]
    if len(temp) <= 5:
        data.drop(row[0], axis=0, inplace=True)
    else:
        avg = round((temp[-1] - temp[0])/(len(temp) - 1), 1)
        avg_list.append(avg)

data = data.reset_index(drop=True)
data['avg'] = np.array(avg_list)  # 添加平均升迁间隔信息
data.drop(['track'], axis=1, inplace=True)

# 填充nan
data['major'].replace('无', np.nan, inplace=True)
data['p_year'].replace(0, np.nan, inplace=True)

# 性别 男male 女female
data['gender'].replace(['男', '女'], [1, 2], inplace=True)
# 民族 汉族han 少数民族minority
data['race'].replace('汉族', 1, inplace=True)
data.loc[data['race'] != 1, 'race'] = 2
# 学历  中央党校+专科xue(专科2，党校9，合并） 硕士shuo 博士bo
data['degree'].replace(['学士', '硕士', '博士'], [1, 2, 3], inplace=True)
data['degree'].replace(['大专', '党校'], 4, inplace=True)
# 学位类别 一级学科所属学位类别
data['major'].replace(['工商管理', '公共管理'], '管理学', inplace=True)
data['major'].replace(['工程', '昆虫学'], ['工学', '理学'], inplace=True)
data['major'].replace(['农业', '林学'], '农学', inplace=True)
data['major'].replace(['法律', '政策分析'], '法学', inplace=True)
data['major'].replace(['管理学', '经济学', '工学', '法学', '理学', '农学', '文学', '哲学', '历史学', '教育学', '医学'],
                      [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], inplace=True)

# 构造方位 代替省份
dir_list = []
for row in data.iterrows():
    if row[1]['hometown'] == '黑龙江' or row[1]['hometown'] == '吉林' or row[1]['hometown'] == '辽宁':
        dir_list.append(1)
    elif row[1]['hometown'] == '北京' or row[1]['hometown'] == '天津' or row[1]['hometown'] == '河北' \
        or row[1]['hometown'] == '内蒙古' or row[1]['hometown'] == '山西':
        dir_list.append(2)
    elif row[1]['hometown'] == '新疆' or row[1]['hometown'] == '青海' or row[1]['hometown'] == '甘肃'\
        or row[1]['hometown'] == '宁夏' or row[1]['hometown'] == '陕西':
        dir_list.append(3)
    elif row[1]['hometown'] == '西藏' or row[1]['hometown'] == '四川' or row[1]['hometown'] == '重庆'\
        or row[1]['hometown'] == '贵州' or row[1]['hometown'] == '云南':
        dir_list.append(4)
    elif row[1]['hometown'] == '河南' or row[1]['hometown'] == '湖北' or row[1]['hometown'] == '湖南':
        dir_list.append(5)
    elif row[1]['hometown'] == '山东' or row[1]['hometown'] == '安徽' or row[1]['hometown'] == '江苏' \
         or row[1]['hometown'] == '江西' or row[1]['hometown'] == '浙江' or row[1]['hometown'] == '福建'\
            or row[1]['hometown'] == '上海':
        dir_list.append(6)
    elif row[1]['hometown'] == '广西' or row[1]['hometown'] == '广东' or row[1]['hometown'] == '海南' \
         or row[1]['hometown'] == '台湾':
        dir_list.append(7)
    else:
        print('attention!')
data['dir'] = dir_list

# 籍贯 （4位无法查证籍贯的领导，以工作历任地点的众数填充）
data['hometown'].replace(['山东', '河南', '江苏', '湖南', '河北', '湖北', '安徽', '重庆', '辽宁',
                         '浙江', '四川', '山西', '广东', '陕西', '江西', '黑龙江', '广西', '内蒙古',
                         '吉林', '云南', '福建', '贵州', '天津', '甘肃', '宁夏', '上海', '新疆',
                         '北京', '青海', '海南', '西藏', '台湾'],
                        ['lu', 'yu4', 'su', 'xiang', 'ji4', 'e', 'hui', 'yu2', 'liao',
                         'zhe', 'chuan', 'jin3', 'yue', 'shan', 'gan4', 'hei', 'gui', 'meng',
                         'ji2', 'dian', 'min', 'qian', 'jin1', 'gan1', 'ning', 'hu', 'xin',
                         'jing', 'qing', 'qiong', 'zang', 'tai'], inplace=True)

# 党派 共产党 民主党派 无党派
data['party'].replace(['中国共产党', '无'], [1, 2], inplace=True)
data.loc[(data['party'] != 1) & (data['party'] != 2), 'party'] = 3

data['age'] = 2020 - data['age']
data['p_year'] = 2020 - data['p_year']

# 年龄 分箱 年龄反应了所处的时代的升迁速度
bins = [39, 44, 49, 54, 59, 64, 69, 100]
data['age'] = pd.cut(data['age'], bins, labels=[1, 2, 3, 4, 5, 6, 7])

# 党龄 均值填充及分箱， 10年一分
p_year_list = []
for row in data[(data['p_year'].isnull()) & (data['party'] == 1)].iterrows():
    avg = data.groupby(['gender', 'age', 'party'])['p_year'].mean()[row[1]['gender']][row[1]['age']][row[1]['party']]
    p_year_list.append(avg)
data.loc[(data['p_year'].isnull()) & (data['party'] == 1), 'p_year'] = p_year_list

data.loc[data['party'] == 3, 'p_year'] = 1
data.loc[data['party'] == 2, 'p_year'] = 2
bins = range(15, 60, 10)
data.loc[data['party'] == 1, 'p_year'] = pd.cut(data.loc[data['party'] == 1, 'p_year'], bins, labels=[3, 4, 5, 6])

mean_num = data['avg'].mean()
mid_num = data['avg'].median()
mod_num = data['avg'].mode()
print('\nmean:', mean_num)
print('\nmod:', mod_num[0])
print('\nmid:', mid_num)
# 2.6 2.5 2.753
# 升迁速度分箱
bins = [1, 2.9, 10]
cut = pd.cut(data['avg'], bins)
print(pd.value_counts(cut))

data['avg'] = pd.cut(data['avg'], bins, labels=[1, 0])

# 专业填充 党校/大专 专业为z
data.loc[(data['degree'] == 4), 'major'] = 1
major_list = []
for row in data[data['major'].isnull()].iterrows():
    major = pd.Series.mode(data.loc[(data['gender'] == row[1]['gender']) & (data['age'] == row[1]['age']) & (data['major'] != 1), 'major'])
    rint = random.randint(0, len(major)-1)
    major_list.append(major.values[rint])
data.loc[data['major'].isnull(), 'major'] = major_list

data = data.reset_index(drop=True)
data.drop(['name'], axis=1, inplace=True)
data.drop(['hometown'], axis=1, inplace=True)

# print(data)
print('总数据量：', len(data))

# for col in data.columns.tolist():
#     print(data[col].value_counts())
#     missing_num = data[col].isnull().sum()
#     if missing_num:
#         print('Missing value:{:10s} : {:5}, ({:.1f}%) '.format(col, missing_num, missing_num * 100 / len(data)))

# length = np.array(length)
# # 对数据进行切片，将数据按照从最小值到最大值分组，分成20组
# bins = np.linspace(min(length), max(length), 80)
#
# # 这个是调用画直方图的函数，意思是把数据按照从bins的分割来画
# plt.hist(length,bins)
# #设置出横坐标
# plt.xlabel('职位变动次数')
# #设置纵坐标的标题
# plt.ylabel('频数')
# #设置整个图片的标题
# plt.show()

data = data[['gender', 'race', 'age', 'dir', 'p_year', 'party', 'major', 'degree', 'avg']]
data = data.reset_index(drop=True)
data.to_csv('./clean_data.csv', sep=',', header=True, index=True)

