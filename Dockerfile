# Stage 1: Build and download models
#FROM 763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-inference:1.8.1-gpu-py36-cu111-ubuntu18.04
FROM pytorch/pytorch:1.8.1-cuda11.1-cudnn8-runtime

# Install sys depend
RUN apt-get update && apt-get install -y ffmpeg

# Install necessary packages for building
RUN pip install --no-cache-dir transformers torch torchaudio pyannote.audio pydub

RUN python -c "from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor; \
    from pyannote.audio import Pipeline; \
    Wav2Vec2ForCTC.from_pretrained('facebook/wav2vec2-base-960h'); \
    Wav2Vec2Processor.from_pretrained('facebook/wav2vec2-base-960h'); \
    Pipeline.from_pretrained('pyannote/speaker-diarization')"

# Copy your inference code
COPY inference.py /opt/ml/code/inference.py

# Set the entrypoint
ENTRYPOINT ["python", "/opt/ml/code/inference.py"]
