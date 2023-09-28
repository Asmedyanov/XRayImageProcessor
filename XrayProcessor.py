import os
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from tkinter import filedialog
from matplotlib import pyplot as plt
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\User\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'


class XrayProcessor:
    def __init__(self):
        self.dir = os.curdir
        self.load_folder_before()
        self.load_folder_after()
        # self.get_text()
        # self.show_example()
        self.get_avg()
        self.align_brightness()
        self.save_result()

    def save_result(self):
        os.chdir(self.dir)
        try:
            os.mkdir('Result')
        except Exception as ex:
            print(ex)
        for name,image in zip(self.list_names_after,self.list_after):
            image_contrast = np.where(image<0.05*image.mean(),0.1*image,1.0*image)
            image_to_save = Image.fromarray(image_contrast)#.convert('RGB')
            image_to_save.save(f'Result/{name}')

    def align_brightness(self):
        max_before = np.mean(self.list_avg_before)
        sum = self.list_avg_before[0]
        for i, avg in enumerate(self.list_avg_before):
            self.list_before[i] = self.list_before[i]*max_before / avg
            self.list_before[i] = self.list_before[i]*0.25/self.list_before[i].max()
            if i==0:
                sum = self.list_before[i]
            else:
                sum = sum+self.list_before[i]
        sum = sum/len(self.list_before)
        plt.imshow(sum)
        plt.show()
        for i, avg in enumerate(self.list_avg_after):
            self.list_after[i] = self.list_after[i]*max_before / avg
            self.list_after[i] = self.list_after[i] * 0.25 / self.list_after[i].max()
            #self.list_after[i] = sum-self.list_after[i]
            #self.list_after[i] = self.list_after[i]-self.list_after[i].min()

    def get_avg(self):
        self.list_avg_before = []
        self.list_avg_after = []
        for image in self.list_before:
            image_cut = image[:230, :240]
            avg = image_cut.mean()
            self.list_avg_before.append(avg)
        for image in self.list_after:
            image_cut = image[:230, :240]
            avg = image_cut.mean()
            self.list_avg_after.append(avg)

    def get_text(self):
        self.list_text_image_before = []
        self.list_text_before = []
        self.list_text_image_after = []
        self.list_text_after = []
        for image in self.list_before:
            image_cut = image[238:, 240:]
            self.list_text_image_before.append(image_cut)
            try:
                text = pytesseract.image_to_string(image_cut,
                                                   config='--psm 10 --oem 1 -c tessedit_char_whitelist=0123456789ns')
                text = text.split('n')[0]
                text = text.replace(',', '.')
                text = int(text)
                self.list_text_before.append(text)
            except Exception as ex:
                print(ex)
        self.time_array_before = np.array(self.list_text_before)

        for image in self.list_after:
            image_cut = image[238:, 240:]
            self.list_text_image_after.append(image_cut)
            try:
                text = pytesseract.image_to_string(image_cut,
                                                   config='--psm 10 --oem 1 -c tessedit_char_whitelist=0123456789ns')
                text = text.split('n')[0]
                text = text.replace(',', '.')
                text = int(text)
                self.list_text_after.append(text)
            except Exception as ex:
                print(ex)
        self.time_array_after = np.array(self.list_text_after)

    def show_example(self):
        plt.imshow(self.list_text_image_before[0])
        plt.show()

    def load_folder_before(self):
        self.directory = filedialog.askdirectory()
        os.chdir(self.directory)
        self.list_before = []
        self.list_names_before = []
        for name in os.listdir():
            if name[-5:] == '.tiff':
                image = Image.open(name)
                self.list_before.append(np.asarray(image))
                self.list_names_before.append(name)
        os.chdir(self.dir)

    def load_folder_after(self):
        self.directory = filedialog.askdirectory()
        os.chdir(self.directory)
        self.list_after = []
        self.list_names_after = []
        for name in os.listdir():
            if name[-5:] == '.tiff':
                image = Image.open(name)
                self.list_after.append(np.asarray(image))
                self.list_names_after.append(name)
        os.chdir(self.dir)
