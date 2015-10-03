import getopt
import sys
from traffic_light import app

CONF = {
    'host': '0.0.0.0',
    'port': 8080
}


def set_conf(argv):
    try:
        opts, args = getopt.getopt(argv, 'h:p:', ['host=', 'port='])
        for opt, arg in opts:

            if opt in ('-h', '--host'):
                CONF['host'] = arg
            elif opt in ('-p', '--port'):
                CONF['port'] = int(arg)

    except getopt.GetoptError:
        print 'Usage: traffic-light [-h|--host] [-p|--port]'
        print 'Example: traffic-light -p 8080 --host=0.0.0.0'
        sys.exit()


def main():
    set_conf(sys.argv[1:])
    app.run(host=CONF['host'], port=CONF['port'])
