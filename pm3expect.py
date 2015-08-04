from flask import Flask, request, redirect, make_response
import pexpect
import os.path
import sys
from functools import wraps, update_wrapper
import datetime
import json

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
        
    return update_wrapper(no_cache, view)

app = Flask(__name__, static_url_path='/static')
pm3 = {}
pm3cli = './proxmark3'
pm3usb = '/dev/ttyACM0'

def pm3_pexpect():
    global pm3
    if isinstance(pm3, pexpect.spawn):
        return
    if os.path.exists(pm3cli) and os.path.exists(pm3usb):
        pm3 = pexpect.spawn(pm3cli + ' ' + pm3usb)
        try:
            pm3.expect('proxmark3> ', 5)
        except pexpect.TIMEOUT:
            sys.exit('Timeout waiting for proxmark3 client application response')
        if 'ERROR' in pm3.before:
            sys.exit(pm3.before.strip())
    else:
        sys.exit('Either proxmark client or device do not exist')
    return
            
def pm3_cmd(cmd):
    global pm3
    pm3_pexpect()
    cmdlen = pm3.sendline(cmd)
    pm3.expect('proxmark3> ')
    return pm3.before[cmdlen + 1:]

@app.route("/")
def root():
    return app.send_static_file('tnp3test13.html')

@app.route("/hw-version")
def pm3_hw_version():
    return pm3_cmd('hw version')

@app.route("/json-hf-reader")
def pm3_script_run_jsonhfone():
    output = pm3_cmd('script run jsonhfone')
    return output[output.find('{'):output.rfind('}')+1]
    
@app.route("/json-tnp3-reader")
def pm3_script_run_jsonhftwo():
    output = pm3_cmd('script run jsonhftwo')
    return output[output.find('{'):output.rfind('}')+1]
    
@app.route("/json-tnp3-block00")
def pm3_script_run_jsonhfthree():
    keyA = request.args.get('keya', '')
    if not keyA:
        return '{"error": "No key A specified"}'
    output = pm3_cmd('script run jsonhfthree -k ' + keyA)
    if '#db#' in output and '"error":' in output:
        return '{"error": "' + [x.lstrip('#db# ') for x in output.split('\n') if x.startswith('#db#')][0].strip() + '"}'
    return output[output.find('{'):output.rfind('}')+1]
    
@app.route("/json-tnp3-blocksstartingat0")
def pm3_script_run_jsonhffour():
    keysA = request.args.get('keysa', '')
    if not keysA:
        return '{"error": "No keys A specified"}'
    numblocks = request.args.get('blocks', '')
    if not numblocks:
        return '{"error": "No number of blocks specified"}'
    output = pm3_cmd('script run jsonhffour -k ' + keysA + ' -b ' + numblocks)
    blocks = json.loads(output[output.find('{'):output.rfind('}')+1])
    dbs = [x.lstrip('#db# ').rstrip() for x in output.split('\n') if x.startswith('#db# ')]
    
    for index, block in enumerate(blocks['blocks']):
        if '#db#' in block:
            realdb = 0
            for db in dbs:
                if index == realdb:
                    blocks['blocks'][index] = {'error': db}
                    break
                if 'READ BLOCK FINISHED' in db:
                    realdb = realdb + 1
    
    return json.dumps(blocks)
    
@app.route("/json-tnp3-block")
def pm3_script_run_jsonhffive():
    keyA = request.args.get('keya', '')
    if not keyA:
        return '{"error": "No key A specified"}'
    numblock = request.args.get('block', '')
    if not numblock:
        return '{"error": "No block number specified"}'
    output = pm3_cmd('script run jsonhffive -k ' + keyA + ' -b ' + numblock)
    blockdata = json.loads(output[output.find('['):output.rfind(']')+1])
    dbs = [x.lstrip('#db# ').rstrip() for x in output.split('\n') if x.startswith('#db# ')]
    
    if '#db#' in blockdata:
        if len(dbs) > 0:
            block = {'error': dbs[0]}
        else:
            block = {'error': 'pm3 returned nothing'}
    else:
        block = {'data': blockdata[0]}
    
    return json.dumps(block)
    
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)