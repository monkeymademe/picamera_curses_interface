import io
import picamera
import curses
from time import sleep

class MyOutput(object):
    def __init__(self):
        self.file_num = 0
        self.write_frame = False
        self.output = None
        self.lapse = False
        self.interval = 3

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            if self.output:
                self.output.close()
            self.output = None
            if self.write_frame:
                self.file_num += 1
                self.output = io.open('%d.jpg' % self.file_num, 'wb')
                if self.lapse == True:
                    sleep(self.interval)
                    self.write_frame = True
                else:
                    self.write_frame = False
        if self.output:
            self.output.write(buf)

def main(window):
    window.nodelay(True)
    with picamera.PiCamera(resolution=(1280, 720), framerate=15) as camera:
        output = MyOutput()
        camera.start_recording(output, format='mjpeg')
        try:
            while True:
                window.addstr(0, 0, 'Press Q to quit')
                window.addstr(2, 0, 'Press F to capture a single frame')
                window.addstr(3, 0, 'Press 3 to start 3s timeplase')
                window.addstr(4, 0, 'Press S to start custom interval timelapse')
                window.addstr(5, 0, 'Press P to stop/pause the timelapse')
                window.addstr(6, 0, 'Use the up and down arrow keys to adjust timelapse interval')
                window.addstr(7, 0, 'Timelapse interval in secounds is: %i     ' % output.interval)
                window.addstr(10, 0, 'Frame %d.jpg' % output.file_num)
                window.refresh()
                c = window.getch()
                if c == ord('q'):
                    break
                elif c == ord('f'):
                    output.write_frame = True
                elif c == ord('3'):
                    if output.lapse == True:
                        window.addstr(9, 0, 'Timelapse already running')
                    else:
                        output.lapse = True
                        output.interval = 3
                        output.write_frame = True
                        window.addstr(9, 0, 'Timelapse started                ')
                elif c == ord('s'):
                    if output.lapse == True:
                        window.addstr(9, 0, 'Timelapse already running')
                    else:
                        output.lapse = True
                        output.write_frame = True
                        window.addstr(9, 0, 'Timelapse started                ')
                elif c == ord('p'):
                    output.lapse = False
                    window.addstr(9, 0, 'Timelapse paused                  ')
                elif c == curses.KEY_UP:
                    if output.lapse == False:
                        output.interval = output.interval + 1
                elif c == curses.KEY_DOWN:
                    if output.lapse == False:
                        if output.interval > 1:
                            output.interval = output.interval - 1
                camera.wait_recording(0.1)
        finally:
            camera.stop_recording()

curses.initscr()
curses.wrapper(main)
