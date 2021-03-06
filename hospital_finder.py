# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HospitalFinder
                                 A QGIS plugin
 This plugins finds the best hospital for an emergency situation
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-01-02
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Ufuk Bakan
        email                : println.ufukbakan@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.gui import QgsMapToolEmitPoint
from qgis.gui import *
from qgis.core import *
from qgis.PyQt.QtGui import *
import csv
import codecs
import collections

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .hospital_finder_dialog import HospitalFinderDialog
import os.path


class HospitalFinder:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.myLocation = None
        self.measurer = QgsDistanceArea()
        #self.measurer.setEllipsoidalMode(True)
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'HospitalFinder_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Hospital Finder')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
    
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('HospitalFinder', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/hospital_finder/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Hospital Finder'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Hospital Finder'),
                action)
            self.iface.removeToolBarIcon(action)

    def printArrLineByLine(self, arr):
        for elem in arr:
            print(elem)
    
    def dupplicateFilter(self):
        coordinates = list(map(self.getCoordinates,self.hospitals))
        for coordinate in coordinates:
            count = coordinates.count(coordinate)
            if(count > 1):
                print("DUPLICATE !!!!")
                print(coordinate)


    def getCoordinates(self, hospital):
        return [ hospital[2], hospital[3] ]


    def run(self):
        """Run method that performs all the real work"""
        # Fetch CSV Database :
        with codecs.open(os.path.join(self.plugin_dir,"hospitals.csv"), encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            self.hospitals = []
            for row in csv_reader:
                if line_count == 0:
                    print('Column names are ', row)
                    line_count += 1
                else:
                    row[2] = float(row[2])
                    row[3] = float(row[3])
                    self.hospitals.append(row)
                    #print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                    line_count += 1
            print(f'Processed {line_count} lines.')
            self.filteredHospitals = self.hospitals.copy()
            print("eg: \n" + str(self.hospitals[0]))
        
        QgsProject.instance().setTitle("Hospital Finder Project")
        self.dupplicateFilter()

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = HospitalFinderDialog()
        
        self.updatePossibleResultsLabel()
        #self.dlg.hideLocationMarkerButton.clicked.connect(self.hideLocationMarker)
        self.dlg.latitudeInput.textChanged.connect(self.coordinatesChanged)
        self.dlg.longitudeInput.textChanged.connect(self.coordinatesChanged)
        self.dlg.drawBaseMapButton.clicked.connect(self.drawBaseMap)
        self.dlg.zoomToAnkaraButton.clicked.connect(self.zoomToAnkara)
        self.dlg.showClosestHospitalButton.clicked.connect(self.findClosestHospital)

        canvas = self.iface.mapCanvas()
        self.pickPointTool = QgsMapToolEmitPoint(canvas)
        self.pickPointTool.canvasClicked.connect(self.setCoordinateInputs)
        self.dlg.markMyLocationButton.clicked.connect(self.switchToPickPointTool)
        self.dlg.typeFilter.currentIndexChanged.connect(self.typeFilterChanged)
        self.dlg.nameFilter.textChanged.connect(self.nameFilterChanged)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_() or True
        # See if OK was pressed
        if result:
            self.clearAllMarkers()

    def updatePossibleResultsLabel(self):
        self.dlg.possibleResultsLabel.setText(str(len(self.filteredHospitals)) + " possible results" )

    def applyFilters(self):
        self.filteredHospitals = list(filter(self.filterHospitalbyType, self.hospitals))
        self.filteredHospitals = list(filter(self.filterHospitalbyName, self.filteredHospitals))
        self.dlg.resultLabel.setText('')
        self.updatePossibleResultsLabel()
        self.drawHospitalMarkers()
    
    def typeFilterChanged(self, event):
        self.applyFilters()

    def nameFilterChanged(self, event):
        self.applyFilters()

    def filterHospitalbyName(self, hospital):
        if self.dlg.nameFilter.text().lower() in hospital[0].lower():
            return True
        else:
            return False
    

    def filterHospitalbyType(self, hospital):
        x = self.dlg.typeFilter.currentIndex()
        if x == 0:
            return True
        elif x == 1:
            if hospital[1]=="E??itim ve ara??t??rma hastanesi":
                return True
            else:
                return False
        elif x == 2:
            if hospital[1]=="Devlet hastanesi":
                return True
            else:
                return False
        elif x == 3:
            if hospital[1]=="A????z ve di?? sa??l?????? merkezi":
                return True
            else:
                return False
        elif x == 4:
            if hospital[1]=="??niversite hastanesi":
                return True
            else:
                return False
        elif x == 5:
            if hospital[1]=="??zel hastane":
                return True
            else:
                return False                    

    
    def hideLocationMarker(self, event):
        self.locationMarker.hide()

    def clearAllMarkers(self):
        vertex_items = [ i for i in self.iface.mapCanvas().scene().items() if issubclass(type(i), QgsVertexMarker)]
        for ver in vertex_items:
            if ver in self.iface.mapCanvas().scene().items():
                self.iface.mapCanvas().scene().removeItem(ver)

    #didnt work as expected so unused:
    def clearAllMarkersByType(self, QgsVertexMarkerIconType):
        vertex_items = [ i for i in self.iface.mapCanvas().scene().items() if issubclass(type(i), QgsVertexMarker)]
        for ver in vertex_items:
            if (ver in self.iface.mapCanvas().scene().items()):
                if(ver.IconType() == QgsVertexMarkerIconType):
                    self.iface.mapCanvas().scene().removeItem(ver)

    def clearAllMarkersByColor(self, QColor):
        vertex_items = [ i for i in self.iface.mapCanvas().scene().items() if issubclass(type(i), QgsVertexMarker)]
        for ver in vertex_items:
            if (ver in self.iface.mapCanvas().scene().items()):
                if(ver.color().rgb() == QColor.rgb()):
                    self.iface.mapCanvas().scene().removeItem(ver)
    
    def switchToPickPointTool(self, e):
        self.iface.mapCanvas().setMapTool( self.pickPointTool )

    def coordinatesChanged(self, e):
        try:
            self.myLocation = QgsPointXY(float(self.dlg.longitudeInput.text()), float(self.dlg.latitudeInput.text()))
            point = self.toCanvasCRS(self.myLocation)
            self.dlg.resultLabel.setText('')
            self.clearAllMarkersByColor(QColor(150,120,255))
            self.drawLocationMarker(point.x(), point.y())
        except:
            self.myLocation = None
            self.dlg.resultLabel.setText('<span style=" color:#ff0000;">Please enter or mark your location</span>')
            self.clearAllMarkersByColor(QColor(150,120,255))
            pass

    def drawLocationMarker(self, x, y):
        locationMarker = QgsVertexMarker(self.iface.mapCanvas())
        locationMarker.setCenter(QgsPointXY(x,y))
        locationMarker.setColor(QColor(150,120,255)) #(R,G,B)
        locationMarker.setIconSize(20)
        locationMarker.setIconType(QgsVertexMarker.ICON_X)
        locationMarker.setPenWidth(6)
        locationMarker.show()

    def drawHospitalMarkers(self):
        self.clearAllMarkersByColor(QColor(255,100,50))
        if(self.myLocation != None):
            self.clearAllMarkersByColor(QColor(150,120,255))
        for hospital in self.filteredHospitals:
            marker = QgsVertexMarker(self.iface.mapCanvas())
            marker.setCenter(self.toCanvasCRS(QgsPointXY(hospital[3],hospital[2]))) #longitude, latitude to canvas point
            marker.setColor(QColor(255,100,50)) #(R,G,B)
            marker.setIconSize(20)
            marker.setIconType(QgsVertexMarker.ICON_BOX)
            marker.setPenWidth(6)
            marker.show()
        if(self.myLocation != None):
            myPoint = self.toCanvasCRS(self.myLocation)
            self.drawLocationMarker(myPoint.x(), myPoint.y())

    def findClosestHospital(self, event):
        if(self.myLocation == None):
            self.dlg.resultLabel.setText('<span style=" color:#ff0000;">Please enter or mark your location</span>')
        elif len(self.filteredHospitals)>0:
            qgsHospitalPoints = list(map(self.getQgsPoints, self.filteredHospitals))
            distancesArray = list(map(lambda hp: self.calculateDistance(hp, self.myLocation), qgsHospitalPoints))
            closestHospitalIndex = distancesArray.index(min(distancesArray))
            closestHospital = self.filteredHospitals[closestHospitalIndex]
            self.dlg.resultLabel.setText('<span style=" color:#5544ff;">'+closestHospital[0]+'/'+ closestHospital[1]+ '<br/>' + 'Latitude, Longitude:'+ str(closestHospital[2]) + ', '+ str(closestHospital[3]) +'</span>')
        else:
            self.dlg.resultLabel.setText('<span style=" color:#ff0000;">There is no hospital suitable with your filters</span>')
        
    
    def getQgsPoints(self, hospital):
        return QgsPointXY(hospital[3],hospital[2]) #x=longitude, y=latitude


    def calculateDistance(self, QgsP1, QgsP2):
        return self.measurer.measureLine(QgsP1, QgsP2)
    
    def toWGS84(self, pointXY):
        source_crs = self.iface.mapCanvas().mapSettings().destinationCrs()
        wgs84_crs = QgsCoordinateReferenceSystem(4326)
        transformer = QgsCoordinateTransform(source_crs, wgs84_crs, QgsProject.instance())
        return transformer.transform(pointXY)

    def toCanvasCRS(self, pointXY):
        source_crs = self.iface.mapCanvas().mapSettings().destinationCrs()
        wgs84_crs = QgsCoordinateReferenceSystem(4326)
        transformer = QgsCoordinateTransform(wgs84_crs, source_crs, QgsProject.instance())
        return transformer.transform(pointXY)

    def setCoordinateInputs(self, point, mouseButton):
        point = self.toWGS84(point)
        self.dlg.longitudeInput.setText(str(point.x()))
        self.dlg.latitudeInput.setText(str(point.y()))

    def drawBaseMap(self, e):
        tms = 'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0'
        openStreetLayer = QgsRasterLayer(tms,"Open Street Map", "wms")
        QgsProject.instance().addMapLayer(openStreetLayer)
        #changing mapcanvas crs to wgs84 makes map look weird instead im gona use transforms
        #QgsProject.instance().setCrs(QgsCoordinateReferenceSystem(4326))
        #iface.mapCanvas().mapSettings().setDestinationCrs(QgsCoordinateReferenceSystem(4326))
        self.drawHospitalMarkers()
    
    def zoomToPoint(self, x, y, zoom):
        rect = QgsRectangle(x-zoom,y-zoom,x+zoom,y+zoom)
        canvas = self.iface.mapCanvas()
        canvas.setExtent(rect)
        canvas.refresh()
        
    def zoomToAnkara(self, e):
        #3657288.43,4854439.67
        #scale:3000
        self.zoomToPoint(3657288.43,4854439.67, 400)