from sortrobot.mech import Robot
import sys
sr = Robot()

cmds = {
    'FD': sr.fd,
    'BK': sr.bk,
    'LF': sr.lf,
    'RT': sr.rt,
}

cmd = sys.argv[-2]
val = float(sys.argv[-1])
cmds[cmd.upper()](val)
