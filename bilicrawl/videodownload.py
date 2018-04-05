# -*-coding:utf-8-*-
import os
import sys
import urllib
import requests
from bs4 import BeautifulSoup

import xlwt

from constants import BASE_DOWN_URL, BASE_FILE_PATH, BARRAGE_BASE_DIR_NAME, \
    MP3_BASE_DIR_NAME, MP4_BASE_DIR_NAME, FLV_BASE_DIR_NAME, ERROR_BASE_DIR_NAME

reload(sys)
sys.setdefaultencoding('utf8')


class BiliVedioDownloadCrawl(object):

    def __init__(self, video_id, title_name_list, save_path):
        '''
        Arguments:
            video_id {[str]} -- 输入的id只能为av+num（视频），或者ep+num（番剧）
        '''
        self.video_id = video_id
        self.HEADERS = {
            "Host":"www.jijidown.com",
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        }
        self.video_url = self.get_video_down_url(self.video_id)
        self.req = self.get_req(self.video_url, error_file_name='jiji')
        self.soup = BeautifulSoup(self.req.content, 'lxml')
        self.video_name = self.get_video_total_title(self.soup)

        self.book = xlwt.Workbook(encoding='utf-8')
        self.sheet = self.book.add_sheet('sheet', cell_overwrite_ok=True)
        # 创建样式
        self.style1 = xlwt.XFStyle()
        self.font1 = xlwt.Font()
        # 字体加粗
        self.font1.bold = True
        self.style1.font = self.font1
        self.title_name_list = title_name_list
        self.save_path = save_path

    def get_video_down_url(self, video_id):
        '''不同视频对应的下载链接页面，根据输入的id，判断视频是单视频还是番剧，
            输入格式，必须带上前面的两个字符，如av&ep：
            eg:
                单视频:av21412072，
                番剧:ep198380
         
        Arguments:
            video_id {[str]} -- 视频id
        
        Returns:
            down_url[str] -- 不同视频对应的下载链接页面
        '''
        video_type = video_id[:2]
        if video_type == 'av':
            down_url = BASE_DOWN_URL + '/video/' + self.video_id
        elif video_type == 'ep':
            down_url = BASE_DOWN_URL + '/bangumi/play/' + self.video_id
        print down_url
        return down_url

    def get_req(self, url, error_file_name, params=None):
        while 1:
            try:
                req = requests.get(url, headers=self.HEADERS, params=params)
                break
            except Exception, e:
                error_file = os.path.join(BASE_FILE_PATH, error_file_name +'.txt')
                with open(error_file, 'a+') as error_f:
                    error_f.write(url+'\n')
                print url, e

        if req.status_code == 200:
            return req

    def get_video_total_title(self, soup):
        '''总标题，单视频的标题和番剧的总标题
        '''
        video_total_title = soup.find('div', {'class':'Win8-Title Title_No'}).text
        return video_total_title

    def get_bangumi_sub_title(self, Data_Box):
        '''针对于番剧和多P视频，有N篇番，每篇的标题
        '''
        bangumi_sub_title = Data_Box.find('span', {'class':'PBoxName'}).text
        return bangumi_sub_title
        
    def get_thunder_url(self, soup):
        '''迅雷下载地址
        '''
        xunlei = soup.find('div', {'class':'xunlei'})
        xunlei_parent = xunlei.find_parent('a')
        thunder_url = xunlei_parent['href']
        return thunder_url

    def get_xuanfeng_url(self, soup):
        '''旋风下载地址
        '''
        xuanfeng = soup.find('div', {'class':'xunlei'})
        xuanfeng_parent = xuanfeng.find_parent('a')
        xuanfeng_url = xuanfeng_parent['href']
        return xuanfeng_url

    def get_flv_url(self, Data_Box):
        '''flv格式的下载页面
        '''
        data_flv = Data_Box.find('span', {'class':'Data_Flv'})
        data_flv_a = data_flv.a
        if data_flv_a:
            flv_href = data_flv_a['href']
            flv_url = BASE_DOWN_URL + flv_href
        else:
            flv_url = 'None'
        return flv_url

    def get_flv_section_info(self, soup):
        '''flv视频分段，获取每段的地址及名称
            source：'http://www.jijidown.com/DownLoad/Cid/18221183'
        '''
        flv_section_infos = []
        flv_section_info = {}
        download_hrefs = soup.find_all('a', {'download':'download'})
        for download_href in download_hrefs:
            flv_section_info['flv_section_url'] = download_href['href'] 
            flv_section_info['flv_section_name'] = download_href.text
            flv_section_infos.append(flv_section_info)
        return flv_section_infos

    def get_data_mp4(self, Data_Box):
        '''MP3和MP4在同一个父标签下
        '''
        data_mp4 = Data_Box.find('span', {'class':'Data_Mp4'})
        mp4_a = data_mp4.find_all('a', attrs={'href':True})
        return mp4_a if mp4_a else None

    def get_mp3_page(self, mp4_a):
        '''mp3的下载页
        
        Arguments:
            mp4_a {[list]} -- MP3和MP4的同一个父标签获得的链接列表
        
        Returns:
            mp3_page[str] -- mp3的下载页
        '''
        if len(mp4_a) == 2:
            mp3_href = mp4_a[1]['href']
            mp3_page = BASE_DOWN_URL + mp3_href
        else:
            mp3_page = 'None'
            return mp3_page

    def get_mp4_page(self, mp4_a):
        '''mp4的下载页，默认格式是freedown，
        下载页面为：'http://www.jijidown.com/FreeDown/17053582.php'

        Arguments:
            mp4_a {[list]} -- MP3和MP4的同一个父标签获得的链接列表
        
        Returns:
            mp4_page[str] -- mp4的下载页
        '''
        mp4_href = mp4_a[0]['href']
        mp4_page = BASE_DOWN_URL + mp4_href
        return mp4_page

    def get_barrage_url(self, Data_Box, ass_type='xml'):
        '''弹幕下载地址
        
        Keyword Arguments:
            ass_type {str} -- 想要弹幕的格式(default: {'xml'})：
                -- ass_type='xml'则下载XML文件
                -- ass_type='ass'则下载ASS文件
        
        Returns:
            barrage_url[str] -- 弹幕下载地址
        '''
        data_ass = Data_Box.find('span', {'class':'Data_Ass'})
        ass_hrefs = data_ass.find_all('a')
        barrage_ass_url = ass_hrefs[0].a['href']
        barrage_xml_url = ass_hrefs[1].a['href']
        if ass_type == 'xml':
            barrage_url = BASE_DOWN_URL + barrage_xml_url
        else:
            barrage_url = BASE_DOWN_URL + barrage_ass_url
        return barrage_url

    def make_dir(self, path):
        '''如果路径不存在，则创建
        '''
        is_exists = os.path.exists(path)
        if not is_exists:
            os.mkdir(path)
        return path

    def make_new_dir(self, dir_name, video_name):
        '''根据当前视频的总标题创建文件夹
        '''
        new_dir_path = os.path.join(dir_name, video_name)
        current_dir = self.make_dir(new_dir_path)
        return current_dir

    def get_common_down_way_url(self, mp4_soup, down_way='xunlei'):
        '''迅雷和旋风下载的不同url
        
        Keyword Arguments:
            down_way {str} -- [description] (default: {'xunlei'})
        
        Returns:
            [type] -- [description]
        '''
        if down_way == 'xunlei':
            down_url = self.get_thunder_url(mp4_soup)
        else:
            down_url = self.get_xuanfeng_url(mp4_soup)
        return down_url

    def get_common_down_url(self, mp4_page, mp_num='4', down_way='xunlei'):
        '''MP3和MP4的公共部分
        
        Arguments:
            mp4_page {[type]} -- MP3和MP4的下载页面
        
        Keyword Arguments:
            down_way {str} -- [description] (default: {'xunlei'})
        
        Returns:
            [type] -- [description]
        '''
        mp4_req = self.get_req(mp4_page, error_file_name='mp%s' + mp_num)
        mp4_soup = BeautifulSoup(mp4_req, 'lxml')
        down_url = self.get_common_down_way_url(mp4_soup, down_way=down_way)
        return down_url

    def get_flv_down_url(self, flv_url, down_way='xunlei'):
        '''flv格式的下载页面，一种是分段页面，一种是迅雷、旋风页面
        
        [description]
        
        Arguments:
            flv_url {[type]} -- [description]
        
        Keyword Arguments:
            down_way {str} -- [description] (default: {'xunlei'})
        '''
        file_path = self.make_new_dir(FLV_BASE_DIR_NAME, self.video_name)
        flv_req = self.get_req(flv_url, error_file_name='flv')
        if flv_req.url == flv_url:
            flv_soup = BeautifulSoup(flv_req, 'lxml')
            flv_section_infos = self.get_flv_section_info(flv_soup)
            for flv_section_info in flv_section_infos:
                flv_section_url = flv_section_info['flv_section_url']
                flv_section_name = flv_section_info['flv_section_name']
                sub_path = os.path.join(file_path, flv_section_name)
                urlretrieve(flv_section_url, sub_path)
        else:
            flv_req = self.get_req(flv_req.url, error_file_name='flv')
            flv_soup = BeautifulSoup(flv_req, 'lxml')
            down_url = self.get_common_down_way_url(flv_soup, down_way=down_way)
            return down_url

    def download_video(self, Data_Box, down_type='mp4', down_way='xunlei'):
        '''根据需要（MP3/MP4/FLV）,下载视频（只提供迅雷和旋风下载）,需要自己启动迅雷
        '''
        if down_type == 'flv':
            flv_url = self.get_flv_url(Data_Box)
            down_url = self.get_flv_down_url(flv_url, down_way=down_way)
            # video_data.update({'down_url':down_url})
            return down_url
        else:
            data_mp4 = self.get_data_mp4(Data_Box)
            if data_mp4:
                if down_type == 'mp4':
                    mp4_page = self.get_mp4_page(data_mp4)
                    if mp4_page:
                        down_url = self.get_common_down_url(mp4_page, down_way=down_way)
                    else:
                        flv_url = self.get_flv_url(Data_Box)
                        down_url = self.get_flv_down_url(flv_url, down_way=down_way)
                    # video_data.update({'down_url':down_url})
                    return down_url
                
                elif down_type == 'mp3':
                    mp3_page = self.get_mp3_page(data_mp4)
                    if mp3_page:
                        down_url = self.get_common_down_url(mp3_page, mp_num='3', down_way=down_way)
                    else:
                        down_url = None
                    # video_data.update({'down_url':down_url})
                    return down_url
        return video_data

    def download_barrage(self, Data_Box, ass_type='xml'):
        '''下载弹幕到本地（单个视频）
        
        file_path为本地目录，名字 = 当前路径 + 视频的名字
        
        Keyword Arguments:
            ass_type {str} -- [description] (default: {'xml'})
        '''
        barrage_url = self.get_barrage_url(Data_Box, ass_type=ass_type)
        file_path = os.path.join(BARRAGE_BASE_DIR_NAME, ass_type, self.video_name)
        urlretrieve(barrage_url,file_path)

    def save_video_excel(self, down_type='mp4', down_way='xunlei'):
        total_names = []
        sub_names = []
        mp4_urls = []
        for index, t_name in enumerate(self.title_name_list):
            self.sheet.write(0, index, t_name, self.style1)

        # file_path = self.make_new_dir(MP4_BASE_DIR_NAME, self.video_name)
        Right_Main = self.soup.find('div',attrs={'id':'Right_Main'})
        data_nobgs = Right_Main.find_all('div',attrs={'data-nobg':'No','id':False})

        for data_nobg in data_nobgs:
            Data_Boxs = data_nobg.find_all('span', {'class':'Width-2 Box PBox'})
            for Data_Box in Data_Boxs:
                if Data_Box.find('a',attrs={'href':True}):
                    sub_title = self.get_bangumi_sub_title(Data_Box)
                else:
                    sub_title = 'None'

                down_url = self.download_video(Data_Box, down_type=down_type, down_way=down_way)
                # 下载弹幕
                # self.download_barrage(Data_Box, ass_type=ass_type)

                total_names.append(self.video_name)
                sub_names.append(sub_title)
                mp4_urls.append(down_url)

                for row, item in enumerate(total_names):        
                    self.sheet.write(row+1, 0, item)

                for row, item in enumerate(sub_names):        
                    self.sheet.write(row+1, 1, item)

                for row, item in enumerate(mp4_urls):        
                    self.sheet.write(row+1, 2, item)

                book.save(save_path)

            # 下载视频，将视频的迅雷链接写入文本
            # with open(sub_file_path, 'a+') as f:
            #     self.download_video(Data_Box, sub_title, down_type=down_type, down_way=down_way)


if __name__ == '__main__':
    save_path = 'd:\\bilivideo.xls'
    title_name_list = [u'番名',u'视频名',u'下载链接']
    video_id = 'av4551380'
    BiliVedioDownloadCrawl(video_id, title_name_list, save_path).save_video_excel()