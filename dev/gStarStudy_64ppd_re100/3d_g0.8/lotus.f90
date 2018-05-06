!-------------------------------------------------------!
!------------------- Cylinder Array --------------------!
!-------------------------------------------------------!
!  Lotus reference file for the 3d high res simulations
! without any twist.
!  The aim is to validate the phenomenon seen on similar
! 2d simulations.
!
! Re = 100
! g_star = range of values
! twist_pitch = infinite
!
! Grid size:
!   x: [-5DG,15DG]
!   y: [-5DG,5DG]
!   z: [-10DG,10DG]
!-------------------------------------------------------!
!  NOTE: Bernat needs to modify the number of blocks to
! match with the number of cores in Iridis (line 57).
!-------------------------------------------------------!
program array
  use fluidMod,   only: fluid
  use bodyMod,    only: body
  use mympiMod!,   only: init_mympi,mympi_end,mympi_rank
  use gridMod,    only: xg,composite
  use imageMod,   only: display
  use geom_shape!, only: cylinder,operator(.and.),pi
  implicit none
!
! -- physical parameters
  integer,parameter :: rows   = 1     ! number of rows (not include center)
  real,parameter    :: g_star = 0.8 ! nondimensional spacing
  real,parameter    :: aoa    = 0     ! angle of attack
  real,parameter    :: Re_D   = 100   ! Reynolds number based on diameter
!
! -- numerical parameters
  real,parameter  :: D      = 64       ! resolution (pnts per diameter)
  real,parameter  :: finish = 500*D ! finish time
  integer         :: n(3)              ! number of points
  integer         :: npx = 16
  integer         :: npy = 8
  integer         :: npz = 4
!
! -- derived values (don't touch)
  real,parameter :: nu = D/Re_D                     ! nondim viscosity
  real,parameter :: DG = (2.*rows*(1.+g_star)+1.)*D ! group diameter
!
! -- grid parameters
  real,parameter :: nPnts_3d(3) = D*(/20,10,5/) ! number of points. note (/20,10,6/) for full size domain
  real,parameter :: nPnts_2d(3) = D*(/20,10,0/) !
  real,parameter    :: height_z = 4.            ! height of cells in z
  integer,parameter :: noDims = 3        ! no. of dims of the simulation
!
! -- twist parameters
  ! logical,parameter :: twist_indicator = .false.    ! to twist or not to twist
  ! integer,parameter :: twist_axis      = 3          ! z axis
  ! real(8),parameter :: twist_pitch     = TWISTPITCH ! equal to 6 times the depth of domain (20DG)
!
! -- MPI utils
  integer :: b(3)             ! blocks (to be modified by Bernat)
  integer :: m(3)             ! number of points per block
  logical :: root             ! root processor
  logical :: kill = .false.   ! exits the time loop
!
! -- data utils
  real,parameter :: dtPrint    = 50*D  ! print rate
  real,parameter :: dtDisplay  = 5*D   ! vorticity display rate
  real,parameter :: dtWriteVTK = 500*D ! VTK writing rate
!
! -- simulation variables
  type(fluid) :: flow                     ! fluid object
  type(body)  :: bodies                   ! body object
  real :: dt, t1, pforce(3), vforce(3), U !
!
! -- initialize MPI (if MPI is OFF, b is set to 1)
  b = (/npx,npy,npz/)
  if (noDims == 2) then
    call init_mympi(noDims,set_blocks=b)
  else if (noDims == 3) then
    call init_mympi(noDims,set_blocks=b,set_periodic=(/.false.,.false.,.true./))
  end if
  root = mympi_rank()==0
! -- Print MPI info
  if (root) print *, 'Blocks: ',b
!
! -- Initialize grid (might need to adjust these parameters later)
  if (noDims == 2) then
    n = composite(nPnts_2d, prnt=root)
  end if
  if (noDims == 3) then
    n = composite(nPnts_3d, prnt=root)
    xg(3)%h = height_z
  end if
!
  call xg(1)%stretch(n(1), -5*DG, -0.6*DG, 0.6*DG, 15*DG, h_max=15., prnt=root)
  call xg(2)%stretch(n(2), -5*DG, -0.6*DG, 0.6*DG, 5*DG, prnt=root)
!
! -- Initialize cylinder array
  ! bodies = make_array(aoa).map.init_twist(twist_axis,twist_pitch)
  ! if (root) print *, 'Twist of the array:',twist_pitch/DG,'DG'
  bodies = make_array(aoa)
!
! -- Initialize fluid
  m = n/b ! number of points per block!!
  call flow%init(m, bodies, V=(/1.,0.,0./), nu=nu)
  if(root) print *, '-- init complete --'

  call gatherRead2D(flow%velocity,n,b)
  call flow%write()
!
! -- Time update loop
  time_loop: do while (flow%time<finish)
     dt = flow%dt       ! time step
     t1 = flow%time+dt  ! time at the end of this step
     call flow%update() ! update N-S
!
! -- measure and write to file force coefficients
     pforce = -2.*bodies%pforce(flow%pressure)/(D * n(3)*xg(3)%h)
     vforce = 2.*nu*bodies%vforce(flow%velocity)/(D * n(3)*xg(3)%h)
     if(root) write(9,'(f10.4,f8.4,6e16.8)') t1/D,dt,pforce,vforce
     if(root) flush(9)
!
! -- print time left
     if(mod(t1,dtPrint)<dt) then
       if(root) print "('Time:',f8.3,'. Time remaining:',f8.3)", t1/D,finish/D-t1/D
     end if
 !
 ! -- display vorticity image
      ! if(mod(t1,dtDisplay)<dt) then
      !   call display(flow%velocity%vorticity_z(),'vorticity', box = int((/-DG,-DG,6*DG,2*DG/)))!,lim=4./DG)
      ! end if
!
! -- write VTK image
     ! if(mod(t1,dtWriteVTK)<dt) then
     !   call flow%write()
     ! end if
!
! -- check if .kill, end the time_loop
     inquire(file=".kill", exist=kill)
     if (kill) exit time_loop
!
  end do time_loop
  call flow%write()


  call mympi_end()
contains
!
! -- make an array of cylinders with group diameter DG
  type(set) function make_array(aoa)
    real,intent(in) :: aoa
    integer,parameter :: n(4) = (/6,13,19,25/)
    real,parameter    :: R = 0.5*DG-0.5*D
    real    :: theta,xc,yc
    integer :: i,j
    make_array = place_cyl(0.,0.)
    do j=1,rows
       do i=1,n(j)
          theta = 2.*pi*(i-1.)/real(n(j))+aoa
          xc = R*sin(theta)*real(j)/rows
          yc = R*cos(theta)*real(j)/rows
          make_array = make_array.or.place_cyl(xc,yc)
       end do
    end do
  end function make_array
  type(cylinder) function place_cyl(xc,yc)
    real,intent(in) :: xc,yc
    place_cyl = cylinder(axis=3,radius=0.5*D,center=(/xc,yc,0./))
  end function place_cyl

  subroutine gatherRead2D(u,n,b)
  	use fieldMod, only: field
  	use vectorMod, only: vfield
  	use mympiMod
  	type(vfield),intent(inout) :: u
  	integer,intent(in)			:: n(3),b(3)
  	integer :: is,ie,js,je,ks,ke,mx,my,mz
  	integer :: i,j,k,m(3),p,nproc,my_rank,index, skip_blocs, skipx1, skipx2
  	logical :: root
  	real :: pos(3), dum1, dum2
  	character(len=100)	:: file,dir,s1,s2
  	character(len=16) 	:: m_char
  	type(vfield)				:: v

  	m = n/b

  	call u%e(1)%limits(is,ie,js,je,ks,ke)
  	root = mympi_rank()==0
  	nproc = product(b)
  	my_rank = mympi_rank()
  	
	file = '/scratch/bfg1g15/Lotus/projects/cylinder/Carlos/2d_g0.8/gather_output_2D.dat'

  	open(my_rank, file = file, status = 'old', action = 'read', form = 'unformatted', access='stream')
			mx = int(my_rank/(b(3)*b(2)))
			my = mod(int(my_rank/b(3)),b(2))

			skip_blocs = my*m(2)*n(1) ! Skipe entire row of blocks
      !write(*,*) 'skip_blocs',my_rank, skip_blocs, my, m(2), n(1)
			do k = 1, skip_blocs
				read(my_rank) dum1, dum2
			end do

      skipx1 = mx*m(1)
     ! write(*,*) 'skipx1',my_rank, skipx1, mx, m(1)
      skipx2 = (b(1)-mx-1)*m(1)
     ! write(*,*) 'skipx2',my_rank, skipx2, b(1), mx, m(1)

			do j = js,je
				do k = 1, skipx1
					read(my_rank) dum1, dum2
				end do

				do i = is,ie
					read(my_rank) u%e(1)%p(i, j, 1), u%e(2)%p(i, j, 1)
				end do

				do k = 1, skipx2
					read(my_rank) dum1, dum2
				end do
		  end do
  	close(my_rank)

    call u%e(1)%spread()
    call u%e(2)%spread()
    call u%e(3)%perturb(0.02,zero_ave=.true.)

  end subroutine gatherRead2D
end program array
