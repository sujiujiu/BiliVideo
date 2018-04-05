# -*- coding:utf-8 -*-
import xlwt

# book = xlwt.Workbook(encoding='utf-8')

# sheet = book.add_sheet('sheet', cell_overwrite_ok=True)


class SaveToExcel(object):

    def __init__(self, title_name_list, save_path):
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


    def write_sheet(self, col, titles):
        '''写入sheet表
        格式：sheet.write(row, col, item)
        '''
        for row, item in enumerate(titles):        
            self.sheet.write(row+1, col, item)

    def add_item(self, title_lists, items):
        '''将元素添加到对应的列表里
        
        [description]
        
        Arguments:
            title_lists {[list]} -- 标题的列表
            items {[list]} -- 要添加的内容
        
        Returns:
            else_list[list] -- 多维数组
        '''
        else_list = []
        for title_list in title_lists:
            for item in items:
                title_list.append(item)
            else_list.append(title_list)
        return else_list

    def save_sheet(self, items):
        '''保存到sheet表
        '''
        title_lists = [[] for i in xrange(len(self.title_name_list))]
        # 最上一层标题
        for index, t_name in enumerate(self.title_name_list):
            self.sheet.write(0, index, t_name, self.style1)

        else_list = self.add_item(title_lists, items)
        # 其他要填充的内容
        for col, title_list in enumerate(else_list):
            self.write_sheet(col, title_list)
        self.book.save(self.save_path)




