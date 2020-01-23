#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# Author : Moise Rousseau (2019), email at moise.rousseau@polymtl.ca


from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt




class PlotCanvas(FigureCanvas):
  def __init__(self, parent=None, width=5, height=4, dpi=100):
    self.fig = Figure(figsize=(width, height), dpi=dpi)
    self.axes = self.fig.add_subplot(111)
    self.axes.set_xlabel("Non orthogonality angle (°)")
    self.axes.set_ylabel("Number of volumes")
    self.axes.grid(True)
    plt.tight_layout()
    FigureCanvas.__init__(self, self.fig)
    #self.setParent(parent)

    FigureCanvas.setSizePolicy(self,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)
    FigureCanvas.updateGeometry(self)
    return
    

  def plotHist(self, data, bins, xlab='', ylab='', title='', xlim=None, ylim=None, grid=True):
    ax = self.axes
    ax.cla()
    # the histogram of the data
    #https://matplotlib.org/3.1.1/gallery/pyplots/pyplot_text.html#sphx-glr-gallery-pyplots-pyplot-text-py
    n, bins, patches = ax.hist(data, bins, density=False, facecolor='g', alpha=0.75)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title)
    #ax.relim()
    #ax.autoscale_view()
    if xlim: ax.set_xlim(xlim[0], xlim[1])
    if ylim: ax.set_ylim(ylim[0], ylim[1])
    ax.grid(grid)
    #self.fig.show()
    self.draw()
    return





class Ui_Dialog(object):

  def setupUi(self, Dialog):
    Dialog.setObjectName("Dialog")
    Dialog.resize(450, 720)
    Dialog.setSizeGripEnabled(True)
    
    #principal layout
    self.gridLayout_main = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_main.setObjectName("gridLayout_main")
    #QtWidgets.QWidget.setLayout(self.gridLayout_main)
    
    ### MESH SELECTION AND COMPUTE
    
    #mesh selection
    self.gridLayout_mesh = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_mesh.setObjectName("gridLayout_mesh")
    #mesh
    self.label_mesh = QtWidgets.QLabel(Dialog)
    self.label_mesh.setObjectName("label_mesh")
    self.pb_origMeshFile = QtWidgets.QPushButton(Dialog)
    self.pb_origMeshFile.setObjectName("origMeshFile")
    self.pb_origMeshFile.setCheckable(True)
    self.le_origMeshFile = QtWidgets.QLineEdit(Dialog)
    self.le_origMeshFile.setObjectName("le_origMeshFile")
    self.le_origMeshFile.setReadOnly(True)
    self.gridLayout_mesh.addWidget(self.label_mesh, 0, 0)
    self.gridLayout_mesh.addWidget(self.pb_origMeshFile, 0, 2)
    self.gridLayout_mesh.addWidget(self.le_origMeshFile, 0, 1)
    #add layout
    self.gridLayout_main.addLayout(self.gridLayout_mesh, 0, 0)
    
    #compute statistics
    self.gridLayout_compute = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_compute.setObjectName("gridLayout_compute")
    self.pb_compute = QtWidgets.QPushButton(Dialog)
    self.pb_compute.setObjectName("compute_stat")
    self.gridLayout_compute.addWidget(self.pb_compute, 0, 0)
    self.gridLayout_main.addLayout(self.gridLayout_compute, 1, 0)
    
    
    
    ### MPL PLOTS
    ## non orth
    self.gridLayout_plots = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_plots.setObjectName("gridLayout_plot_NO")
    self.label_plot_no = QtWidgets.QLabel(Dialog)
    self.label_plot_no.setObjectName("label_plot_no")
    self.plot_no = PlotCanvas(self, width=2, height=1)
    self.plot_no.setObjectName("plot_no")
    self.gridLayout_plots.addWidget(self.label_plot_no, 0, 0)
    self.gridLayout_plots.addWidget(self.plot_no, 1, 0)
    
    ## skew
    self.label_plot_skew = QtWidgets.QLabel(Dialog)
    self.label_plot_skew.setObjectName("label_plot_skew")
    self.plot_skew = PlotCanvas(self, width=2, height=1)
    self.plot_skew.setObjectName("plot_skew")
    self.gridLayout_plots.addWidget(self.label_plot_skew, 3, 0)
    self.gridLayout_plots.addWidget(self.plot_skew, 4, 0)
    self.gridLayout_main.addLayout(self.gridLayout_plots, 2, 0)
    
    
    ### GROUPS
    self.gridLayout_groups = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_groups.setObjectName("gridLayout_groups")
    #title
    self.label_groups = QtWidgets.QLabel(Dialog)
    self.label_groups.setObjectName("label_groups")
    self.gridLayout_groups.addWidget(self.label_groups, 0, 0)
    #label for no and skew
    self.label_group_no = QtWidgets.QLabel(Dialog)
    self.label_group_no.setObjectName("label_group_no")
    self.gridLayout_groups.addWidget(self.label_group_no, 1, 0)
    self.label_group_skew = QtWidgets.QLabel(Dialog)
    self.label_group_skew.setObjectName("label_group_no")
    self.gridLayout_groups.addWidget(self.label_group_skew, 2, 0)
    #linedit
    self.le_group_no = QtWidgets.QLineEdit(Dialog)
    self.le_group_no.setObjectName("le_group_no")
    self.gridLayout_groups.addWidget(self.le_group_no, 1, 1)
    self.le_group_skew = QtWidgets.QLineEdit(Dialog)
    self.le_group_skew.setObjectName("le_group_skew")
    self.gridLayout_groups.addWidget(self.le_group_skew, 2, 1)
    #push button
    self.pb_group_no = QtWidgets.QPushButton(Dialog)
    self.pb_group_no.setObjectName("pb_group_no")
    self.gridLayout_groups.addWidget(self.pb_group_no, 1, 2)
    self.pb_group_skew = QtWidgets.QPushButton(Dialog)
    self.pb_group_skew.setObjectName("pb_group_skew")
    self.gridLayout_groups.addWidget(self.pb_group_skew, 2, 2)
    #add layout
    self.gridLayout_main.addLayout(self.gridLayout_groups, 3, 0)
    
    
    #ok and cancel button
    self.splitter = QtWidgets.QSplitter(Dialog)
    self.splitter.setOrientation(QtCore.Qt.Horizontal)
    self.splitter.setObjectName("splitter")
    self.pb_okCancel = QtWidgets.QDialogButtonBox(self.splitter)
    self.pb_okCancel.setOrientation(QtCore.Qt.Horizontal)
    self.pb_okCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
    self.pb_okCancel.setObjectName("pb_okCancel")
    self.gridLayout_main.addWidget(self.splitter, 7, 0)
    self.pb_okCancel.rejected.connect(Dialog.reject)
    
    self.retranslateUi(Dialog)
    self.setDefaultValue()
    

  def retranslateUi(self, Dialog):
    _translate = QtCore.QCoreApplication.translate
    Dialog.setWindowTitle(_translate("Dialog", "Finite volume mesh quality"))
    ### MESH SELECTION AND COMPUTE
    self.pb_origMeshFile.setText(_translate("Dialog", "Select"))
    self.label_mesh.setText(_translate("Dialog", "Mesh:"))
    self.pb_compute.setText(_translate("Dialog", "Compute stats"))
    
    #plot
    self.label_plot_no.setText(_translate("Dialog", "Mesh non Orthogonality:"))
    self.label_plot_skew.setText(_translate("Dialog", "Mesh skewness:"))
    
    #group
    self.label_groups.setText(_translate("Dialog", "Generate groups"))
    self.label_group_no.setText(_translate("Dialog", "Create a group for non-orthonality angle > "))
    self.label_group_skew.setText(_translate("Dialog", "Create a group for skewness > "))
    self.pb_group_no.setText(_translate("Dialog", "Make group"))
    self.pb_group_skew.setText(_translate("Dialog", "Make group"))
  
  
  def setDefaultValue(self):
    pass


