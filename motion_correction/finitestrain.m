Transforms = load('Transforms.txt')
dirs=load('dirs_62.dat')
fd = fopen('newdirs.dat','w');
if (size(dirs,1) > size(dirs,2) )
	dirs = dirs';
end

for (i=0:size(dirs,2)-1) 
  disp(i)
  F = Transforms((i*4+1):((i*4+1)+2),1:3); 
  disp(F);
  R = ((F*F')^(-0.5))*F;
  disp(R);
%  disp(dirs(1:3, i+1));
  dir = (real(R))*dirs(1:3, i+1);
%  disp(dir');
  fprintf(fd,'%f %f %f\n',dir);
  disp('---');
end
fclose(fd);
quit;
