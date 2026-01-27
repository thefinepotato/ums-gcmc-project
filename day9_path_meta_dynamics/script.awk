BEGIN{
  N=100;
  T = 300.;
  x0=-3.0;
  xe=2.0;
  y0=-1.5;
  ye=3.5;
  dx=(xe-x0)/(N-1);
  dy=(ye-y0)/(N-1);
# print header
  print "# ",N,N
#  print "#! FIELDS d1.x d1.y external.bias "
#  print "#! SET min_d1.x ",x0
#  print "#! SET max_d1.x ",xe
#  print "#! SET nbins_d1.x ",N
#  print "#! SET periodic_d1.x false"
#  print "#! SET min_d1.y ",y0
#  print "#! SET max_d1.y ",ye
#  print "#! SET nbins_d1.y ",N
#  print "#! SET periodic_d1.y false"
#
# ------------------------
  k = 0;
  AA[k] = -200.0;
  a[k] = -1.0;
  b[k] = 0.0;
  c[k] = -10.0;
  xt[k] = 1.0;
  yt[k] = 0.0;
  k = 1;
  AA[k] = -100.0;
  a[k] = -1.0;
  b[k] = 0.0;
  c[k] = -10.0;
  xt[k] = 0.0;
  yt[k] = 0.5;
  k = 2;
  AA[k] = -170.0;
  a[k] = -6.5;
  b[k] = 11.0;
  c[k] = -6.5;
  xt[k] = -0.5;
  yt[k] = 1.5;
  k = 3;
  AA[k] = 15.0;
  a[k] = 0.7;
  b[k] = 0.6;
  c[k] = 0.7;
  xt[k] = -1.0;
  yt[k] = 1.0;
  MAXF = 600;
# ------------------------
  k = 0;
  for(i=0;i<N;i++){
    for(j=0;j<N;j++){
      x=x0+i*dx;
      y=y0+j*dy;
      f = 0.0;
      for(k=0;k<4;k++){
        f += AA[k] * exp( a[k]*(x-xt[k])**2 + b[k]*(x-xt[k])*(y-yt[k]) + c[k]*(y-yt[k])**2 );
      }
      if( f > MAXF ) f = MAXF;
      printf(" %12.6f %12.6f %12.6f\n",x,y,f);
    }
    print " ";
  }
}
