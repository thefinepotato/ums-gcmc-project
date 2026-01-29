c   system.inc
      double precision box,temp,beta,hbox,slitwidth
      common/sys1/box,hbox,temp,beta,slitwidth
c
c     box      : simulation box length
c     hbox     : 0.5 * box
c     temp     : temperature
c     beta     : 1/temp
c     figured this out, but c is just comment in fortran
c     SO this file is more or less setting up global variables for simulation
c     double precision, its just 64 bit floating numbers
c     common syntax is just creating global memory
c     will add slit width variable as we need that for the project
c     slitwidth: the distance between walls in z as per project A.1   
