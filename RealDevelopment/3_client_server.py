from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel

def simpleClientServerTopo():
    net = Mininet(switch=OVSSwitch)
    print("Creating nodes")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    s1 = net.addSwitch('s1', failMode='standalone')
    #c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.8', port=65432)

    print("Creating links")
    net.addLink(h1, s1)
    net.addLink(h2, s1)

    print("Starting network")
    net.start()

    print("Running CLI")
    CLI(net)

    print("Stopping the network")
    net.stop()

def main():
    setLogLevel('info')
    simpleClientServerTopo()

if __name__ == '__main__':
    main()