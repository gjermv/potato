from PyQt4 import QtGui

# import the UI from the generated file
from trainingAnalyzer_Form import Ui_MainWindow
from PyQt4 import QtCore, QtGui
import gpx_file_formater
import training_analyzer
from segmentTimer import TrackSegment,CrossLine,SegmentResult
import matplotlib.pyplot as plt
import numpy as np
import pickle


class MyMainWindow(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.openfiledialog)
        self.pushButton_2.clicked.connect(self.savefile)
        self.pushButton_3.clicked.connect(self.opendirdialog)
        
        self.comboBox.activated.connect(self.activityButtonChanged)
        
        self.webView.setUrl(QtCore.QUrl("C:\\python\\resc\\map.html"))
        self.webView.loadFinished.connect(self.onLoadFinished)
        
        self.label.setStyleSheet("image: url(C:/python/resc/pRect.png);")
        

    def openfiledialog(self):
        self.fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file','C:\\Users\\Gjermund\\Downloads\\gpx-n',("GPS files (*.tcx *.gpx)"))
        #'C:\\Users\\gjermund.vingerhagen\\Downloads\\'
        if self.fname:
            self.lineEdit_file_name.setText(self.fname)
            self.lineEdit_file_newname.setText('Please wait')
            newname = gpx_file_formater.getNewFileName(self.fname)
            self.lineEdit_file_newname.setText(newname)
            self.onReadFileFinished()

            self.data = training_analyzer.getTrainingData(self.fname)
            data = self.data
            
            self.lab_date.setText(data['dateandtime'].strftime('%Y-%m-%d %H:%M:%S'))
            self.lab_length.setText(str(data['length']))
            self.lab_tottime.setText(str(data['tottime']))
            self.lab_climb.setText(str(data['climbing']))
            self.lab_walktime.setText(str(data['walk_time']))
            self.lab_avgspeed.setText(str(data['avg_speed']))
        
            self.label.setStyleSheet("image: url(C:/python/resc/pRect2.png);")
            self.label_elevation.setStyleSheet("image: url(C:/python/resc/elevationProfile.png);")
            self.label_speed.setStyleSheet("image: url(C:/python/resc/speedProfile.png);")
            self.label_hr.setStyleSheet("image: url(C:/python/resc/hrProfile.png);")
            
    def opendirdialog(self):
        print("openfiledialog")
        fname = QtGui.QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\python\\gpstracks\\files', QtGui.QFileDialog.ShowDirsOnly)
        if fname:
            self.lineEdit_file_saveto.setText(fname)
         
    def onLoadFinished(self):
        with open("C:\\python\\resc\\map.js", 'r') as f:
            frame = self.webView.page().mainFrame()
            frame.evaluateJavaScript(f.read())
            
    def onReadFileFinished(self):
        with open("C:\\python\\resc\\map.js", 'r') as f:
            frame = self.webView.page().mainFrame()
            frame.evaluateJavaScript(training_analyzer.getTrackData(self.fname))
            frame.evaluateJavaScript(training_analyzer.getTrackBounds(self.fname))

    def activityButtonChanged(self):
        actbox_txt = self.comboBox.currentText()
        comment_txt = self.textEdit.toPlainText()
        originalfile = self.lineEdit_file_name.text()
        filename = self.lineEdit_file_newname.text()
        print(filename)
        
        df = training_analyzer.insertToGPXDatabase(originalfile,filename, actbox_txt, comment_txt,self.data)
        self.textEdit_2.setPlainText(training_analyzer.getStatistic(df, filename))
        #self.textEdit_3.setPlainText(training_analyzer.getSegmentResults(filename,originalfile,actbox_txt))

    def savefile(self):
        origfile = self.lineEdit_file_name.text()
        path = self.lineEdit_file_saveto.text()
        newname = self.lineEdit_file_newname.text()
        
        self.data['filename'] = newname
        self.data['activity'] = self.comboBox.currentText()
        self.data['comment'] = self.textEdit.toPlainText()
        self.data['segments'] = ''
        
        if len(newname)> 0 and len(path) > 0:
            try:
                #training_analyzer.checkForNewFiles('C:\\python\\testdata\\gpxx4\\files\\*.*')
                training_analyzer.saveGPSFile(origfile,additional_info=self.data)
                gpx_file_formater.copyGPSFile(origfile,path,newname)
            
            except:
                print("Something went wrong saving the file")

if __name__ == '__main__':
    app = QtGui.QApplication([])
    win = MyMainWindow()
    win.show()
    app.exec_()