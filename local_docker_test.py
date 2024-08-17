import docker
import json
import os
import time
import subprocess

# Path to your audio file for testing
AUDIO_FILE_PATH = '/Users/christianreetz/Downloads/Call-test-50sec.m4a'

# Name of your Docker image
IMAGE_NAME = 'stt-diarization-model:latest'

# Initialize Docker client
client = docker.from_env()

def run_command(command, stream_output=False):
    if stream_output:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        for line in process.stdout:
            print(line, end='')
        process.wait()
        if process.returncode != 0:
            print(f"Command failed with return code {process.returncode}")
            return None
        return "Command completed successfully"
    else:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        output, error = process.communicate()
        if process.returncode != 0:
            print(f"Error: {error.decode('utf-8')}")
            return None
        return output.decode('utf-8')

def build_image():
    print("Building Docker image...")
    try:
        image, build_logs = client.images.build(
            path='.',
            tag=IMAGE_NAME,
            rm=True,
            forcerm=True
        )
        for log in build_logs:
            if 'stream' in log:
                print(log['stream'].strip())
            print("Successfully build Docker image")
    except docker.errors.BuildError as e:
        print(f"Build failed: {e}")
        for log in e.build_logs:
            if 'stream' in log:
                print(log['stream'].strip())
        raise

    

def run_container():
    print("Running container...")
    container = client.containers.run(
        IMAGE_NAME,
        detach=True,
        remove=True,
        ports={'8080/tcp': 8080},
        volumes={os.path.dirname(AUDIO_FILE_PATH): {'bind': '/data', 'mode': 'ro'}},
        environment={
            'AUDIO_PATH': f'/data/{os.path.basename(AUDIO_FILE_PATH)}',
        }
    )
    return container

def test_inference(container):
    print("Testing inference...")
    # Wait for the container to be ready
    time.sleep(10)

    # Prepare the payload
    payload = {
        'audio_path': f'/data/{os.path.basename(AUDIO_FILE_PATH)}'
    }

    # Send a request to the container
    response = container.exec_run(
        cmd=['python', '-c', f"""
import json
import sys
sys.path.append('/opt/ml/code')
from inference import input_fn, predict_fn, output_fn, model_fn
model = model_fn('/opt/ml/model')
input_data = input_fn('{json.dumps(payload)}', 'application/json')
prediction = predict_fn(input_data, model)
output = output_fn(prediction, 'application/json')
print(output)
"""]
    )

    print("Response:")
    print(response.output.decode())

def main():
    build_image()
    container = run_container()
    try:
        test_inference(container)
    finally:
        print("Stopping container...")
        container.stop()

if __name__ == "__main__":
    main()
