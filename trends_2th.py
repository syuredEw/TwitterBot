# -*- coding:utf-8 -*-  

from six import u
import tweepy
import os
from tweepy.models import Status
import access_token
import MeCab
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np


# トレンドの順位を50位まで取得する関数
def get_twitter_trends(woeid):
    for area, wid in woeid.items():
        print("--- {} ---".format(area))
        trends = api.trends_place(wid)[0]
        #print(trends.keys()) #trends, as_of, created_of, locations
        #print(len(trends["trends"])) # 50
        #トレンドを格納するリスト
        body = [] 


        #トレンド順位を表示
        for i, content in enumerate(trends["trends"]):
            #print(i+1, content['name'])
            body.append(content['name'])
        #print("--------")
    return trends

#引数をtwitterで検索してツイートを取得
def gettwitterdata(keyword):

    #検索キーワード設定 RTを除外
    q = keyword + '-filter:links'
    #q ='日向坂46 -filter:links AND -filter:retweets'


    #つぶやきを格納するリスト
    tweets_data = []

    #カーソルを使用してデータを取得
    for tweet in tweepy.Cursor(api.search, q = q, count = 100, tweet_mode = 'extended').items(100):
        #つぶやき時間がUTCのためにJSTに変換　debug用
        #jsttime = tweet.created_at + datetime.timedelta(hours=9)
        #print(jsttime)

        #つぶやきテキストを取得
        tweets_data.append(tweet.full_text + '\n')

    #つぶやきテキストを返す
    return tweets_data

#WordCloudを用いて視覚化
def analyze_tweet(trends, trends_2th):
    
    #読み込みファイル名をせってい
    #fname = r"'" + dfile + "'"
    #fname = fname.replace("'", "")

    #MeCabを使って形態素解析
    mecab = MeCab.Tagger(r"-Ochasen -d C:\\ipadic-NEologd")

    #名詞，動詞，形容詞，副詞を格納するリスト
    words = []


    for tweet in trends:
        #MeCabで形態素解析を実施
        node = mecab.parseToNode(tweet)

        while node:
            word_type = node.feature.split(",")[0]

            #単語を取得
            if word_type in ["名詞", "形容詞", "動詞"]:

                words.append(node.surface)
            node = node.next
    
    #wordcloudで出力するフォントを指定
    font_path = r"C:\Windows\Fonts\meiryo.ttc"
    txt = " ".join(words)

    #ストップワードのせってい　＊これは検索キーワードによって除外したほうがいい単語

    stop_words = ['https', 'http', 't','co', 'jp', 'RT', u'てる', u'いる', u'なる', u'れる', u'する', u'ある', u'こと', u'これ', u'さん', u'して',\
              u'くれる', u'やる', u'くださる', u'そう', u'せる', u'した', u'思う',\
              u'それ', u'ここ', u'ちゃん', u'くん', u'', u'て', u'に', u'を', u'は', u'の', u'が', u'と', u'た', u'し', u'で', \
              u'ない', u'も', u'な', u'い', u'か', u'ので', u'よう', u'そこ',u'ン', u'ー',u'なり',u'られ',u'ん', u'ください', u'れ', u'でき']

    #マスクの生成
    mask_ary = np.zeros(shape=(800, 800))
    mask_ary = mask_ary.astype(np.uint8)

    for i in range(800):
        for j in range(800):
            if (i-400)**2 + (j-400)**2 > 380**2:
                mask_ary[i, j] = 255

    #解析した単語，ストップワードをせってい
    worldcouds = WordCloud(mask=mask_ary, font_path = font_path, stopwords = set(stop_words), contour_color='green', contour_width=1, prefer_horizontal=1, background_color='white', colormap='tab20').generate(txt)

    #画像のほぞん
    worldcouds.to_file("trends_2th.png")
    """
    plt.imshow(worldcouds)
    plt.axis("off")
    plt.show()
    """

    tweet = "日本の今のトレンド第1位は'" + trends_2th + "'だ！，関連ワードを可視化しました！ #python, #wordcloud"
    api.update_with_media(status=tweet, filename= "trends_2th.png")
    print("Success to tweet it!")

#フォローを返す関数
def follow_back():
    #自分のフォロワーのIDの取得
    follower_id = api.followers_ids()

    #自分のフォローのIDを取得
    follow_id = api.friends_ids()

    #フォローされているけど自分がフォローしていない人の取得
    not_followed_user_id = set(follow_id + follower_id) ^ set(follow_id)

    #フォローされていないけど自分がフォローしている人の取得
    #not_follower_user_id = set(follow_id + follower_id) ^ set(follower_id)

    number_of_followed, number_of_destroy_followed = 0, 0
    #フォローバックする
    for user_id in not_followed_user_id:
        try:
            api.create_friendship(user_id)
            number_of_followed += 1
        except Exception as e:
            print(e)
    #フォローバックした人数を表示
    print('number of followed : {}'.format(number_of_followed))

#apiインスタンスの作成
api = access_token.get_api_instance()

#tweetの範囲指定
woeid = {
    "日本": 23424856
}

#トレンド50位までを格納
get_trends = get_twitter_trends(woeid)

#トレンド第2位の単語を格納
trends_2th = get_trends["trends"][0]["name"]
print("日本の第1位のトレンドは" + trends_2th + "だ！")

#第2位のトレンドでつぶやかれているツイートを取得
trends_2th_tweet_date = gettwitterdata(trends_2th)
#確認用
#print(trends_2th_tweet_date)

#フォローを返す
follow_back()

# WordCloudの実行
analyze_tweet(trends_2th_tweet_date, trends_2th)




