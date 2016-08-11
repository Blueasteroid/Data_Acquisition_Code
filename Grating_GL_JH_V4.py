# JH@KrappLab 
# 2016-08-03 [V1] grating stim implemneted
# 2016-08-05 [V2] fixed a timing bug and raised priority in win32
# 2016-08-07 [V3] pseudo-random stim sequence
# 2016-08-11 [V4] using us accuracy

from numpy import *
from numpy.random import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time, sys

DEBUG = 1

if DEBUG==0:
	from JH_DAQ_Thread import *

############################################

halted=0

t=0
prev_ang = 0
prev_sec=-1 
stim_flag = 0
stim_time = 0
us_stamp=0
stamped=0

anglist=[90,180,270,0,45,135,225,315]
ang=anglist[0]
#print "debug",ang

#current_milli_time = lambda: int(floor(time.time() * 1000))
current_us_time = lambda: int(floor(time.time() * 1000000 ))

############################################

def init_daq():
	global daq, DEBUG
	if DEBUG == 0:
		daq = JH_DAQ_Thread(Duration=8, memo='[az0][el0]',log=1)


def display(*args):
	global t, prev_ang,ang, prev_sec, stim_flag,stim_time,stamped,anglist
	global us_stamp

	glClearColor(0.5, 0.5, 0.5, 0.0)	
	glClear(GL_COLOR_BUFFER_BIT)

	h=float(2)	# pattern height
	w=float(1)	# pattern width
	#spatial_freq = 2
	#w=float(2/spatial_freq)

	if stim_flag == 1:
		if stamped == 0:
#			stim_time = current_milli_time()
			#ms_tick = int(floor(time.time() * 1000))
			us_stamp = current_us_time()
			stamped = 1

		#ms_tick=current_milli_time()-stim_time
		us_tick = current_us_time() - us_stamp
		ms_tick = us_tick//1000


		if ms_tick//1000 == prev_sec+1 and ms_tick//1000 <=7:
			print 'Sec:',ms_tick//1000,', Angle:', ang	#...debug

			glRotatef( -prev_ang, 0.0, 0.0 ,1.0)
			glRotatef( ang, 0.0, 0.0 ,1.0)
			prev_ang=ang
			#ang = (ang+45)%360
			ang=anglist[((ms_tick//1000+1)%len(anglist))]

			prev_sec = ms_tick//1000


		if ms_tick%1000 <= 250 or ms_tick%1000 >= 750 :	# 1 sec
			glClearColor(0.0, 0.0, 0.0, 0.0)
			glClear(GL_COLOR_BUFFER_BIT)
			
			glColor3f(0.5, 0.5, 0.5)           	
			glBegin(GL_QUADS)                  
			glVertex3f(-1.5, 1.5, 0.0)      
			glVertex3f(1.5, 1.5, 0.0)          
			glVertex3f(1.5, -1.5, 0.0)         
			glVertex3f(-1.5, -1.5, 0.0)         
			glEnd() 
			
		else:
			glClearColor(1.0, 1.0, 1.0, 0.0)
			glClear(GL_COLOR_BUFFER_BIT)
		
			if ms_tick%1 == 0:		# 1 ms
				t=(t+0.001)%w
				#t=us_tick%w
				glColor3f(0.0, 0.0, 0.0)           	

				for i in range(50):
					glBegin(GL_QUADS)                   # Start drawing a 4 sided polygon
					glVertex3f(t-2+w*i, h, 0.0)         
					glVertex3f(t-2+w*i-w/2, h, 0.0)           
					glVertex3f(t-2+w*i-w/2, -h, 0.0)          
					glVertex3f(t-2+w*i, -h, 0.0)         
					glEnd()  

		if ms_tick//1000 >7:
			stim_flag=0
			#daq = JH_DAQ_Thread(Duration=8, memo='[az0][el0]',log=1)
			init_daq()

	else:
		t=0
		ang=anglist[0] #float(45)
		prev_sec=-1 
		stamped=0
		glRotatef( -prev_ang, 0.0, 0.0 ,1.0)
		prev_ang=0



	glFlush()
	glutSwapBuffers()


def halt():
	pass

def keyboard(*args):
	global stim_flag, daq
	global halted
	if (args[0]=='s') :
		stim_flag=1
		if DEBUG==0:
			daq.start() # <<<<< DAQ trigger
	elif (args[0]=='p') :
		if halted:
			glutIdleFunc(display)
			halted = 0
		else:
			glutIdleFunc(halt)
			halted = 1
	else:
		sys.exit()

def mouse(button, state, x, y):
	pass
	
def setup_viewport():
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)

def reshape(w, h):
	#glViewport(0, 0, w, h)
	pattern_size = 800
	glViewport((w-pattern_size)/2, (h-pattern_size)/2, pattern_size, pattern_size)
	setup_viewport()

def main():
	glutInit(sys.argv)
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
	glutInitWindowSize(800, 800)
	glutCreateWindow('JH_GL_Grating')
	setup_viewport()
	glutReshapeFunc(reshape)
	glutDisplayFunc(display)
	glutIdleFunc(display)
	glutMouseFunc(mouse)
	glutKeyboardFunc(keyboard)
	glutMainLoop()

def setpriority(pid=None,priority=1):
    """ Set The Priority of a Windows Process.  Priority is a value between 0-5 where
        2 is normal priority.  Default sets the priority of the current
        python process but can take any valid process ID. """
        
    import win32api,win32process,win32con
    
    priorityclasses = [win32process.IDLE_PRIORITY_CLASS,
                       win32process.BELOW_NORMAL_PRIORITY_CLASS,
                       win32process.NORMAL_PRIORITY_CLASS,
                       win32process.ABOVE_NORMAL_PRIORITY_CLASS,
                       win32process.HIGH_PRIORITY_CLASS,
                       win32process.REALTIME_PRIORITY_CLASS]
    if pid == None:
        pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, priorityclasses[priority])

############################################

if __name__ == "__main__":
	setpriority()
	print "Hit 's' key to record. Hit other key to quit."
	#print "Hit any key to quit."
	#daq = JH_DAQ_Thread(Duration=8, memo='[az0][el0]',log=1)

	init_daq()
	main()
