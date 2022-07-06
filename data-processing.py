# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# Imports
from utils import *
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nrclex import NRCLex


df = pd.read_csv('kindle_reviews.csv', index_col=0)

# 删掉无用列
df.drop(['reviewTime', 'helpful', 'reviewerName', 'reviewerID', ], axis=1, inplace=True)

# 筛选评论数大于300的产品
id_count = df['asin'].value_counts()
id_df = pd.DataFrame(id_count)
id_moreThan_100 = id_df[id_df['asin'] > 300]
popular_df = pd.DataFrame()
id_index = id_moreThan_100.index.values
for i in id_index:
    filter_df = df.loc[df['asin'] == i]
    popular_df = pd.concat([filter_df, popular_df], ignore_index=True)
    
popular_df.reviewText = popular_df.reviewText.apply(lambda x: clean_text(str(x)))

stopwords = set(stopwords.words('english'))
stopwords.update(["br", "href"])

# contents stopwords 定义成为列表，把每一行装进列表里
contents = popular_df.reviewText.values.tolist()

#取出处理好的句子，和词
contents_clean, all_words = drop_stopwords(contents, stopwords)

popular_df['reviewText'] = contents_clean

popular_df['reviewText'] = popular_df['reviewText'].apply(text_lemmatization)

# 丢弃txt这列中有缺失值的行
popular_df.dropna(axis=0, subset = ["reviewText"])

# 将不同的product装到不同的csv里
product_set = set(popular_df['asin'])
for uniqueProduct in product_set:
    df = popular_df[popular_df['asin'] == uniqueProduct]
    csv_path = 'Processed_product/product_' + str(uniqueProduct) + '.csv'
    df.to_csv(csv_path, index=False)
    
# Sentiment analysis
for product in product_set:
    csv_path = 'Processed_product/product_' + str(product) + '.csv'
    df = pd.read_csv(csv_path)
    print('write file ' + csv_path)
    df.sort_values(by=['unixReviewTime'], inplace=True)
    df['reviewsInNext7Days'] = df.unixReviewTime.apply(lambda x: countReviewsInNext7Days(x))
    df['emotions'] = df['reviewText'].apply(lambda x: NRCLex(str(x)).affect_frequencies)
    df = pd.concat([df.drop(['emotions'], axis = 1), df['emotions'].apply(pd.Series)], axis = 1)
    new_csv_path = 'Analyzed_product_data/product_' + str(product) + '.csv'
    df.to_csv(new_csv_path)
    

