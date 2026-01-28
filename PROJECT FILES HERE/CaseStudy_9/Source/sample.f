**==sample.spg  processed by SPAG 4.52O  at 18:49 on  6 Jun 1996
 
      SUBROUTINE SAMPLE(I, En, Vir)
c     writes quantities to file
      IMPLICIT NONE
      INCLUDE 'parameter.inc'
      INCLUDE 'conf.inc'
      INCLUDE 'system.inc'
      INCLUDE 'potential.inc'
      INTEGER I
      DOUBLE PRECISION En, enp, Vir, press, CORP, vol, rho
      INTEGER NBIN
      PARAMETER (NBIN=100)
      INTEGER hist, nsamp_rhoz
      DIMENSION hist(NBIN)
      SAVE hist, nsamp_rhoz
      INTEGER init_rhoz
      SAVE init_rhoz
      DATA init_rhoz /0/

      INTEGER ip, ibin
      DOUBLE PRECISION dzbin
      INTEGER j
      DOUBLE PRECISION area, zc, rhoz



      IF (I.EQ.0) THEN
         DO 10 I=1,NBIN
            hist(I)=0
   10    CONTINUE
         nsamp_rhoz = 0
      END IF
c     --- one-time init for rho(z) ---
      IF (init_rhoz.EQ.0) THEN
         DO 11 j=1,NBIN
            hist(j)=0
   11    CONTINUE
         nsamp_rhoz = 0
         init_rhoz = 1
      END IF 
      IF (NPART.NE.0) THEN
         enp = En/DBLE(NPART)
         vol = BOX*BOX*LZ
         rho = NPART/vol
         press = rho/BETA + Vir/(3.D0*vol)
         IF (TAILCO) press = press + CORP(RC, rho)
      ELSE
         rho = 0.D0
         enp = 0.D0
         press = 0.D0
      END IF
c     --- rho(z) histogram accumulation ---
      dzbin = LZ/DBLE(NBIN)
      DO 20 ip=1,NPART
         ibin = 1 + INT( z(ip)/dzbin )
         IF (ibin.LT.1) ibin = 1
         IF (ibin.GT.NBIN) ibin = NBIN
         hist(ibin) = hist(ibin) + 1
   20 CONTINUE
      nsamp_rhoz = nsamp_rhoz + 1
      WRITE (66, *) I, SNGL(enp), SNGL(press), SNGL(rho)
c     --- write rho(z) profile (overwrite each call; last one is final) ---
      IF (nsamp_rhoz.GT.0) THEN
         area  = BOX*BOX
         dzbin = LZ/DBLE(NBIN)
         OPEN(99,FILE='rho_z.dat',STATUS='unknown')
         DO 30 j=1,NBIN
            zc   = (DBLE(j)-0.5D0)*dzbin
            rhoz = DBLE(hist(j)) / ( DBLE(nsamp_rhoz)*area*dzbin )
            WRITE(99,'(2E16.8)') zc, rhoz
   30    CONTINUE
         CLOSE(99)
      END IF

      RETURN
      END
