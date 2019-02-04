## 简介
本程序用于定时自动从[miobt](http://miobt.com)获取番剧信息并自动创建transmission任务下载\

**注意：**\
此程序的使用需要一定的Python/Json知识



## 安装运行环境
### 1.安装Python3.6+
1.安装python：
略
2.安装依赖库：

	pip install bcoding schedule requests transmissionrpc


### 2.安装transmission
**Linux：**
1.Ubuntu/Debian/Raspbian/其他debian系系统：

	apt-get install transmission-daemon

2.RedHat/CentOS/其他redhat系系统：

_未测试_

**Windows:**

_未测试_

### 3.修改transmission配置文件

修改“download-dir”为下载文件保存文件夹\
确保“rpc-enabled”值为true

### 4.修改config.py

修改dowbload_path为刚刚在transmission配置文件中设置的路径\
修改ip_address为安装了transmission机器的地址，如果是本机请填'127.0.0.1'\
最后按照范例修改anime_list

关于auto_copy和auto_remove:\
auto_copy代表每个番下完后是否自动复制到独立设置的番剧储存目录\
auto_remove代表是否在种子做种完成后删除相应的文件 ***如果auto_copy为False的话，请务必使此变量也为False***

### 运行auto_download.py

请保证此程序一直运行。