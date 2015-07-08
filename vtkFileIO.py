import vtk
import numpy as np

def vtkToStreamlines(filename):
    vreader = vtk.vtkPolyDataReader()
    vreader.SetFileName(filename)
    vreader.Update()
    inputPolyData = vreader.GetOutput()

    streamlines = []
    for i in range(inputPolyData.GetNumberOfCells()):
        pts = inputPolyData.GetCell(i).GetPoints()
        npts = np.array([pts.GetPoint(i) for i in range(pts.GetNumberOfPoints())])
        streamlines.append(npts)
    return streamlines, inputPolyData