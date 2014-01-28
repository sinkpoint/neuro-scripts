import numpy

class NrrdReader:
    grdkey = 'DWMRI_gradient'
    b0num = 'b0num'      
        
    def getFileContent(self, filename):
        TFILE = open(filename, 'r')
        params = {self.grdkey:[], 
                  self.b0num:0}        
    
        while ( TFILE ):
            line = TFILE.readline()
            if len(line) == 0:
                break;
            line = line.strip()
            if line == '':
                continue
            
            if line.startswith('#'):
                continue
            
            if line.startswith('NRRD'):
                params['header'] = line
            else:
                key,val = line.split(':')
                key = key.strip()
                val = val.replace('=','').strip()
                
                if key == 'sizes':
                    val = self.getVals(val, 'int')                    
                elif key.startswith(self.grdkey):
                    val = self.getVals(val, 'float')
                else:
                    val = self.getVals(val, 'str')
                    
                if key.startswith(self.grdkey):
                    if val[0] == 0 and val[1] == 0 and val[2] == 0:
                        if params[self.b0num] < 1:
                            params[self.grdkey].append(val)
                        params[self.b0num] += 1
                    else:                                                   
                        params[self.grdkey].append(val)
                else:
                    params[key]= val
        TFILE.close()
        return params
    
    def asDtype(self, dtype, value):
        if dtype=='float':
            return float(value)
        elif dtype=='int':
            return int(value)
        else:
            return value 
    
    def getVals(self,input, dtype='str'):
        input = input.replace('(','')
        input = input.replace(')','')
        input = input.split(' ')
        res = []
        for i in input:
            if i == '':
                continue
            if i.find(',') > -1:
                i = i.split(',')
                for k in range(len(i)):
                    i[k] = self.asDtype(dtype, i[k])
                    res.append(i)
            else:
                i = self.asDtype(dtype, i)
                res.append(i)                
            
            
        if len(res) == 1:
            a = numpy.array(res)
            res = list(numpy.ravel(a))
        return res             