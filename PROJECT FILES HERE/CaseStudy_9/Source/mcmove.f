**==mcmove.spg  processed by SPAG 4.52O  at 18:49 on  6 Jun 1996
      SUBROUTINE MCMOVE(En, Vir, Attempt, Nacc, Dr, Iseed)
c
c     attempts to displace a randomly selected particle
c     modified script --> add wall before energy calculation and remove z-wrapping
      IMPLICIT NONE
      INCLUDE 'parameter.inc'
      INCLUDE 'conf.inc'
      INCLUDE 'system.inc'
      DOUBLE PRECISION enn, eno, En, RANF, xn, yn, zn, viro, virn, Vir, 
     &                 Dr
      INTEGER o, Attempt, Nacc, jb, Iseed
 
      Attempt = Attempt + 1
      jb = 1
c     ---select a particle at random
      o = INT(NPART*RANF(Iseed)) + 1
c     ---calculate energy old configuration
      CALL ENERI(X(o), Y(o), Z(o), o, jb, eno, viro)
c     ---give particle a random displacement
      xn = X(o) + (RANF(Iseed)-0.5D0)*Dr
      yn = Y(o) + (RANF(Iseed)-0.5D0)*Dr
      zn = Z(o) + (RANF(Iseed)-0.5D0)*Dr

c     --slit pore check for wall potential 
c     --if z outside of the range 0:slitwidth then U_wall = infinte, reject
      IF (zn.LT.0.D0) .OR. zn.GT.SLITWIDTH RETURN
c     ---calculate energy new configuration:
      CALL ENERI(xn, yn, zn, o, jb, enn, virn)
c     ---acceptance test
      IF (RANF(Iseed).LT.EXP(-BETA*(enn-eno))) THEN
c        --accepted
         Nacc = Nacc + 1
         En = En + (enn-eno)
         Vir = Vir + (virn-viro)
c        ---put particle in simulation box OUTDATED
c         IF (xn.LT.0) xn = xn + BOX
c         IF (xn.GT.BOX) xn = xn - BOX
c         IF (yn.LT.0) yn = yn + BOX
c         IF (yn.GT.BOX) yn = yn - BOX
c         IF (zn.LT.0) zn = zn + BOX
c         IF (zn.GT.BOX) zn = zn - BOX
c         X(o) = xn
c         Y(o) = yn
c         Z(o) = zn
c        ---put particle in simulation box with PBC in only X AND Y but Z is a real wall
          IF (xn.LT.0) xn = xn + BOX
          IF (xn.GT.BOX) xn = xn - BOX
          IF (yn.LT.0)  yn = yn + BOX
          IF (yn.GT.BOX) yn = yn - BOX
c        ---now for z: NO PBC, walls are real boundaries
          X(o) = xn
          Y(o) = yn
          Z(o) = zn
      END IF
      RETURN
      END
