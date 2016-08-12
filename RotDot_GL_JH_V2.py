# JH@KrappLab 
# 2016-08-10: [V1] Rotating Dot
# 2016-08-12: [V2] Sync
#

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

ang=0
prev_ang = 0
angv = 360 # deg/s

stim_flag = 0
stamped=0
us_stamp=0

radorb=0.5
raddot=0.3

current_us_time = lambda: int(floor(time.time() * 1000000 ))

############################################

def init_daq():
	global daq, DEBUG
	if DEBUG == 0:
		daq = JH_DAQ_Thread(Duration=8, memo='[az0][el0]',log=1)


def display(*args):
	#global t,ang, prev_sec ,stim_time,anglist, prev_ms
	global stim_flag,stamped
	global ang, prev_ang , angv
	global us_stamp
	global raddot,radorb

	glClearColor(0.5, 0.5, 0.5, 0.0)	
	glClear(GL_COLOR_BUFFER_BIT)

	if stim_flag == 1:
		if stamped == 0:
			us_stamp = current_us_time()
			stamped = 1

		us_tick = current_us_time() - us_stamp
		ms_tick = us_tick//1000


		# sync
		if ms_tick%1000 <= 30:
			glClearColor(1.0, 1.0, 1.0, 0.0)
			glClear(GL_COLOR_BUFFER_BIT)

		else:
			glClearColor(0.0, 0.0, 0.0, 0.0)
			glClear(GL_COLOR_BUFFER_BIT)

			glColor3f(1.0, 1.0, 1.0)
			glBegin(GL_POLYGON)
			for i in range(360):
				glVertex3f(cos(i*pi/180.0), sin(i*pi/180.0), 0.0)
			glEnd()  		


		# stim
		ang = (us_tick//1000) *(angv/1000.0)
		glRotatef(-prev_ang, 0.0, 0.0 ,1.0)
		glRotatef(ang, 0.0, 0.0 ,1.0)
		glColor3f(0.0, 0.0, 0.0)
		
		glBegin(GL_POLYGON)	# Start drawing a circle
		for i in range(360):
			glVertex3f(cos(i*pi/180.0)*raddot+radorb, sin(i*pi/180.0)*raddot, 0.0)
		glEnd()  

		prev_ang=ang

		prev_ms=us_tick//1000  # 1 ms

		
		if ms_tick//1000 >= 3:
			stim_flag=0
			#daq = JH_DAQ_Thread(Duration=8, memo='[az0][el0]',log=1)
			init_daq()
		
	else:
		glClearColor(0.5, 0.5, 0.5, 0.0)
		glClear(GL_COLOR_BUFFER_BIT)
		#t=0
		#ang=anglist[0] #float(45)
		#prev_sec=-1 
		stamped=0
		#glRotatef( -prev_ang, 0.0, 0.0 ,1.0)
		#prev_ang=0



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
	#print "Hit 's' key to record. Hit other key to quit."
	print "Hit any key to quit."
	#daq = JH_DAQ_Thread(Duration=8, memo='[az0][el0]',log=1)

	init_daq()
	main()
