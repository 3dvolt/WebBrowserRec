from flask import Flask, render_template, Response
import cv2
import framework
import pyaudio
import audio_processing as audioRec

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

audio = pyaudio.PyAudio()


app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


# Stream routing
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(generateVideo(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/audio_feed")
def audio_feed():
    """Audio streaming route. Put this in the src attribute of an audio tag."""
    return Response(generateAudio(),
                    mimetype="audio/x-wav")


# Stream generating
def generateVideo():
    """Video streaming generator function."""
    cap = cv2.VideoCapture(0)
    while (cap.isOpened()):
        ret, frame = cap.read()
        output = framework.streamer(frame, 'final')
        cv2.imwrite('signals/currFrame.jpg', output)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('signals/currFrame.jpg', 'rb').read() + b'\r\n')


def generateAudio():
    """Audio streaming generator function."""
    currChunk = audioRec.record()
    data_to_stream = genHeader(44100, 32, 1, 200000) + currChunk
    yield data_to_stream

    # with open("signals/audio.wav", "rb") as fwav:
    #     data = fwav.read(1024)
    #     while data:
    #         yield data
    #         data = fwav.read(1024)


def genHeader(sampleRate, bitsPerSample, channels, samples):
    datasize = samples * channels * bitsPerSample // 8
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
