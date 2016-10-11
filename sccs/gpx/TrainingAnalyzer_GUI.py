from PyQt4 import QtGui

# import the UI from the generated file
from gpx.trainingAnalyzer_Form import Ui_MainWindow
from PyQt4 import QtCore, QtGui
from gpx import gpx_file_formater
from gpx import training_analyzer
import matplotlib.pyplot as plt
import numpy as np


class MyMainWindow(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.openfiledialog)
        self.pushButton_3.clicked.connect(self.opendirdialog)
        self.pushButton_2.clicked.connect(self.savefile)
        self.comboBox.activated.connect(self.activityButtonChanged)
        
        self.webView.setUrl(QtCore.QUrl("C:\\python\\testdata\\map.html"))
        
        self.webView.loadFinished.connect(self.onLoadFinished)
        self.label.setStyleSheet("image: url(C:/python/image/pRect.png);")

    def openfiledialog(self):
        self.fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file','C:\\python\\testdata\\gpxx4\\files',("GPS files (*.tcx *.gpx)"))
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
        
            self.label.setStyleSheet("image: url(C:/python/image/pRect2.png);")
            self.label_elevation.setStyleSheet("image: url(C:/python/image/elevationProfile.png);")
            self.label_speed.setStyleSheet("image: url(C:/python/image/speedProfile.png);")
            self.label_hr.setStyleSheet("image: url(C:/python/image/hrProfile.png);")
            
    def opendirdialog(self):
        print("openfiledialog")
        fname = QtGui.QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\python\\testdata\\gpxx4\\files', QtGui.QFileDialog.ShowDirsOnly)
        if fname:
            self.lineEdit_file_saveto.setText(fname)
    
    def savefile(self):
        origfile = self.lineEdit_file_name.text()
        path = self.lineEdit_file_saveto.text()
        newname = self.lineEdit_file_newname.text()
        newfileloc = path+'\\'+newname
        print(newfileloc)
        
        if len(newname)>0 and len(path) > 0:
            try:
                gpx_file_formater.copyGPSFile(origfile,path,newname)
                training_analyzer.checkForNewFiles('C:\\python\\testdata\\gpxx4\\files\\*.*')
            except:
                print("Somthing went wrong saving the file")
        
    def onLoadFinished(self):
        with open("C:\\python\\testdata\\map.js", 'r') as f:
            frame = self.webView.page().mainFrame()
            frame.evaluateJavaScript(f.read())
            
    def onReadFileFinished(self):
        with open("C:\\python\\testdata\\map.js", 'r') as f:
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
        self.textEdit_2.setPlainText(training_analyzer.printSomething(df, filename))

if __name__ == '__main__':
    app = QtGui.QApplication([])
    win = MyMainWindow()
    win.show()
    app.exec_()