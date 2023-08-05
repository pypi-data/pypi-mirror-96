from portdatasplitter.main import PortDataSplitter


server = PortDataSplitter('0.0.0.0', 2290, port_name='/dev/ttyUSB0')
ports = server.get_all_connected_devices()

server = PortDataSplitter('0.0.0.0', 2290, port_name='COM1', debug=True)
server.start()