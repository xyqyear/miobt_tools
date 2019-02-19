## 简介
本程序用于定时自动从[miobt](http://miobt.com)获取番剧信息并自动创建transmission任务下载

**注意：**\
此程序的使用需要一定的Python/Json知识



## 配置运行环境
### 1.安装Python3.6+
1.安装python：\
略\
2.安装依赖库：

	pip install bcoding schedule requests transmissionrpc


### 2.安装transmission
**Linux：**
1.Ubuntu/Debian/Raspbian/其他debian系系统：

	apt-get install transmission-daemon

2.RedHat/CentOS/其他redhat系系统：

_未测试_

**Windows:**

去[transmission官网](https://transmissionbt.com/download/)下载适合自己的.msi安装文件\
安装好之后打开界面,一路确定.

### 3.修改transmission配置
**Linux:**\
配置文件位置: /etc/transmission-daemon/settings.json\
修改“download-dir”为下载文件保存文件夹\
确保“rpc-enabled”值为true\
**Windows:**\
1.修改  **编辑--首选项--下载--保存到位置** 为种子下载位置\
2.修改  **编辑--首选项--远程--勾选允许远程访问**

### 4.修改config.py
修改dowbload_path为刚刚在transmission配置文件中设置的路径\
修改ip_address为安装了transmission机器的地址，如果是本机请填'127.0.0.1'\
(Linux默认用户密码)修改username和password都为'transmission'(windows默认留空)\
密码也可以在上一步**修改transmission配置文件**修改\
最后按照范例修改anime_list

关于auto_copy和auto_remove:\
auto_copy代表每个番下完后是否自动复制到独立设置的番剧储存目录\
auto_remove代表是否在种子做种完成后删除相应的文件 ***如果auto_copy为False的话，此选项不会生效***\
seed_ratio代表此任务上传和下载之比(和transmission里的配置一致)(不知道的话可以不用管)

### 运行auto_download.py

请保证此程序一直运行。
