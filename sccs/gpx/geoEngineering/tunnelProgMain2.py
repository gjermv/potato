# -*- coding: utf-8 -*-

import sys
sys.path.append('C:\\Users\\A485753\\eclipse-workspace\\Projectplace\\')

from PyQt5 import QtGui
from PyQt5 import QtCore, QtGui,QtWidgets

import feltskjemaAnalyzer

from tunnelProgGUI2 import Ui_MainWindow
import feltskjemaAnalyzer as fAnalyzer
import TunnelCreatorV2 as tunnelCreatorV2
import Bilag3_generator as bilag3



class MyMainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        

        self.pushButton.clicked.connect(self.openfiledialogExcel)
        self.pB_createDXF.clicked.connect(self.createDXF)
        
        self.pB_bilag3_excel.clicked.connect(self.openfiledialogExcel_bilag3)
        self.pB_bilag3_image.clicked.connect(self.openfiledialog_SelectImageFolder)
        
        self.pB_bilag3_export.clicked.connect(self.createBilag3)

    def openfiledialogExcel(self):
        self.fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Read file', 'C:\\python_proj\\tunnelinspek\\import_filer',
            filter=('Excel file (*.xlsx)'))[0]
            
       
        if self.fname:
            self.lE_excelInput.setText(self.fname)

    def openfiledialog(self):
        self.fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Read file', 'C:\\',
            filter=('DXF file (*.dxf)'))[0]
            
        if self.fname:
            self.lE_tunnelnavn_4.setText(self.fname)

    def openfiledialogExcel_bilag3(self):
        self.fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Read file', 'C:\\',
            filter=('Excel file (*.xlsx)'))[0]
            
        if self.fname:
            self.lE_excelInput_2.setText(self.fname)
    
    def openfiledialog_SelectImageFolder(self):
        self.fname = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
            
       
        if self.fname:
            self.lE_imagefolder_3.setText(self.fname)
 
    def analyzeFile(self):
        fname = self.lE_tunnelnavn_4.text()
        if len(fname)>0:
            print(fname)
            fAnalyzer.analyseDXF(fname, "Markering_ny", 200)
        else:
            print('No file')
    
    def createDXF(self):
        
        self.tunnelName =   self.lE_tunnelName.text()
        
        try:
            self.profile_from = int(self.lE_profile_from.text())
            self.profile_to = int(self.lE_profile_to.text())
        except:
            self.textBrowser.setText("ERROR: From / To must be a number")
            return -1
            
        self.fromDir = self.lE_fromDir.text()
        self.toDir= self.lE_toDir.text()
        self.xlsx_file = self.lE_excelInput.text()
        

        if self.radioButton1.isChecked():
            tunnelCreatorV2.tunnelCreator_Run( self.tunnelName, int(self.profile_from), self.profile_to, self.toDir, self.fromDir, self.xlsx_file, 1 )
        else: 
            tunnelCreatorV2.tunnelCreator_Run( self.tunnelName, int(self.profile_from), self.profile_to, self.toDir, self.fromDir, self.xlsx_file, 2 )
               
            
        self.textBrowser.setText("File saved as C:\\python_proj\\tunnelinspek\\{}.dxf".format(self.tunnelName))
        return 1

    def createBilag3(self):
        tunnel_name = self.lE_tunnelName_2.text()
        excel_fil = self.lE_excelInput_2.text()
        image_folder = self.lE_imagefolder_3.text()        
        
        bilag3.create_bilag3(tunnel_name, excel_fil, image_folder)
        
        self.textBrowser.setText("File saved as C:\\python_proj\\Bilag3\\Bilag 3 - {}.docx".format(tunnel_name))

    def createBilag1(self):
        print('Create Bilag 1 / Not implemented!!')

       
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = MyMainWindow()
    win.show()
    app.exec_()