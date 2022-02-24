# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HospitalFinder
                                 A QGIS plugin
 This plugins finds the best hospital for an emergency situation
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-01-02
        copyright            : (C) 2022 by Ufuk Bakan
        email                : println.ufukbakan@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load HospitalFinder class from file HospitalFinder.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .hospital_finder import HospitalFinder
    return HospitalFinder(iface)
