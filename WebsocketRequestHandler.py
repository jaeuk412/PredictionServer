from socketserver import BaseRequestHandler
from base64 import b64encode
from hashlib import sha1
import struct

#------------------------
class WebsocketRequestHandler( BaseRequestHandler ):
    # Override
    def setup( self ):
        self.socket = self.request
        self.is_valid = True
        self.is_handshake = False

    # Override

    def handle( self ):
        while self.is_valid:
            if not self.is_handshake:
                self.handshake()
            else:
                self.receive_message()
    # Override

    def finish( self ):
        self.server.out_client( self )

    def handshake( self ):
        header = self.socket.recv( 1024 ).decode().strip()
        request_key = ''

        for each in header.split( '\r\n' ):
            if each.find( ': ' ) == -1:
                continue
            ( k, v ) = each.split( ': ' )

            if k.strip().lower() == 'sec-websocket-key':
                request_key = v.strip()
                break

        if not request_key:
            self.is_valid = False
            print( 'Not valid handshake request_key' )
            return

        response_key = b64encode( sha1( request_key.encode() + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'.encode() ).digest() ).strip().decode()

        response = \
            'HTTP/1.1 101 Switching Protocols\r\n'\
            'Upgrade: websocket\r\n'\
            'Connection: Upgrade\r\n'\
            'Sec-WebSocket-Accept: %s\r\n'\
            '\r\n' % response_key

        self.is_handshake = self.socket.send( response.encode() )

        self.server.in_client( self )

        print( 'Handshake OK!' )

#------------------------- 클라이언트로 부터 메시지 받음.

    def receive_message( self ):

        byte1, byte2 = self.socket.recv( 2 )
        opcode = byte1 & 15
        is_mask = byte2 & 128
        payload_length = byte2 & 127

        if not byte1 or opcode == 8 or not is_mask:
            self.is_valid = False
            return

        if payload_length == 126:
            payload_length = struct.unpack( '>H', self.socket.recv( 2 ) )[ 0 ]
        elif payload_length == 127:
            payload_length = struct.unpack( '>Q', self.socket.recv( 4 ) )[ 0 ]

        masks = self.socket.recv( 4 )
        payload = self.socket.recv( payload_length )
        message = ''

        for byte in payload:
            byte ^= masks[ len( message ) % 4 ]
            message += chr( byte )


        self.server.receive_message( self, message )

#---------------------------- 클라이언트한태 메시지 보냄.

    def send_message( self, message ):

        header = bytearray()
        payload = message.encode( 'UTF-8' )
        payload_length = len( payload )

        header.append( 129 )

        if payload_length <= 125:
            header.append( payload_length )

        elif payload_length >= 126 and payload_length <= pow( 2, 16 ):
            header.append( 126 )
            header.extend( struct.pack( '>H', payload_length ) )
        elif payload_length <= pow( 2, 64 ):
            header.append( 127 )
            header.extend( struct.pack( '>Q', payload_length ) )
        else:
            print( 'Not valid send payload_length' )
            return

        self.socket.send( header + payload )


#----------------------------------

