#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

# add import makeTerm
from mininet.term import makeTerm

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/24')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')
    
    # Moved switches to the top of this block and placed in the correct order
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    # Corrected IP addresses and placed in the correct order
    r3 = net.addHost('r3', cls=Node, ip='10.0.1.1/24')
    r3.cmd('sysctl -w net.ipv4.ip_forward=1')

    r4 = net.addHost('r4', cls=Node, ip='192.168.1.1/30')
    r4.cmd('sysctl -w net.ipv4.ip_forward=1')

    r5 = net.addHost('r5', cls=Node, ip='10.0.2.1/24')
    r5.cmd('sysctl -w net.ipv4.ip_forward=1')
    
    info( '*** Add hosts\n')
    
    # Added subnet masks to host IP addresses and corrected default routes
    h1 = net.addHost('h1', cls=Host, ip='10.0.1.2/24', defaultRoute='via 10.0.1.1')
    h2 = net.addHost('h2', cls=Host, ip='10.0.1.3/24', defaultRoute='via 10.0.1.1')
    h3 = net.addHost('h3', cls=Host, ip='10.0.2.2/24', defaultRoute='via 10.0.2.1')
    h4 = net.addHost('h4', cls=Host, ip='10.0.2.3/24', defaultRoute='via 10.0.2.1')

    # Links
    
    net.addLink(s1, r3) # r3-eth0
    
    # Added interface names to connections between r3 and r4 - needed for static links
    net.addLink(r3, r4, intfName1='r3-eth1', params1={'ip': '192.168.1.2/30'}, intfName2='r4-eth0', params2={'ip': '192.168.1.1/30'})

    # Links from hosts to switches
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s2)
    net.addLink(h4, s2)

    net.addLink(s2, r5) # r5-eth0
    
    # Added interface names to connections between r4 and r5 - needed for static links
    net.addLink(r4, r5, intfName2='r4-eth1', params1={'ip': '192.168.2.1/30'}, intfName1='r5-eth1', params2={'ip': '192.168.2.2/30'})

    # Added static links so r3 can reach r5 through r4 and vice versa
    net['r3'].cmd('ip route add 10.0.2.0/24 via 192.168.1.1 dev r3-eth1')
    net['r5'].cmd('ip route add 10.0.1.0/24 via 192.168.2.1 dev r4-eth1')

    net['r4'].cmd('ip route add 10.0.1.0/24 via 192.168.1.2 dev r4-eth0')
    net['r4'].cmd('ip route add 10.0.2.0/24 via 192.168.2.2 dev r5-eth1')

    net['r3'].cmd('ip route add 192.168.2.0/30 via 192.168.1.1 dev r3-eth1')
    net['r5'].cmd('ip route add 192.168.1.0/30 via 192.168.2.1 dev r4-eth1')

    info( '*** Starting network\n')
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])

    info( '*** Post configure switches and hosts\n')

    net.build()
    
    
    
    # Create directories like we did in lab 6
    
    makeTerm(node=h2, cmd='sudo mkdir /etc/ssl/demoCA/newcerts')
    makeTerm(node=h2, cmd='sudo mkdir /etc/ssl/demoCA/private')
    
    # Create server private key
    makeTerm(node=h2, cmd='sudo openssl genrsa -out chatserver-key.pem 2048')
    
    # Create server certificate signing request
    makeTerm(node=h2, cmd='sudo openssl req -nodes -new -config /etc/ssl/openssl.cnf -key chatserver-key.pem -out chatserver.csr -subj "/C=US/ST=CA/L=Seaside/O=CST311/OU=Networking/CN=chatserver-cert"')

    makeTerm(node=h2, cmd='sudo openssl x509 -req -days 365 -in chatserver.csr -CA chatserver.pem -CAkey ./private/chatserver.pem -CAcreateserial -out chatserver-cert.pem')

    
    makeTerm(node=h2, cmd='sudo openssl x509 -req -days 365 -in chatserver.csr -CA chatserver.pem -CAkey ./private/chatserver.pem -CAcreateserial -out chatserver-cert.pem -extfile $HOME/CST311/extClient.cnf')
    makeTerm(node=h2, cmd ='sudo mv chatserver-cert.pem newcerts')
    makeTerm(node=h2, cmd='sudo mv chatserver-key.pem private')
    makeTerm(node=h2, cmd='sudo su')
    makeTerm(node=h2, cmd='chmod -R 600 private')

    # Run server.py in xterm
    makeTerm(node=h2, title='h2', term='xterm', display=None, cmd='sudo python server.py')


    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
