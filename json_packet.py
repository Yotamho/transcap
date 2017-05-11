from dpkt.dpkt import Packet, UnpackError, NeedData
from dpkt.ethernet import Ethernet
from dpkt.ip import IP
from dpkt.tcp import TCP
from dpkt.udp import UDP
from dpkt.http import Request as HTTPRequest
from dpkt.http import Response as HTTPResponse


class JsonPacket:

    def __init__(self, packet: Packet, ts, packet_number):
        self.packet = packet
        self.dict = {'timestamp': ts, 'num': packet_number}

        eth = Ethernet(self.packet)
        self.dict['smac'] = str(eth.src)
        self.dict['dmac'] = str(eth.dst)

        if isinstance(eth.data, IP):
            ip = eth.data
            self.dict['sip'] = str(ip.src)
            self.dict['dip'] = str(ip.dst)
            self.dict['ttl'] = ip.ttl
            self.dict['ipid'] = ip.id
            self.dict['ipv'] = ip.v
            self.dict['prot'] = ip.p
            self.dict['dfrag'] = ip.df

            if isinstance(ip.data, TCP):
                tcp = ip.data
                self.dict['sport'] = tcp.sport
                self.dict['dport'] = tcp.dport
                self.dict['tcpwin'] = tcp.win

                self.dict['tcpopts'] = str(tcp.opts)
                # Parse options:
                # self.dict['tcpopts'] = [(opt[0], str(opt[1])) for opt in parse_opts(tcp.opts)]

                self.dict['tcpflags'] = tcp.flags
                self.dict['tcpackn'] = tcp.ack
                self.dict['tcpseq'] = tcp.seq
                self.dict['tcpoff'] = tcp.off

                if self.dict['dport'] == 80:
                    try:
                        http = HTTPRequest(tcp.data)
                        try:
                            self.dict['host'] = http.headers['host']
                        except (AttributeError, KeyError):
                            pass
                        try:
                            self.dict['user-agent'] = http.headers['user-agent']
                        except (AttributeError, KeyError):
                            pass
                        try:
                            self.dict['cookie'] = http.headers['cookie']
                        except (AttributeError, KeyError):
                            pass
                        try:
                            self.dict['uri'] = http.uri
                        except (AttributeError):
                            pass
                    except (UnpackError, NeedData):
                        pass
                elif self.dict['sport'] == 80:
                    try:
                        http = HTTPResponse(tcp.data)
                        try:
                            self.dict['setcookie'] = http.headers['set-cookie']
                        except (AttributeError, KeyError):
                            pass
                    except (UnpackError, NeedData):
                        pass

            elif isinstance(ip.data, UDP):
                udp = ip.data
                self.dict['sport'] = udp.sport
                self.dict['dport'] = udp.dport

    def __dict__(self):
        return self.dict
