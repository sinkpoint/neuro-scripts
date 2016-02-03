import vtk
import numpy as np
import os
def vtkToStreamlines(filename):

    ext = 'vtk'
    basetoks = os.path.basename(filename).split('.')
    if len(basetoks) > 1:
        ext = basetoks[1]

    vreader = vtk.vtkPolyDataReader()
    if ext == 'vtp':
        vreader = vtk.vtkXMLPolyDataReader()

    vreader.SetFileName(filename)
    vreader.Update()
    inputPolyData = vreader.GetOutput()

    streamlines = []
    for i in range(inputPolyData.GetNumberOfCells()):
        pts = inputPolyData.GetCell(i).GetPoints()
        npts = np.array([pts.GetPoint(i) for i in range(pts.GetNumberOfPoints())])
        streamlines.append(npts)
    return streamlines, inputPolyData