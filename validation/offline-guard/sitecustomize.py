import sys,os,json,time

def audit(event,args):
    if event not in ('socket.connect','socket.getaddrinfo'):return
    address=args[1] if event=='socket.connect' else args[0]
    host=address[0] if isinstance(address,tuple) else address
    if host in ('127.0.0.1','localhost','::1','0.0.0.0',None):return
    path=os.environ.get('VALIDATION_NETWORK_LOG')
    if path:
        try:
            with open(path,'a',encoding='utf-8') as f:f.write(json.dumps({'event':event,'host':str(host),'time':time.time()})+'\n')
        except OSError:pass
    raise OSError('External network disabled during isolated project validation')
sys.addaudithook(audit)
