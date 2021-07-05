from flask import Flask, request, jsonify

app=Flask(__name__)

# {
#   "command": "start",
#   "mode": "black" | "normal" | "anime"
# }

# {
#   "command": "stop"
# }

@app.route('/control', methods=['POST'])
def control():
    data = request.get_json(force = True)
    print('control/ called')
    print('data: ' + str(data))

    if data and 'command' in data:
        if data['command'] == 'start':
            if 'mode' in data:
                if data['mode'] == 'black':
                    print('Set eyes to black')
                elif data['mode'] == 'normal':
                    print('Set eyes to normal')
                elif data['mode'] == 'anime':
                    print('Set eyes to kawai')
            else:
                print('No mode was specified fallback to default')
            print('Eyes are turned on')
        elif data['command'] == 'stop':
            print('Everithing is black now')
        else:
            print('Invalid command is provided')
            return "error: invalid command"
            
    return "ok"

if __name__ == '__main__':
    print("Eye server started")
    app.run(host='0.0.0.0', port=5005, debug=True)