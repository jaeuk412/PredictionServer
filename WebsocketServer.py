from socketserver import ThreadingMixIn, TCPServer
import json



class WebsocketServer( ThreadingMixIn, TCPServer ):
    allow_reuse_address = True
    daemon_threads = True

    client_id = 0
    clients = []
    all_data = {}

    def __init__( self, host, port, handlerClass ):
        TCPServer.__init__( self, ( host, port ), handlerClass )

    def find_client( self, handler ):
        for client in self.clients:
            if client[ 'handler' ] == handler:
                return client

    def in_client( self, handler ):
        self.client_id += 1
        self.clients.append( { 'id' : str( self.client_id ), 'handler' : handler } )
        print( 'In client ' + str( self.client_id ) )

    def out_client( self, handler ):
        for client in self.clients:
            if client[ 'handler' ] == handler:
                self.clients.remove( client )
                del self.all_data[ client[ 'id' ] ]
                handler.send_message( json.dumps( { 'code' : 0, 'message' : 'success' } ) )
                print( 'Out client ' + client[ 'id' ] )
                break

    def receive_message( self, handler, message ):
        pass

from WebsocketRequestHandler import WebsocketRequestHandler


try:

    port = 8080
    wsd = WebsocketServer( '0.0.0.0', port, WebsocketRequestHandler )
    print( 'Starting simple_wsd on port ' + str( port ) )
    # aa = WebsocketRequestHandler()
    # aa.send_message("send message from server")
    wsd.serve_forever()

except KeyboardInterrupt:

    print( 'Shutting down simple_wsd' )

    wsd.socket.close()