# -*- coding:utf-8 -*-

# headers可以自定义,但是一般没必要
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/70.0.3538.102 Safari/537.36'}

anime_list = {}

# 下面是范例
# anime_list = {
#     '兔女郎': {
#         'preference': ['c.c动漫', 'c-a Raws'],  #这个是字幕组的偏向,访问 miobt.com 就知道应该怎么选啦,如果留为[]就是选最近的
#         'date': 'thursday',
#         'time': '03:00',
#         'path': '/nfs/Own/ACGN/Anime/青春猪'},
#     '魔法禁书目录': {
#         'preference': ['c.c动漫', 'c-a Raws'],
#         'date': 'saturday',
#         'time': '00:00',
#         'path': '/nfs/Own/ACGN/Anime/魔禁3'},
#     '刀剑神域 Alicization': {
#         'preference': ['c.c动漫', 'c-a Raws'],
#         'date': 'sunday',
#         'time': '01:00',
#         'path': '/nfs/Own/ACGN/Anime/刀剑_Alicization'}
# }

download_path = ''  # 这是transmission的下载目录,要和transmission的下载目录设置一致
ip_address = '192.168.10.125' # transmission rpc的地址(默认值只是个例子)
port = 9091 # 这个一般留默认

# 这个是transmission rpc的账号密码,没有设置可以留空
username = ''
password = ''

# 是否是debug模式
debug_mode = False