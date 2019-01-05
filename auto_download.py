# -*- coding:utf-8 -*-
import re
import os
import time
import json
import socket
import bcoding
import schedule
import requests
import transmissionrpc

from shutil import copy, rmtree

from config import *


def logger(*log, level=1):
    time_pre = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if level == 0:
        print('[{}][DEBUG]:'.format(time_pre), *log)
    if level == 1:
        print('[{}][MESSAGE]:'.format(time_pre), *log)
    if level == 2:
        print('[{}][WARNING]:'.format(time_pre), *log)


def split_path(path):
    """
    用于切割获得此相对目录的根目录,用于方便删除整个文件夹
    :param path:
    :return:
    """
    dir1, dir2 = os.path.split(path)
    if dir1 == '':
        return dir2
    else:
        return split_path(dir1)


def get_torrents(key_word, pages=1, recent=True):
    """
    获取磁力链接
    :param key_word: 关键词
    :param pages: 搜索页数
    :param recent: 是否只返回时间里带有'天'的(比如:'昨天','今天')
    :return:
    """
    torrents = list()

    for i in range(pages):
        # 获取网页内容
        url = f'http://miobt.com/search.php?keyword={key_word}'
        retry_count = 3
        content = ''
        while retry_count > 0:
            try:
                content = requests.get(url, headers=headers, timeout=15).text
                break
            except Exception as e:
                logger(e)
                if retry_count == 0:
                    return None
                retry_count -= 1

        # 去掉content中的换行,方便使用re
        content = content.replace('\n', '')
        tbody = re.findall(r'<tbody class="tbody" id="data_list">.*</tbody>', content)
        if tbody:
            tbody = tbody[0]
        else:
            return None
        # 获得每个搜索结果
        trs = re.findall(r'<tr class="alt\d">.*?</tr>', tbody)
        for tr in trs:
            # 0:时间,1:类别,2:标题和链接,3:大小,4:种子,5:下载,6:完成,7:UP主/代号
            tds = re.findall(r'<td.*?</td>', tr)
            date = re.sub(r'<.*?>', '', tds[0]).strip()
            # 如果recent为True且不是近几天的,就跳过
            if recent and '天' not in date:
                continue
            torrent_hash = re.findall(r'show-(.*)\.html', tds[2])[0]
            magnet_url = 'magnet:?xt=urn:btih:{}&tr=http://open.acgtracker.com:1096/announce' \
                .format(torrent_hash)
            title = re.sub(r'<.*?>', '', tds[2])
            # 刚刚发现标题中可能有像这样的情况: "[简体内嵌][合集]                    共1条留言", 所以调整下
            title = re.sub(r'共\d+条留言', '', title).strip()

            author = re.sub(r'<.*?>', '', tds[7])

            torrent = dict(date=date,
                           hash=torrent_hash,
                           magnet_url=magnet_url,
                           title=title,
                           author=author)
            torrents.append(torrent)

        if pages > 1:
            time.sleep(3)
    return torrents


def choose_torrents(torrents, preference):
    """
    根据UP主筛选种子,UP主优先级越高,就越放在preference的前面
    :param torrents: 种子列表
    :param preference: UP主优先级列表
    :return:
    """
    if not preference:
        return torrents[0]

    for i in preference:
        for torrent in torrents:
            if i == torrent['author']:
                return torrent

    return None


def get_one_torrent(keyword, preference):
    """
    获得一个种子
    :param keyword:
    :param preference:
    :return:
    """
    torrents = get_torrents(keyword)
    if torrents:
        return choose_torrents(torrents, preference)
    else:
        return None


def get_torrent_file(torrent_hash):
    """
    用于下载种子文件
    :param torrent_hash:
    :return:
    """
    url = 'http://v2.uploadbt.com/?r=down&hash={}'.format(torrent_hash)
    retry_count = 3
    content = bytes()
    while retry_count > 0:
        try:
            content = requests.get(url, headers=headers, timeout=15).content
            break
        except Exception as e:
            logger(e)
            if retry_count == 0:
                return False
            retry_count -= 1
    file_name = '{}.torrent'.format(torrent_hash)
    with open(file_name, 'wb') as f:
        f.write(content)
    return file_name


def get_torrent_file_list(file_path):
    """
    输入种子文件路径,返回文件们的相对路径(利用种子文件)
    :param file_path: 种子文件路径
    :return:
    """
    with open(file_path, 'rb') as f:
        torrent_content = f.read()
    raw_info_dict = bcoding.bdecode(torrent_content)['info']
    handled_file_list = []
    if 'files' not in raw_info_dict:
        handled_file_list = [raw_info_dict['name']]
    else:
        for file in raw_info_dict['files']:
            handled_file_list.append(os.path.join(raw_info_dict['name'], *file['path']))

    return handled_file_list


class Manager:
    def __init__(self):
        self.anime_list = anime_list
        self.tasks = {}
        self.archived_tasks = {}
        if username and password:
            self.transmission_client = transmissionrpc.Client(ip_address, port, username, password)
        else:
            self.transmission_client = transmissionrpc.Client(ip_address, port)
        self.load_tasks()

    def run(self):
        for keyword, anime_info in self.anime_list.items():
            download_time = anime_info['time']
            if anime_info['date'] == 'monday':
                schedule.every().monday.at(download_time).do(self.add_task, keyword)
            if anime_info['date'] == 'tuesday':
                schedule.every().tuesday.at(download_time).do(self.add_task, keyword)
            if anime_info['date'] == 'wednesday':
                schedule.every().wednesday.at(download_time).do(self.add_task, keyword)
            if anime_info['date'] == 'thursday':
                schedule.every().thursday.at(download_time).do(self.add_task, keyword)
            if anime_info['date'] == 'friday':
                schedule.every().friday.at(download_time).do(self.add_task, keyword)
            if anime_info['date'] == 'saturday':
                schedule.every().saturday.at(download_time).do(self.add_task, keyword)
            if anime_info['date'] == 'sunday':
                schedule.every().sunday.at(download_time).do(self.add_task, keyword)

        schedule.every().minute.do(self.get_status)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def save_tasks(self):
        with open('tasks.json', 'w') as f:
            f.write(json.dumps(self.tasks))

        with open('archived_tasks.json', 'w') as f:
            f.write(json.dumps(self.archived_tasks))

    def load_tasks(self):
        if os.path.exists('tasks.json') and os.path.exists('archived_tasks.json'):
            with open('tasks.json', 'r') as f:
                self.tasks = json.loads(f.read())

            with open('archived_tasks.json', 'r') as f:
                self.archived_tasks = json.loads(f.read())

    def add_task_next_time(self, keyword, retry_count):
        self.add_task(keyword, retry_count)
        return schedule.CancelJob

    def add_task(self, keyword, retry_count=6):
        """
        添加任务
        :param keyword: 搜索时的关键字
        :param retry_count: 搜索到目标种子为止的重试次数
        :return:
        """
        torrent = get_one_torrent(keyword, self.anime_list[keyword]['preference'])
        logger('got_torrent:', torrent, level=0)
        # 如果未找到,就再次尝试多次
        if not torrent:
            if retry_count > 0:
                logger(keyword, ':目标种子未找到,休息一小时')
                schedule.every().hour.do(self.add_task_next_time, keyword, retry_count-1)
                return

            else:
                return
        # 如果种子已经下载过就跳过
        if torrent['hash'] in self.tasks or torrent['hash'] in self.archived_tasks:
            logger(torrent['title'], ':种子已下载,跳过')
            return

        # 新建一个任务,以种子哈希值作为任务名,方便以后判断任务是否存在
        task = dict(keyword=keyword,  # 种子搜索时的关键词
                    title=torrent['title'],  # miobt上的标题
                    magnet_url=torrent['magnet_url'],  # 种子链接
                    status='downloading',  # 种子状态 downloading -> seeding -> stopped
                    torrent_id=0,  # 种子在transmission中的id
                    file_list=[],
                    copied=False)  # 种子文件列表
        torrent_file = get_torrent_file(torrent['hash'])
        task['file_list'] = get_torrent_file_list(torrent_file)
        torrent_file_full_path = 'file://' + os.path.join(os.path.abspath('.'), torrent_file)

        transmission_task = self.transmission_client.add_torrent(torrent_file_full_path)
        os.remove(torrent_file)
        task['torrent_id'] = transmission_task.id
        logger(task['title'], ': 任务创建成功')
        self.tasks[torrent['hash']] = task

    def get_status(self):
        for torrent_hash, task_info in self.tasks.items():
            # 获取任务状态的时候可能会连接超时 (因为我家路由器有时候要重启=a=
            try:
                torrent_task = self.transmission_client.get_torrent(task_info['torrent_id'])
            except transmissionrpc.error.TransmissionError:
                return
            except socket.timeout:
                return

            task_info['status'] = torrent_task.status

        self.handle_status()

    def handle_status(self):
        to_del_hash = []
        for torrent_hash, task_info in self.tasks.items():
            # 如果是seeding状态的话,就复制文件到番剧目录,并且标记状态为copied
            if auto_copy and task_info['status'] == 'seeding' and not task_info['copied']:
                logger(task_info['title'], ': 下载完成,正在复制文件')
                for file_path in task_info['file_list']:
                    src = os.path.join(download_path, file_path)
                    dist = os.path.join(anime_list[task_info['keyword']]['path'], file_path)
                    copy(src, dist)
                logger(task_info['title'], ': 文件复制完成')
                task_info['copied'] = True
            # 如果是stopped状态就说明做种完成,删除任务并删除数据,归档数据
            elif auto_remove and task_info['status'] == 'stopped' and task_info['copied']:
                logger(task_info['title'], ': 做种完成,正在删除文件')
                self.archived_tasks[torrent_hash] = task_info
                to_del_hash.append(torrent_hash)

                if len(task_info['file_list']) > 1:
                    _dir = split_path(task_info['file_list'][0])
                    rmtree(os.path.join(download_path, _dir))
                else:
                    os.remove(os.path.join(download_path, task_info['file_list'][0]))

                logger(task_info['title'], ': 删除完成,任务已存档')

        for torrent_hash in to_del_hash:
            del self.tasks[torrent_hash]

        self.save_tasks()
        # 代替以前的那个自动移除transmission任务的脚本
        if auto_remove:
            self.del_other_task()

    def del_other_task(self):
        try:
            torrents = self.transmission_client.get_torrents()
        except transmissionrpc.error.TransmissionError:
            return
        except socket.timeout:
            return

        for torrent in torrents:
            if torrent.status == 'stopped':
                logger('已删除任务: ', torrent.name)
                try:
                    self.transmission_client.remove_torrent(torrent.id)
                except transmissionrpc.error.TransmissionError:
                    return
                except socket.timeout:
                    return


def demo():
    torrents = get_torrents('悠哉日常大王', pages=10, recent=False)
    print(json.dumps(torrents))
    chosen_torrent = choose_torrents(torrents, ['千夏字幕组', 'c.c动漫'])
    print(chosen_torrent)


def main():
    manager = Manager()
    manager.run()


if __name__ == '__main__':
    # demo()
    main()
