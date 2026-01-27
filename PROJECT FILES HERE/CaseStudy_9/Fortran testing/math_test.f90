program math_test
    implicit none
    real :: radius, area
    real, parameter :: PI = 3.14159265

    print *, 'Enter the radius of a circle:'
    read *, radius

    area = PI * radius**2

    print *, 'The area is:', area
end program math_test